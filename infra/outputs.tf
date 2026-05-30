output "github_actions_azure_client_id" {
  description = "Save this as AZURE_CLIENT_ID in your GitHub Secrets"
  value       = azurerm_user_assigned_identity.github_deploy.client_id
}

output "github_actions_azure_tenant_id" {
  description = "Save this as AZURE_TENANT_ID in your GitHub Secrets"
  value       = data.azurerm_client_config.current.tenant_id
}

output "github_actions_azure_subscription_id" {
  description = "Save this as AZURE_SUBSCRIPTION_ID in your GitHub Secrets"
  value       = data.azurerm_client_config.current.subscription_id
}

output "azurerm_user_assigned_identity_principal_id" {
  value = azurerm_user_assigned_identity.github_deploy.principal_id
}

output "acr_pull_client_id" {
  description = "Client ID for acr_pull identity - use in service account annotations"
  value       = azurerm_user_assigned_identity.acr_pull.client_id
}

output "acr_pull_principal_id" {
  description = "Principal ID for acr_pull identity"
  value       = azurerm_user_assigned_identity.acr_pull.principal_id
}