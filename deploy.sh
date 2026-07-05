#!/usr/bin/env bash
#
# deploy.sh — Journal API two-tier deployment on Azure (idempotent).
#
# Provisions a two-tier architecture in a single virtual network:
#
#   Public tier  (public subnet):  API VM with a public IP. nginx terminates
#                                   TLS on 443 and reverse-proxies to the
#                                   FastAPI app on localhost:8000.
#   Private tier (private subnet):  PostgreSQL VM with NO public IP. Reachable
#                                   only from the public subnet on port 5432.
#
# Traffic flow:  Internet --443/TLS--> API VM --> app --5432(private only)--> DB VM
#
# The database is never publicly reachable: it has no public IP and its network
# security group only admits PostgreSQL traffic from the API (public) subnet.
#
# This script is safe to re-run: every resource is created only if it does not
# already exist (create-or-skip), so re-running converges to the same state.
#
# Configuration (override via environment variables):
#   RESOURCE_GROUP    Resource group name        (default: journal-rg)
#   LOCATION          Azure region               (default: centralus)
#   PREFIX            Name prefix for resources   (default: journal)
#   ADMIN_SOURCE_IP   CIDR allowed to SSH (22)    (default: none -> SSH denied)
#   VM_SIZE           VM size                     (default: Standard_B1s)
#   VM_IMAGE          VM image                    (default: Ubuntu2204)
#   ADMIN_USERNAME    VM admin username           (default: azureuser)
#
# Requires: azure-cli (az), logged in via `az login`.

set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
RESOURCE_GROUP="${RESOURCE_GROUP:-journal-rg}"
LOCATION="${LOCATION:-centralus}"
PREFIX="${PREFIX:-journal}"
ADMIN_SOURCE_IP="${ADMIN_SOURCE_IP:-}"
VM_SIZE="${VM_SIZE:-Standard_B1s}"
VM_IMAGE="${VM_IMAGE:-Ubuntu2204}"
ADMIN_USERNAME="${ADMIN_USERNAME:-azureuser}"

# Network layout
VNET_NAME="${PREFIX}-vnet"
VNET_CIDR="10.0.0.0/16"
PUBLIC_SUBNET_NAME="public-subnet"
PUBLIC_SUBNET_CIDR="10.0.1.0/24"
PRIVATE_SUBNET_NAME="private-subnet"
PRIVATE_SUBNET_CIDR="10.0.2.0/24"

# NSGs
API_NSG_NAME="${PREFIX}-api-nsg"
DB_NSG_NAME="${PREFIX}-db-nsg"

# Compute
API_VM_NAME="${PREFIX}-api-vm"
DB_VM_NAME="${PREFIX}-db-vm"
API_PUBLIC_IP_NAME="${PREFIX}-api-pip"
API_NIC_NAME="${PREFIX}-api-nic"
DB_NIC_NAME="${PREFIX}-db-nic"

AZ="az"
AZ_QUIET=(--only-show-errors --output none)

log() { printf '\n\033[1;34m==>\033[0m %s\n' "$1"; }
info() { printf '    %s\n' "$1"; }

# ---------------------------------------------------------------------------
# Preflight
# ---------------------------------------------------------------------------
if ! command -v az >/dev/null 2>&1; then
  echo "ERROR: azure-cli (az) is not installed. See https://aka.ms/azure-cli" >&2
  exit 1
fi

if ! $AZ account show --only-show-errors >/dev/null 2>&1; then
  echo "ERROR: not logged in to Azure. Run 'az login' first." >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# Cloud-init: private-tier PostgreSQL VM
# ---------------------------------------------------------------------------
DB_CLOUD_INIT="$(mktemp)"
cat >"$DB_CLOUD_INIT" <<EOF
#cloud-config
package_update: true
packages:
  - postgresql
  - postgresql-contrib
runcmd:
  # Listen on the private interface so the API tier can reach PostgreSQL,
  # while the NSG restricts access to the public subnet only.
  - sed -i "s/^#\\?listen_addresses.*/listen_addresses = '*'/" /etc/postgresql/*/main/postgresql.conf
  - echo "host all all ${PUBLIC_SUBNET_CIDR} scram-sha-256" >> /etc/postgresql/*/main/pg_hba.conf
  - systemctl enable postgresql
  - systemctl restart postgresql
  - sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'changeme-in-prod';"
  - sudo -u postgres createdb journal || true
EOF

