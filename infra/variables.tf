variable "aks_cluster_name" {
  description = "Name of the AKS cluster"
  type        = string
}

variable "namespace" {
  description = "Kubernetes namespace"
  type        = string
}

variable "service_account_name" {
  description = "Kubernetes service account name"
  type        = string
}

variable "resource_group_name" {
  description = "Resource Group Name"
}

variable "location" {
  description = "Location for the resources"
}

variable "acr_name" {
  description = "Azure Container Registry Name"
}

variable "acr_identity_name" {

  description = "journal api acr pull identity name"
}