# Example Terraform variables - copy to terraform.tfvars and fill in your values
resource_group_name  = "learntocloud"
aks_cluster_name     = "learntocloud"
acr_name             = "journalapicontainerregistry"
namespace            = "learntocloud"
service_account_name = "journal-api"
location             = "westus"
acr_identity_name    = "journal-acr-pull-identity"
