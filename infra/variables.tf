variable "aws_region" {
  description = "The AWS region to deploy resources in"
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr_block" {
  description = "The CIDR block for the VPC"
  type        = string
  }
  
variable "public_subnets_cidr_blocks" {
  description = "The CIDR blocks for the public subnets"
  type        = list(string)
}

variable "private_subnets_cidr_blocks" {
  description = "The CIDR blocks for the private subnets"
  type        = list(string)
}

variable "availability_zones" {
  description = "The availability zones to deploy resources in"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "ecr_repository_name" {
  description = "The name of the ECR repository"
  type        = string
}

variable "eks_cluster_name" {
  description = "The name of the EKS cluster"
  type        = string
}

variable "kubernetes_version" {
  description = "The version of Kubernetes to use for the EKS cluster"
  type        = string
}

variable "eks_node_group_name" {
  description = "The name of the EKS node group"
  type        = string
}

variable "eks_node_instance_type" {
  description = "The instance type for the EKS node group"
  type        = string
}

variable "eks_node_desired_nodes" {
  description = "The desired number of nodes for the EKS node group"
  type        = number
}

variable "eks_node_min_nodes" {
  description = "The minimum number of nodes for the EKS node group"
  type        = number
}

variable "eks_node_max_nodes" {
  description = "The maximum number of nodes for the EKS node group"
  type        = number
}

variable "db_identifier" {
  description = "The identifier for the RDS database"
  type        = string
}

variable "db_name" {
  description = "The name of the RDS database"
  type        = string
}

variable "db_instance_class" {
  description = "The instance class for the RDS database"
  type        = string
}

variable "db_allocated_storage" {
  description = "The allocated storage for the RDS database"
  type        = number
}

variable "db_username" {
  description = "The username for the RDS database"
  type        = string
}

variable "db_password" {
  description = "The password for the RDS database"
  type        = string
}