data "azurerm_client_config" "current" {}

resource "azurerm_key_vault" "journal_kv" {
  name                       = "journalkv"
  location                   = azurerm_resource_group.resource_group.location
  resource_group_name        = azurerm_resource_group.resource_group.name
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  soft_delete_retention_days = 7
  sku_name                   = "standard"

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id

    secret_permissions = [
      "Set",
      "Get",
      "Delete",
      "Purge",
      "Recover",
      "List"
    ]
  }
}

resource "azurerm_key_vault_secret" "postgres_password" {
  name         = "postgrespassword"
  value        = "placeholder"
  key_vault_id = azurerm_key_vault.journal_kv.id

  lifecycle {
    ignore_changes = [value]
  }
}

resource "azurerm_key_vault_secret" "openai_api_key" {
  name         = "OpenAiApiKey"
  value        = "placeholder"
  key_vault_id = azurerm_key_vault.journal_kv.id

  lifecycle {
    ignore_changes = [value]
  }
}

resource "azurerm_key_vault_secret" "database_url" {
  name         = "databaseurl"
  value        = "placeholder"
  key_vault_id = azurerm_key_vault.journal_kv.id

  lifecycle {
    ignore_changes = [value]
  }
}

resource "azurerm_key_vault_access_policy" "csi_driver" {
  key_vault_id = azurerm_key_vault.journal_kv.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = azurerm_kubernetes_cluster.cluster.key_vault_secrets_provider[0].secret_identity[0].object_id

  secret_permissions = ["Get", "List"]
  depends_on         = [azurerm_kubernetes_cluster.cluster]
}