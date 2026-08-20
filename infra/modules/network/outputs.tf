output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.journal-api-eks-vpc.id
}

output "public_subnet_ids" {
  description = "Public Subnet IDs"
  value       = [aws_subnet.journal-api-eks-vpc-PublicSubnet01.id, aws_subnet.journal-api-eks-vpc-PublicSubnet02.id]
}

output "private_subnet_ids" {
  description = "Private Subnet IDs"
  value       = [aws_subnet.journal-api-eks-vpc-PrivateSubnet01.id, aws_subnet.journal-api-eks-vpc-PrivateSubnet02.id]
}
