#!/usr/bin/env bash

# High-level AWS deployment for the Career Journal two-tier architecture.
# The script focuses on the main resources and documents instance configuration
# without reproducing every manual command used during the original build.

# Prerequisites:
#   - AWS CLI configured and authenticated
#   - Existing EC2 key pair

# Before running:
#   export AWS_REGION="us-east-1"
#   export KEY_NAME="your-existing-key-pair"
#   export MY_IP_CIDR="your-public-ip/32"
#   export REPOSITORY_URL="https://github.com/your-user/journal-starter.git"

# Then run:
#   chmod +x deploy.sh
#   ./deploy.sh

set -Eeuo pipefail

AWS_REGION="${AWS_REGION:-us-east-1}"
PROJECT="${PROJECT:-career-journal}"
AZ="${AZ:-${AWS_REGION}a}"

VPC_CIDR="${VPC_CIDR:-10.0.0.0/16}"
PUBLIC_CIDR="${PUBLIC_CIDR:-10.0.1.0/24}"
PRIVATE_CIDR="${PRIVATE_CIDR:-10.0.2.0/24}"

INSTANCE_TYPE="${INSTANCE_TYPE:-t3.micro}"
KEY_NAME="${KEY_NAME:?Set KEY_NAME}"
MY_IP_CIDR="${MY_IP_CIDR:?Set MY_IP_CIDR, such as 203.0.113.10/32}"
REPOSITORY_URL="${REPOSITORY_URL:?Set REPOSITORY_URL}"

export AWS_DEFAULT_REGION="$AWS_REGION"

log() { printf '\n==> %s\n' "$*"; }

# Return the first matching resource ID, or "None".
lookup() {
    aws "$@" --output text
}

# ---------------------------------------------------------------------------
# 1. Network
# ---------------------------------------------------------------------------

log "Creating or reusing the VPC"

VPC_ID="$(lookup ec2 describe-vpcs \
    --filters "Name=tag:Name,Values=${PROJECT}-vpc" \
    --query 'Vpcs[0].VpcId')"

if [[ "$VPC_ID" == "None" ]]; then
    VPC_ID="$(lookup ec2 create-vpc \
        --cidr-block "$VPC_CIDR" \
        --tag-specifications \
        "ResourceType=vpc,Tags=[{Key=Name,Value=${PROJECT}-vpc}]" \
        --query 'Vpc.VpcId')"

    aws ec2 modify-vpc-attribute \
        --vpc-id "$VPC_ID" \
        --enable-dns-hostnames '{"Value":true}'
fi

PUBLIC_SUBNET_ID="$(lookup ec2 describe-subnets \
    --filters "Name=tag:Name,Values=${PROJECT}-public-subnet" \
    --query 'Subnets[0].SubnetId')"

if [[ "$PUBLIC_SUBNET_ID" == "None" ]]; then
    PUBLIC_SUBNET_ID="$(lookup ec2 create-subnet \
        --vpc-id "$VPC_ID" \
        --availability-zone "$AZ" \
        --cidr-block "$PUBLIC_CIDR" \
        --tag-specifications \
        "ResourceType=subnet,Tags=[{Key=Name,Value=${PROJECT}-public-subnet},{Key=Tier,Value=public}]" \
        --query 'Subnet.SubnetId')"

    aws ec2 modify-subnet-attribute \
        --subnet-id "$PUBLIC_SUBNET_ID" \
        --map-public-ip-on-launch
fi

PRIVATE_SUBNET_ID="$(lookup ec2 describe-subnets \
    --filters "Name=tag:Name,Values=${PROJECT}-private-subnet" \
    --query 'Subnets[0].SubnetId')"

if [[ "$PRIVATE_SUBNET_ID" == "None" ]]; then
    PRIVATE_SUBNET_ID="$(lookup ec2 create-subnet \
        --vpc-id "$VPC_ID" \
        --availability-zone "$AZ" \
        --cidr-block "$PRIVATE_CIDR" \
        --tag-specifications \
        "ResourceType=subnet,Tags=[{Key=Name,Value=${PROJECT}-private-subnet},{Key=Tier,Value=private}]" \
        --query 'Subnet.SubnetId')"
