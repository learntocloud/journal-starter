resource "azurerm_resource_group" "resource_group" {
  name     = var.resource_group_name
  location = var.location
}


# Get the ACR data
data "azurerm_container_registry" "acr" {
  name                = azurerm_container_registry.acr.name
  resource_group_name = azurerm_resource_group.resource_group.name
}

# Fetch information about your existing AKS cluster
data "azurerm_kubernetes_cluster" "aks" {
  name                = azurerm_kubernetes_cluster.cluster.name
  resource_group_name = azurerm_kubernetes_cluster.cluster.resource_group_name

}

data "azurerm_user_assigned_identity" "acr_pull" {
  name                = azurerm_user_assigned_identity.acr_pull.name
  resource_group_name = azurerm_user_assigned_identity.acr_pull.resource_group_name
}

# Create the Azure Container Registry
resource "azurerm_container_registry" "acr" {
  name                = var.acr_name
  resource_group_name = azurerm_resource_group.resource_group.name
  location            = azurerm_resource_group.resource_group.location
  sku                 = "Standard"
  admin_enabled       = false

}


resource "azurerm_kubernetes_cluster" "cluster" {
  name                      = var.aks_cluster_name
  location                  = azurerm_resource_group.resource_group.location
  resource_group_name       = azurerm_resource_group.resource_group.name
  dns_prefix                = "learntocloud"
  workload_identity_enabled = true
  oidc_issuer_enabled       = true

  key_vault_secrets_provider {
    secret_rotation_enabled  = true # Optional: Enables automatic rotation
    secret_rotation_interval = "2m" # Optional: Default is 2m
  }

  default_node_pool {
    name       = "default"
    node_count = 1
    vm_size    = "Standard_a2_v2"
  }

  identity {
    type = "SystemAssigned"
  }

  tags = {
    Environment = "Development"
  }
}

resource "azurerm_virtual_network" "network" {
  name                = "learntocloud"
  location            = azurerm_resource_group.resource_group.location
  resource_group_name = azurerm_resource_group.resource_group.name
  address_space       = ["10.0.0.0/16"]
}
resource "azurerm_subnet" "private_subnet" {
  name                 = "journal-database"
  resource_group_name  = azurerm_resource_group.resource_group.name
  virtual_network_name = azurerm_virtual_network.network.name
  address_prefixes     = ["10.0.2.0/24"]
  service_endpoints    = ["Microsoft.Storage"]
  delegation {
    name = "fs"
    service_delegation {
      name = "Microsoft.DBforPostgreSQL/flexibleServers"
      actions = [
        "Microsoft.Network/virtualNetworks/subnets/join/action",
      ]
    }
  }
}
resource "azurerm_postgresql_flexible_server" "example" {
  name                = "journal-psqlflexibleserver"
  resource_group_name = azurerm_resource_group.resource_group.name
  location            = azurerm_resource_group.resource_group.location
  version             = "15"
  #delegated_subnet_id           = azurerm_subnet.private_subnet.id
  #private_dns_zone_id           = azurerm_private_dns_zone.dns_zone.id
  public_network_access_enabled = true
  administrator_login           = "postgres"
  administrator_password        = azurerm_key_vault_secret.postgres_password.value

  storage_mb   = 32768
  storage_tier = "P4"

  sku_name = "B_Standard_B1ms"

}

resource "azurerm_private_dns_zone" "dns_zone" {
  name                = "journal.postgres.database.azure.com"
  resource_group_name = azurerm_resource_group.resource_group.name
}

resource "azurerm_private_dns_zone_virtual_network_link" "dns_link" {
  name                  = "journal.com"
  private_dns_zone_name = azurerm_private_dns_zone.dns_zone.name
  virtual_network_id    = azurerm_virtual_network.network.id
  resource_group_name   = azurerm_resource_group.resource_group.name
  depends_on            = [azurerm_subnet.private_subnet]
}

# Create the User-Assigned Managed Identity
resource "azurerm_user_assigned_identity" "acr_pull" {
  name                = var.acr_identity_name
  location            = var.location
  resource_group_name = azurerm_resource_group.resource_group.name
}

# Assign the AcrPull role to the Managed Identity over the ACR scope
resource "azurerm_role_assignment" "acr_pull_assignment" {
  scope                = data.azurerm_container_registry.acr.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_user_assigned_identity.acr_pull.principal_id

  # Prevents deployment failures if Azure replication is slightly delayed
  skip_service_principal_aad_check = true
}

