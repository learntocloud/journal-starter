variable "public_subnet_ids" {
  description = "Public subnet IDs for the EKS cluster"
  type        = list(string)
}

variable "private_subnet_ids" {
  description = "Private subnet IDs for the EKS cluster and worker nodes"
  type        = list(string)
}

variable "eks_cluster_name" {
  description = "The name of the EKS cluster"
  type        = string
}

variable "kubernetes_version" {
  description = "The Kubernetes version for the EKS cluster"
  type        = string
}

variable "eks_node_group_name" {
  description = "The name of the EKS node group"
  type        = string
}

variable "eks_node_instance_type" {
  description = "The EC2 instance type for EKS worker nodes"
  type        = string
}

variable "eks_node_desired_nodes" {
  description = "Desired number of EKS worker nodes"
  type        = number
}

variable "eks_node_min_nodes" {
  description = "Minimum number of EKS worker nodes"
  type        = number
}

variable "eks_node_max_nodes" {
  description = "Maximum number of EKS worker nodes"
  type        = number
}