fi

IGW_ID="$(lookup ec2 describe-internet-gateways \
    --filters "Name=tag:Name,Values=${PROJECT}-igw" \
    --query 'InternetGateways[0].InternetGatewayId')"

if [[ "$IGW_ID" == "None" ]]; then
    IGW_ID="$(lookup ec2 create-internet-gateway \
        --tag-specifications \
        "ResourceType=internet-gateway,Tags=[{Key=Name,Value=${PROJECT}-igw}]" \
        --query 'InternetGateway.InternetGatewayId')"

    aws ec2 attach-internet-gateway \
        --internet-gateway-id "$IGW_ID" \
        --vpc-id "$VPC_ID"
fi

PUBLIC_RT_ID="$(lookup ec2 describe-route-tables \
    --filters "Name=tag:Name,Values=${PROJECT}-public-rt" \
    --query 'RouteTables[0].RouteTableId')"

if [[ "$PUBLIC_RT_ID" == "None" ]]; then
    PUBLIC_RT_ID="$(lookup ec2 create-route-table \
        --vpc-id "$VPC_ID" \
        --tag-specifications \
        "ResourceType=route-table,Tags=[{Key=Name,Value=${PROJECT}-public-rt}]" \
        --query 'RouteTable.RouteTableId')"

    aws ec2 create-route \
        --route-table-id "$PUBLIC_RT_ID" \
        --destination-cidr-block 0.0.0.0/0 \
        --gateway-id "$IGW_ID"

    aws ec2 associate-route-table \
        --route-table-id "$PUBLIC_RT_ID" \
        --subnet-id "$PUBLIC_SUBNET_ID"
fi

# NAT provides outbound internet access to the private database VM for package
# installation and updates. It does not make the database publicly reachable.
EIP_ID="$(lookup ec2 describe-addresses \
    --filters "Name=tag:Name,Values=${PROJECT}-nat-eip" \
    --query 'Addresses[0].AllocationId')"

if [[ "$EIP_ID" == "None" ]]; then
    EIP_ID="$(lookup ec2 allocate-address \
        --domain vpc \
        --tag-specifications \
        "ResourceType=elastic-ip,Tags=[{Key=Name,Value=${PROJECT}-nat-eip}]" \
        --query 'AllocationId')"
fi

NAT_ID="$(lookup ec2 describe-nat-gateways \
    --filter "Name=tag:Name,Values=${PROJECT}-nat" \
             "Name=state,Values=pending,available" \
    --query 'NatGateways[0].NatGatewayId')"

if [[ "$NAT_ID" == "None" ]]; then
    NAT_ID="$(lookup ec2 create-nat-gateway \
        --subnet-id "$PUBLIC_SUBNET_ID" \
        --allocation-id "$EIP_ID" \
        --tag-specifications \
        "ResourceType=natgateway,Tags=[{Key=Name,Value=${PROJECT}-nat}]" \
        --query 'NatGateway.NatGatewayId')"
fi

aws ec2 wait nat-gateway-available --nat-gateway-ids "$NAT_ID"

PRIVATE_RT_ID="$(lookup ec2 describe-route-tables \
    --filters "Name=tag:Name,Values=${PROJECT}-private-rt" \
    --query 'RouteTables[0].RouteTableId')"

if [[ "$PRIVATE_RT_ID" == "None" ]]; then
    PRIVATE_RT_ID="$(lookup ec2 create-route-table \
        --vpc-id "$VPC_ID" \
        --tag-specifications \
        "ResourceType=route-table,Tags=[{Key=Name,Value=${PROJECT}-private-rt}]" \
        --query 'RouteTable.RouteTableId')"

    aws ec2 create-route \
        --route-table-id "$PRIVATE_RT_ID" \
        --destination-cidr-block 0.0.0.0/0 \
        --nat-gateway-id "$NAT_ID"

    aws ec2 associate-route-table \
        --route-table-id "$PRIVATE_RT_ID" \
        --subnet-id "$PRIVATE_SUBNET_ID"
