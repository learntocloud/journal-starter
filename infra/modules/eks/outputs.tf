output "cluster_name" {
  description = "Name of the EKS cluster"
  value       = aws_eks_cluster.journal-api-eks-cluster.name
}

output "cluster_endpoint" {
  description = "Endpoint of the EKS cluster"
  value       = aws_eks_cluster.journal-api-eks-cluster.endpoint
}

output "cluster_security_group_id" {
  description = "EKS cluster security group ID"
  value       = aws_eks_cluster.journal-api-eks-cluster.vpc_config[0].cluster_security_group_id
}
