import {
  to = aws_ecr_repository.journal-api
  id = "journal-api"
}

# ============================================================
# Networking
# ============================================================

#VPC 
resource "aws_vpc" "journal-api-eks-vpc" {
  cidr_block = var.vpc_cidr_block
}

#Public subnets
resource "aws_subnet" "journal-api-eks-vpc-PublicSubnet01" {
  vpc_id                  = aws_vpc.journal-api-eks-vpc.id
  cidr_block              = var.public_subnets_cidr_blocks[0]
  availability_zone       = var.availability_zones[0]
  map_public_ip_on_launch = true

}

resource "aws_subnet" "journal-api-eks-vpc-PublicSubnet02" {
  vpc_id                  = aws_vpc.journal-api-eks-vpc.id
  cidr_block              = var.public_subnets_cidr_blocks[1]
  availability_zone       = var.availability_zones[1]
  map_public_ip_on_launch = true
}

#Private subnets
resource "aws_subnet" "journal-api-eks-vpc-PrivateSubnet01" {
  vpc_id            = aws_vpc.journal-api-eks-vpc.id
  cidr_block        = var.private_subnets_cidr_blocks[0]
  availability_zone = var.availability_zones[0]
}

resource "aws_subnet" "journal-api-eks-vpc-PrivateSubnet02" {
  vpc_id            = aws_vpc.journal-api-eks-vpc.id
  cidr_block        = var.private_subnets_cidr_blocks[1]
  availability_zone = var.availability_zones[1]
}

#Internet Gateway
resource "aws_internet_gateway" "journal-api-eks-vpc-igw" {
  vpc_id = aws_vpc.journal-api-eks-vpc.id
}

#Elastic IPs for NAT Gateways
resource "aws_eip" "journal-api-eks-vpc-NatGatewayEIPAZ1" {
  domain = "vpc"
}

resource "aws_eip" "journal-api-eks-vpc-NatGatewayEIPAZ2" {
  domain = "vpc"
}

#Nat Gateway
resource "aws_nat_gateway" "journal-api-eks-vpc-NatGatewayAZ1" {
  allocation_id = aws_eip.journal-api-eks-vpc-NatGatewayEIPAZ1.id
  subnet_id     = aws_subnet.journal-api-eks-vpc-PublicSubnet01.id
}

resource "aws_nat_gateway" "journal-api-eks-vpc-NatGatewayAZ2" {
  allocation_id = aws_eip.journal-api-eks-vpc-NatGatewayEIPAZ2.id
  subnet_id     = aws_subnet.journal-api-eks-vpc-PublicSubnet02.id
}

# Routes tables / associations
resource "aws_route_table" "Public_Subnets" {
  vpc_id = aws_vpc.journal-api-eks-vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.journal-api-eks-vpc-igw.id
  }
}

resource "aws_route_table_association" "Public_Subnet_1" {
  subnet_id      = aws_subnet.journal-api-eks-vpc-PublicSubnet01.id
  route_table_id = aws_route_table.Public_Subnets.id
}

resource "aws_route_table_association" "Public_Subnet_2" {
  subnet_id      = aws_subnet.journal-api-eks-vpc-PublicSubnet02.id
  route_table_id = aws_route_table.Public_Subnets.id
}

resource "aws_route_table" "Private_Subnet_AZ1" {
  vpc_id = aws_vpc.journal-api-eks-vpc.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.journal-api-eks-vpc-NatGatewayAZ1.id
  }
}

resource "aws_route_table" "Private_Subnet_AZ2" {
  vpc_id = aws_vpc.journal-api-eks-vpc.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.journal-api-eks-vpc-NatGatewayAZ2.id
  }
}

resource "aws_route_table_association" "Private_Subnet_1" {
  subnet_id      = aws_subnet.journal-api-eks-vpc-PrivateSubnet01.id
  route_table_id = aws_route_table.Private_Subnet_AZ1.id
}

resource "aws_route_table_association" "Private_Subnet_2" {
  subnet_id      = aws_subnet.journal-api-eks-vpc-PrivateSubnet02.id
  route_table_id = aws_route_table.Private_Subnet_AZ2.id
}

# ============================================================
# Container Registry
# ============================================================

