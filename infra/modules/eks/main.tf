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

resource "aws_eks_access_entry" "github_actions" {
  cluster_name  = aws_eks_cluster.journal-api-eks-cluster.name
  principal_arn = var.github_actions_role_arn
  type          = "STANDARD"
}

resource "aws_eks_access_policy_association" "github_actions" {
  cluster_name  = aws_eks_cluster.journal-api-eks-cluster.name
  principal_arn = var.github_actions_role_arn

  policy_arn = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"

  access_scope {
    type = "cluster"
  }

  depends_on = [
    aws_eks_access_entry.github_actions
  ]
}

resource "aws_eks_cluster" "journal-api-eks-cluster" {
  name     = var.eks_cluster_name
  role_arn = aws_iam_role.JournalApiEKSClusterRole.arn
  version  = var.kubernetes_version

  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy
  ]

  vpc_config {
    subnet_ids = concat(
      var.public_subnet_ids,
      var.private_subnet_ids
    )
  }
}

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

resource "aws_eks_node_group" "journal-api-nodes" {
  cluster_name    = aws_eks_cluster.journal-api-eks-cluster.name
  node_group_name = var.eks_node_group_name
  node_role_arn   = aws_iam_role.JournalApiEKSWorkerNodeRole.arn
  subnet_ids      = var.private_subnet_ids

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