# ---------------------------------------------------------------------------
# Cloud-init: public-tier API VM (nginx TLS termination -> app on :8000)
# ---------------------------------------------------------------------------
API_CLOUD_INIT="$(mktemp)"
cat >"$API_CLOUD_INIT" <<EOF
#cloud-config
package_update: true
packages:
  - nginx
  - openssl
write_files:
  - path: /etc/nginx/sites-available/journal-api
    content: |
      server {
          listen 80;
          server_name _;
          # Redirect all plain HTTP to HTTPS.
          return 301 https://\$host\$request_uri;
      }
      server {
          listen 443 ssl;
          server_name _;
          # TLS termination for the API.
          ssl_certificate     /etc/nginx/tls/journal.crt;
          ssl_certificate_key /etc/nginx/tls/journal.key;
          ssl_protocols TLSv1.2 TLSv1.3;
          location / {
              # Reverse proxy to the FastAPI app running on the same VM.
              proxy_pass http://127.0.0.1:8000;
              proxy_set_header Host \$host;
              proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
              proxy_set_header X-Forwarded-Proto \$scheme;
          }
      }
runcmd:
  - mkdir -p /etc/nginx/tls
  - openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/nginx/tls/journal.key -out /etc/nginx/tls/journal.crt -subj "/CN=journal-api"
  - ln -sf /etc/nginx/sites-available/journal-api /etc/nginx/sites-enabled/journal-api
  - rm -f /etc/nginx/sites-enabled/default
  - systemctl enable nginx
  - systemctl restart nginx
EOF

cleanup() { rm -f "$DB_CLOUD_INIT" "$API_CLOUD_INIT"; }
trap cleanup EXIT

# ---------------------------------------------------------------------------
# Idempotency helpers
# ---------------------------------------------------------------------------
group_exists() { $AZ group exists --name "$RESOURCE_GROUP" --only-show-errors | grep -q true; }

exists() {
  # exists <az-show-subcommand...> -> 0 if the resource exists.
  "$@" --only-show-errors >/dev/null 2>&1
}

# ---------------------------------------------------------------------------
# 1. Resource group
# ---------------------------------------------------------------------------
log "Resource group: $RESOURCE_GROUP ($LOCATION)"
if group_exists; then
  info "already exists, skipping"
else
  $AZ group create --name "$RESOURCE_GROUP" --location "$LOCATION" "${AZ_QUIET[@]}"
  info "created"
fi

# ---------------------------------------------------------------------------
# 2. Network security groups
# ---------------------------------------------------------------------------
log "Network security group (public/API tier): $API_NSG_NAME"
if exists $AZ network nsg show -g "$RESOURCE_GROUP" -n "$API_NSG_NAME"; then
  info "already exists, skipping"
else
  $AZ network nsg create -g "$RESOURCE_GROUP" -n "$API_NSG_NAME" "${AZ_QUIET[@]}"
  info "created"
fi

# Allow HTTPS (443) from the Internet -> TLS-terminated API ingress.
if ! exists $AZ network nsg rule show -g "$RESOURCE_GROUP" --nsg-name "$API_NSG_NAME" -n allow-https; then
  $AZ network nsg rule create -g "$RESOURCE_GROUP" --nsg-name "$API_NSG_NAME" -n allow-https \
    --priority 100 --direction Inbound --access Allow --protocol Tcp \
    --source-address-prefixes Internet --destination-port-ranges 443 "${AZ_QUIET[@]}"
  info "rule allow-https created"
fi

# Allow HTTP (80) from the Internet -> redirected to HTTPS by nginx.
if ! exists $AZ network nsg rule show -g "$RESOURCE_GROUP" --nsg-name "$API_NSG_NAME" -n allow-http; then
  $AZ network nsg rule create -g "$RESOURCE_GROUP" --nsg-name "$API_NSG_NAME" -n allow-http \
    --priority 110 --direction Inbound --access Allow --protocol Tcp \
    --source-address-prefixes Internet --destination-port-ranges 80 "${AZ_QUIET[@]}"
  info "rule allow-http created"
fi

# SSH (22) restricted to an explicit admin CIDR; denied entirely if unset.
if [ -n "$ADMIN_SOURCE_IP" ]; then
  if ! exists $AZ network nsg rule show -g "$RESOURCE_GROUP" --nsg-name "$API_NSG_NAME" -n allow-ssh-admin; then
    $AZ network nsg rule create -g "$RESOURCE_GROUP" --nsg-name "$API_NSG_NAME" -n allow-ssh-admin \
      --priority 120 --direction Inbound --access Allow --protocol Tcp \
      --source-address-prefixes "$ADMIN_SOURCE_IP" --destination-port-ranges 22 "${AZ_QUIET[@]}"
    info "rule allow-ssh-admin created ($ADMIN_SOURCE_IP)"
  fi