resource "aws_ecr_repository" "journal-api" {
  name                 = var.ecr_repository_name
  image_tag_mutability = "MUTABLE"
}

# ============================================================
# EKS IAM
# ============================================================

resource "aws_iam_role" "JournalApiEKSClusterRole" {
  name = "JournalApiEKSClusterRole"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {
  role       = aws_iam_role.JournalApiEKSClusterRole.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}


# ============================================================
# EKS Cluster
# ============================================================

resource "aws_eks_cluster" "journal-api-eks-cluster" {
  name     = var.eks_cluster_name
  role_arn = aws_iam_role.JournalApiEKSClusterRole.arn
  version  = var.kubernetes_version

  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy
  ]

  vpc_config {
    subnet_ids = [
      aws_subnet.journal-api-eks-vpc-PublicSubnet01.id,
      aws_subnet.journal-api-eks-vpc-PublicSubnet02.id,
      aws_subnet.journal-api-eks-vpc-PrivateSubnet01.id,
      aws_subnet.journal-api-eks-vpc-PrivateSubnet02.id
    ]
  }
}

# ============================================================
# EKS Worker Node IAM
# ============================================================

resource "aws_iam_role" "JournalApiEKSWorkerNodeRole" {
  name = "JournalApiEKSWorkerNodeRole"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "eks_worker_node_policy" {
  role       = aws_iam_role.JournalApiEKSWorkerNodeRole.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
}

resource "aws_iam_role_policy_attachment" "eks_cni_policy" {
  role       = aws_iam_role.JournalApiEKSWorkerNodeRole.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
}

resource "aws_iam_role_policy_attachment" "eks_registry_policy" {
  role       = aws_iam_role.JournalApiEKSWorkerNodeRole.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPullOnly"
}

# ============================================================
# EKS Managed Node Group
# ============================================================

resource "aws_eks_node_group" "journal-api-nodes" {
  cluster_name    = aws_eks_cluster.journal-api-eks-cluster.name
  node_group_name = var.eks_node_group_name
  node_role_arn   = aws_iam_role.JournalApiEKSWorkerNodeRole.arn
  subnet_ids = [
    aws_subnet.journal-api-eks-vpc-PrivateSubnet01.id,
    aws_subnet.journal-api-eks-vpc-PrivateSubnet02.id
  ]

  depends_on = [
    aws_iam_role_policy_attachment.eks_registry_policy,
    aws_iam_role_policy_attachment.eks_worker_node_policy,
    aws_iam_role_policy_attachment.eks_cni_policy
  ]

  scaling_config {
    desired_size = var.eks_node_desired_nodes
    max_size     = var.eks_node_max_nodes
    min_size     = var.eks_node_min_nodes
  }

  instance_types = [var.eks_node_instance_type]
}

# ============================================================
# PostgreSQL Security Group
# ============================================================

resource "aws_security_group" "postgresql" {
  name        = "postgresql"
  description = "Allow PostgreSQL access"
  vpc_id      = aws_vpc.journal-api-eks-vpc.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_eks_cluster.journal-api-eks-cluster.vpc_config[0].cluster_security_group_id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ============================================================
# RDS Subnet Group
# ============================================================

resource "aws_db_subnet_group" "journal-api-db-subnet-group" {
  name = "journal-api-db-subnet-group"
  subnet_ids = [
    aws_subnet.journal-api-eks-vpc-PrivateSubnet01.id,
    aws_subnet.journal-api-eks-vpc-PrivateSubnet02.id
  ]
}

# ============================================================
# PostgreSQL RDS
# ============================================================

resource "aws_db_instance" "journal-api-postgresql" {
  identifier             = var.db_identifier
  allocated_storage      = var.db_allocated_storage
  db_name                = var.db_name
  engine                 = "postgres"
  engine_version         = "15"
  instance_class         = var.db_instance_class
  username               = var.db_username
  password               = var.db_password
  db_subnet_group_name   = aws_db_subnet_group.journal-api-db-subnet-group.name
  vpc_security_group_ids = [aws_security_group.postgresql.id]
  skip_final_snapshot    = true
  publicly_accessible    = false
  storage_encrypted      = true
}

# ============================================================
# Remote Backend S3 Bucket
# ============================================================

resource "aws_s3_bucket" "journal-api_bucket" {
  bucket = "journal-api-bucket"
}
