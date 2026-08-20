output "ecr_repository_url" {
  description = "The URL of the ECR repository"
  value       = aws_ecr_repository.journal-api.repository_url
}

output "eks_cluster_endpoint" {
  description = "The endpoint of the EKS cluster"
  value       = module.eks.cluster_endpoint
}

output "eks_cluster_name" {
  description = "The name of the EKS cluster"
  value       = module.eks.cluster_name
}

output "kubeconfig_command" {
  description = "The command to generate the kubeconfig for the EKS cluster"
  value       = "aws eks update-kubeconfig --name ${module.eks.cluster_name} --region ${var.aws_region}"
}

output "db_endpoint" {
  description = "The endpoint of the RDS database"
  value       = module.database.db_endpoint
}

output "db_port" {
  description = "The port of the RDS database"
  value       = module.database.db_port
}

output "db_connection_string" {
  description = "The connection string for the RDS database"
  value       = "postgresql://${var.db_username}:${var.db_password}@${module.database.db_endpoint}:${module.database.db_port}/${var.db_name}"
  sensitive   = true
}