else
  info "ADMIN_SOURCE_IP unset -> SSH left denied by default deny rule"
fi

log "Network security group (private/database tier): $DB_NSG_NAME"
if exists $AZ network nsg show -g "$RESOURCE_GROUP" -n "$DB_NSG_NAME"; then
  info "already exists, skipping"
else
  $AZ network nsg create -g "$RESOURCE_GROUP" -n "$DB_NSG_NAME" "${AZ_QUIET[@]}"
  info "created"
fi

# PostgreSQL (5432) allowed ONLY from the public/API subnet.
if ! exists $AZ network nsg rule show -g "$RESOURCE_GROUP" --nsg-name "$DB_NSG_NAME" -n allow-postgres-from-api; then
  $AZ network nsg rule create -g "$RESOURCE_GROUP" --nsg-name "$DB_NSG_NAME" -n allow-postgres-from-api \
    --priority 100 --direction Inbound --access Allow --protocol Tcp \
    --source-address-prefixes "$PUBLIC_SUBNET_CIDR" --destination-port-ranges 5432 "${AZ_QUIET[@]}"
  info "rule allow-postgres-from-api created"
fi

# Explicitly deny any inbound traffic from the Internet to the database tier.
if ! exists $AZ network nsg rule show -g "$RESOURCE_GROUP" --nsg-name "$DB_NSG_NAME" -n deny-internet-inbound; then
  $AZ network nsg rule create -g "$RESOURCE_GROUP" --nsg-name "$DB_NSG_NAME" -n deny-internet-inbound \
    --priority 4000 --direction Inbound --access Deny --protocol '*' \
    --source-address-prefixes Internet --destination-port-ranges '*' "${AZ_QUIET[@]}"
  info "rule deny-internet-inbound created"
fi

# ---------------------------------------------------------------------------
# 3. Virtual network + subnets (each bound to its tier's NSG)
# ---------------------------------------------------------------------------
log "Virtual network: $VNET_NAME ($VNET_CIDR)"
if exists $AZ network vnet show -g "$RESOURCE_GROUP" -n "$VNET_NAME"; then
  info "already exists, skipping"
else
  $AZ network vnet create -g "$RESOURCE_GROUP" -n "$VNET_NAME" \
    --address-prefixes "$VNET_CIDR" \
    --subnet-name "$PUBLIC_SUBNET_NAME" --subnet-prefixes "$PUBLIC_SUBNET_CIDR" \
    "${AZ_QUIET[@]}"
  info "created with public subnet"
fi

# Public subnet -> API NSG
if ! exists $AZ network vnet subnet show -g "$RESOURCE_GROUP" --vnet-name "$VNET_NAME" -n "$PUBLIC_SUBNET_NAME"; then
  $AZ network vnet subnet create -g "$RESOURCE_GROUP" --vnet-name "$VNET_NAME" \
    -n "$PUBLIC_SUBNET_NAME" --address-prefixes "$PUBLIC_SUBNET_CIDR" "${AZ_QUIET[@]}"
fi
$AZ network vnet subnet update -g "$RESOURCE_GROUP" --vnet-name "$VNET_NAME" \
  -n "$PUBLIC_SUBNET_NAME" --network-security-group "$API_NSG_NAME" "${AZ_QUIET[@]}"
info "public subnet associated with $API_NSG_NAME"

# Private subnet -> DB NSG
if ! exists $AZ network vnet subnet show -g "$RESOURCE_GROUP" --vnet-name "$VNET_NAME" -n "$PRIVATE_SUBNET_NAME"; then
  $AZ network vnet subnet create -g "$RESOURCE_GROUP" --vnet-name "$VNET_NAME" \
    -n "$PRIVATE_SUBNET_NAME" --address-prefixes "$PRIVATE_SUBNET_CIDR" "${AZ_QUIET[@]}"
fi
$AZ network vnet subnet update -g "$RESOURCE_GROUP" --vnet-name "$VNET_NAME" \
  -n "$PRIVATE_SUBNET_NAME" --network-security-group "$DB_NSG_NAME" "${AZ_QUIET[@]}"
info "private subnet associated with $DB_NSG_NAME"