fi

# ---------------------------------------------------------------------------
# 2. Security Groups
# ---------------------------------------------------------------------------

log "Creating or reusing security groups"

API_SG_ID="$(lookup ec2 describe-security-groups \
    --filters "Name=group-name,Values=${PROJECT}-api-sg" \
              "Name=vpc-id,Values=$VPC_ID" \
    --query 'SecurityGroups[0].GroupId')"

if [[ "$API_SG_ID" == "None" ]]; then
    API_SG_ID="$(lookup ec2 create-security-group \
        --group-name "${PROJECT}-api-sg" \
        --description "Public API tier" \
        --vpc-id "$VPC_ID" \
        --query 'GroupId')"
fi

DB_SG_ID="$(lookup ec2 describe-security-groups \
    --filters "Name=group-name,Values=${PROJECT}-db-sg" \
              "Name=vpc-id,Values=$VPC_ID" \
    --query 'SecurityGroups[0].GroupId')"

if [[ "$DB_SG_ID" == "None" ]]; then
    DB_SG_ID="$(lookup ec2 create-security-group \
        --group-name "${PROJECT}-db-sg" \
        --description "Private database tier" \
        --vpc-id "$VPC_ID" \
        --query 'GroupId')"
fi

# Duplicate-rule errors are harmless during a repeated deployment.
aws ec2 authorize-security-group-ingress \
    --group-id "$API_SG_ID" \
    --protocol tcp --port 22 --cidr "$MY_IP_CIDR" 2>/dev/null || true

aws ec2 authorize-security-group-ingress \
    --group-id "$API_SG_ID" \
    --protocol tcp --port 80 --cidr 0.0.0.0/0 2>/dev/null || true

aws ec2 authorize-security-group-ingress \
    --group-id "$API_SG_ID" \
    --protocol tcp --port 443 --cidr 0.0.0.0/0 2>/dev/null || true

# Port 8000 is intentionally not public. Nginx proxies to localhost:8000.
aws ec2 authorize-security-group-ingress \
    --group-id "$DB_SG_ID" \
    --ip-permissions \
    "IpProtocol=tcp,FromPort=5432,ToPort=5432,UserIdGroupPairs=[{GroupId=${API_SG_ID}}]" \
    2>/dev/null || true

aws ec2 authorize-security-group-ingress \
    --group-id "$DB_SG_ID" \
    --ip-permissions \
    "IpProtocol=tcp,FromPort=22,ToPort=22,UserIdGroupPairs=[{GroupId=${API_SG_ID}}]" \
    2>/dev/null || true

# ---------------------------------------------------------------------------
# 3. Compute
# ---------------------------------------------------------------------------

log "Resolving the latest Amazon Linux 2023 AMI"

AMI_ID="$(lookup ssm get-parameter \
    --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 \
    --query 'Parameter.Value')"

# These user-data scripts deliberately remain high level. They install the
# dependencies and document the major configuration performed on each tier.

cat > /tmp/db-user-data.sh <<'DB_USER_DATA'
#!/bin/bash
set -eux
dnf update -y
dnf install -y postgresql18 postgresql18-server git

# Initialize and start PostgreSQL if it has not already been initialized.
if [[ ! -f /var/lib/pgsql/data/PG_VERSION ]]; then
    postgresql-setup --initdb
fi

systemctl enable --now postgresql

# Deployment-specific database work:
#   1. Create career_journal and its dedicated application user.
#   2. Run database_setup.sql.
#   3. Grant schema, table, and sequence privileges.
#   4. Configure postgresql.conf to listen on the private interface.
#   5. Configure pg_hba.conf to accept only the API subnet/user/database.
#   6. Restart PostgreSQL.
DB_USER_DATA

