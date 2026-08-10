output "ecr_repository_url" {
  description = "The URL of the ECR repository"
  value       = aws_ecr_repository.journal-api.repository_url
}

output "eks_cluster_endpoint" {
  description = "The endpoint of the EKS cluster"
  value       = aws_eks_cluster.journal-api-eks-cluster.endpoint
}

output "eks_cluster_name" {
  description = "The name of the EKS cluster"
  value       = aws_eks_cluster.journal-api-eks-cluster.name
}

output "kubeconfig_command" {
  description = "The command to generate the kubeconfig for the EKS cluster"
  value       = "aws eks update-kubeconfig --name ${aws_eks_cluster.journal-api-eks-cluster.name} --region ${var.aws_region}"
}

output "db_endpoint" {
  description = "The endpoint of the RDS database"
  value       = aws_db_instance.journal-api-postgresql.endpoint
}

output "db_port" {
  description = "The port of the RDS database"
  value       = aws_db_instance.journal-api-postgresql.port
}

output "db_connection_string" {
  description = "The connection string for the RDS database"
  value       = "postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.journal-api-postgresql.endpoint}:${aws_db_instance.journal-api-postgresql.port}/${var.db_name}"
}

