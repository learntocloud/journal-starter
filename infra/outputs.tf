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