cat > /tmp/api-user-data.sh <<API_USER_DATA
#!/bin/bash
set -eux
dnf update -y
dnf install -y git nginx

if [[ ! -d /home/ec2-user/journal-starter/.git ]]; then
    sudo -u ec2-user git clone "$REPOSITORY_URL" /home/ec2-user/journal-starter
fi

# Install uv and the required Python runtime.
sudo -u ec2-user bash -lc '
    command -v uv >/dev/null 2>&1 ||
        curl -LsSf https://astral.sh/uv/install.sh | sh
    cd /home/ec2-user/journal-starter
    ~/.local/bin/uv python install 3.12
    ~/.local/bin/uv sync
'

# Deployment-specific application work:
#   1. Create the protected environment file containing DATABASE_URL and LLM settings.
#   2. Create and enable the systemd Journal API service.
#   3. Run uvicorn on 127.0.0.1:8000 without --reload.
#   4. Configure Nginx to terminate TLS and proxy to localhost:8000.
systemctl enable --now nginx
API_USER_DATA

find_instance() {
    lookup ec2 describe-instances \
        --filters "Name=tag:Name,Values=$1" \
                  "Name=instance-state-name,Values=pending,running,stopping,stopped" \
        --query 'Reservations[0].Instances[0].InstanceId'
}

DB_INSTANCE_ID="$(find_instance "${PROJECT}-database")"
if [[ "$DB_INSTANCE_ID" == "None" ]]; then
    DB_INSTANCE_ID="$(lookup ec2 run-instances \
        --image-id "$AMI_ID" \
        --instance-type "$INSTANCE_TYPE" \
        --key-name "$KEY_NAME" \
        --subnet-id "$PRIVATE_SUBNET_ID" \
        --security-group-ids "$DB_SG_ID" \
        --no-associate-public-ip-address \
        --user-data file:///tmp/db-user-data.sh \
        --tag-specifications \
        "ResourceType=instance,Tags=[{Key=Name,Value=${PROJECT}-database},{Key=Tier,Value=database}]" \
        --query 'Instances[0].InstanceId')"
fi

API_INSTANCE_ID="$(find_instance "${PROJECT}-api")"
if [[ "$API_INSTANCE_ID" == "None" ]]; then
    API_INSTANCE_ID="$(lookup ec2 run-instances \
        --image-id "$AMI_ID" \
        --instance-type "$INSTANCE_TYPE" \
        --key-name "$KEY_NAME" \
        --subnet-id "$PUBLIC_SUBNET_ID" \
        --security-group-ids "$API_SG_ID" \
        --associate-public-ip-address \
        --user-data file:///tmp/api-user-data.sh \
        --tag-specifications \
        "ResourceType=instance,Tags=[{Key=Name,Value=${PROJECT}-api},{Key=Tier,Value=api}]" \
        --query 'Instances[0].InstanceId')"
fi

# ---------------------------------------------------------------------------
# 4. Summary
# ---------------------------------------------------------------------------

cat <<SUMMARY

Deployment complete or resources already existed.

VPC:              $VPC_ID ($VPC_CIDR)
Public subnet:    $PUBLIC_SUBNET_ID ($PUBLIC_CIDR)
Private subnet:   $PRIVATE_SUBNET_ID ($PRIVATE_CIDR)

API instance:     $API_INSTANCE_ID
API security:     HTTPS 443 and HTTP 80 from the internet
                  SSH 22 only from $MY_IP_CIDR
                  Port 8000 is local to the instance

Database instance:$DB_INSTANCE_ID
Database security:PostgreSQL 5432 and SSH 22 only from the API security group
                  No public IP

Traffic:
Internet -> 443 -> Nginx -> localhost:8000 -> PostgreSQL:5432

The user-data comments intentionally document the application and PostgreSQL
configuration at a high level instead of embedding secrets and every manual
configuration command in this script.
SUMMARY