# Create the Federated Identity Credential
resource "azurerm_federated_identity_credential" "k8s_federation" {
  name                = "journal-api-federation"
  resource_group_name = azurerm_resource_group.resource_group.name

  # The Azure Managed Identity that will hold this trust configuration
  parent_id = azurerm_user_assigned_identity.acr_pull.id

  # Must always be exactly this array for Azure AD Workload Identity exchanges
  audience = ["api://AzureADTokenExchange"]

  # Dynamically points to your AKS Cluster's secure token issuer
  issuer = data.azurerm_kubernetes_cluster.aks.oidc_issuer_url

  # Crucial Security String: Restricts trust to a specific namespace and ServiceAccount name
  # Pattern format: system:serviceaccount:<K8S_NAMESPACE>:<SERVICE_ACCOUNT_NAME>
  subject = "system:serviceaccount:default:journal-api"
}

resource "azurerm_user_assigned_identity" "github_deploy" {
  name                = "github-deploy-identity"
  location            = var.location
  resource_group_name = azurerm_resource_group.resource_group.name
}

# Assign the AcrPush role to the Managed Identity over the ACR scope
resource "azurerm_role_assignment" "github_acr_push" {
  scope                = data.azurerm_container_registry.acr.id
  role_definition_name = "AcrPush"
  principal_id         = azurerm_user_assigned_identity.github_deploy.principal_id

  # Prevents deployment failures if Azure replication is slightly delayed
  skip_service_principal_aad_check = true
}

# Assign the AcrPull role to the Managed Identity over the ACR scope
resource "azurerm_role_assignment" "github_acr_pull" {
  scope                = data.azurerm_container_registry.acr.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_user_assigned_identity.github_deploy.principal_id

  # Prevents deployment failures if Azure replication is slightly delayed
  skip_service_principal_aad_check = true
}

resource "azurerm_role_assignment" "aks_cluster_user" {
  scope                = azurerm_kubernetes_cluster.cluster.id
  role_definition_name = "Azure Kubernetes Service Cluster User Role"
  principal_id         = azurerm_user_assigned_identity.github_deploy.principal_id

  skip_service_principal_aad_check = true
}

resource "azurerm_role_assignment" "aks_rbac_writer" {
  scope                = azurerm_kubernetes_cluster.cluster.id
  role_definition_name = "Azure Kubernetes Service RBAC Writer"
  principal_id         = azurerm_user_assigned_identity.github_deploy.principal_id
}

resource "azurerm_federated_identity_credential" "github_federation" {
  name                = "github-actions-main-branch"
  resource_group_name = azurerm_resource_group.resource_group.name
  parent_id           = azurerm_user_assigned_identity.github_deploy.id

  # Must be this exact value for GitHub Actions
  audience = ["api://AzureADTokenExchange"]

  # The OIDC issuer URL for GitHub Actions
  issuer = "https://token.actions.githubusercontent.com"

  # CRITICAL SECURITY RULE: Restrict trust to your specific repo and branch
  # Format: repo:<org-or-username>/<repository-name>:ref:refs/heads/<branch-name>
  subject = "repo:sudheer-yelleti/journal-starter:ref:refs/heads/main"
}

resource "azurerm_role_assignment" "acr_pull_keyvault" {
  scope                = azurerm_key_vault.journal_kv.id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azurerm_user_assigned_identity.acr_pull.principal_id

  skip_service_principal_aad_check = true
}

resource "azurerm_role_assignment" "aks_kubelet_acr_pull" {
  # Reference the resource directly instead of using a data block
  scope                            = azurerm_container_registry.acr.id
  role_definition_name             = "AcrPull"
  
  # This targets the built-in identity AKS uses to manage nodes and pull images
  principal_id                     = azurerm_kubernetes_cluster.cluster.kubelet_identity[0].object_id
  skip_service_principal_aad_check = true
}

resource "azurerm_application_insights" "journalapi" {
  name                = "journal-api-appinsights"
  location            = var.location
  resource_group_name = azurerm_resource_group.resource_group.name
  application_type    = "web"
}

resource "azurerm_key_vault_secret" "app_insights_connection_string" {
  name         = "AppInsightsConnectionString"
  value        = azurerm_application_insights.journalapi.connection_string
  key_vault_id = azurerm_key_vault.journal_kv.id

  depends_on = [azurerm_application_insights.journalapi]
}