# ---------------------------------------------------------------------------
# 4. Public-tier API VM (public IP + NIC in public subnet)
# ---------------------------------------------------------------------------
log "Public IP for API VM: $API_PUBLIC_IP_NAME"
if exists $AZ network public-ip show -g "$RESOURCE_GROUP" -n "$API_PUBLIC_IP_NAME"; then
  info "already exists, skipping"
else
  $AZ network public-ip create -g "$RESOURCE_GROUP" -n "$API_PUBLIC_IP_NAME" \
    --sku Standard --allocation-method Static "${AZ_QUIET[@]}"
  info "created"
fi

log "NIC for API VM: $API_NIC_NAME (public subnet, with public IP)"
if exists $AZ network nic show -g "$RESOURCE_GROUP" -n "$API_NIC_NAME"; then
  info "already exists, skipping"
else
  $AZ network nic create -g "$RESOURCE_GROUP" -n "$API_NIC_NAME" \
    --vnet-name "$VNET_NAME" --subnet "$PUBLIC_SUBNET_NAME" \
    --public-ip-address "$API_PUBLIC_IP_NAME" "${AZ_QUIET[@]}"
  info "created"
fi

log "API VM: $API_VM_NAME (public tier)"
if exists $AZ vm show -g "$RESOURCE_GROUP" -n "$API_VM_NAME"; then
  info "already exists, skipping"
else
  $AZ vm create -g "$RESOURCE_GROUP" -n "$API_VM_NAME" \
    --image "$VM_IMAGE" --size "$VM_SIZE" \
    --admin-username "$ADMIN_USERNAME" --generate-ssh-keys \
    --nics "$API_NIC_NAME" \
    --custom-data "$API_CLOUD_INIT" "${AZ_QUIET[@]}"
  info "created (nginx TLS termination via cloud-init)"
fi

# ---------------------------------------------------------------------------
# 5. Private-tier database VM (NIC in private subnet, NO public IP)
# ---------------------------------------------------------------------------
log "NIC for database VM: $DB_NIC_NAME (private subnet, no public IP)"
if exists $AZ network nic show -g "$RESOURCE_GROUP" -n "$DB_NIC_NAME"; then
  info "already exists, skipping"
else
  $AZ network nic create -g "$RESOURCE_GROUP" -n "$DB_NIC_NAME" \
    --vnet-name "$VNET_NAME" --subnet "$PRIVATE_SUBNET_NAME" "${AZ_QUIET[@]}"
  info "created (no public IP)"
fi

log "Database VM: $DB_VM_NAME (private tier)"
if exists $AZ vm show -g "$RESOURCE_GROUP" -n "$DB_VM_NAME"; then
  info "already exists, skipping"
else
  $AZ vm create -g "$RESOURCE_GROUP" -n "$DB_VM_NAME" \
    --image "$VM_IMAGE" --size "$VM_SIZE" \
    --admin-username "$ADMIN_USERNAME" --generate-ssh-keys \
    --nics "$DB_NIC_NAME" \
    --custom-data "$DB_CLOUD_INIT" "${AZ_QUIET[@]}"
  info "created (PostgreSQL via cloud-init, private only)"
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
API_IP="$($AZ network public-ip show -g "$RESOURCE_GROUP" -n "$API_PUBLIC_IP_NAME" \
  --query ipAddress -o tsv --only-show-errors 2>/dev/null || echo 'pending')"
DB_PRIVATE_IP="$($AZ network nic show -g "$RESOURCE_GROUP" -n "$DB_NIC_NAME" \
  --query 'ipConfigurations[0].privateIPAddress' -o tsv --only-show-errors 2>/dev/null || echo 'pending')"

log "Deployment complete"
cat <<EOF

  Two-tier architecture provisioned in resource group '$RESOURCE_GROUP':

    Public tier (public subnet $PUBLIC_SUBNET_CIDR):
      API VM        : $API_VM_NAME
      Public IP     : $API_IP
      Ingress       : https://$API_IP  (nginx TLS termination on 443 -> app :8000)

    Private tier (private subnet $PRIVATE_SUBNET_CIDR):
      Database VM   : $DB_VM_NAME   (no public IP)
      Private IP    : $DB_PRIVATE_IP
      PostgreSQL    : reachable only from $PUBLIC_SUBNET_CIDR on 5432

  Traffic flow: Internet --443/TLS--> API VM --> app --5432(private)--> Database VM

  Re-run this script any time; it converges idempotently.
EOF
