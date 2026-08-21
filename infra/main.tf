module "network" {
  source = "./modules/network"

  vpc_cidr_block              = var.vpc_cidr_block
  public_subnets_cidr_blocks  = var.public_subnets_cidr_blocks
  private_subnets_cidr_blocks = var.private_subnets_cidr_blocks
  availability_zones          = var.availability_zones

}

resource "aws_ecr_repository" "journal-api" {
  name                 = var.ecr_repository_name
  image_tag_mutability = "MUTABLE"
}

module "eks" {
  source = "./modules/eks"

  public_subnet_ids  = module.network.public_subnet_ids
  private_subnet_ids = module.network.private_subnet_ids

  eks_cluster_name        = var.eks_cluster_name
  github_actions_role_arn = var.github_actions_role_arn
  kubernetes_version      = var.kubernetes_version
  eks_node_group_name     = var.eks_node_group_name
  eks_node_instance_type  = var.eks_node_instance_type
  eks_node_desired_nodes  = var.eks_node_desired_nodes
  eks_node_min_nodes      = var.eks_node_min_nodes
  eks_node_max_nodes      = var.eks_node_max_nodes
}

module "database" {
  source = "./modules/database"

  vpc_id                        = module.network.vpc_id
  private_subnet_ids            = module.network.private_subnet_ids
  eks_cluster_security_group_id = module.eks.cluster_security_group_id

  db_identifier        = var.db_identifier
  db_name              = var.db_name
  db_instance_class    = var.db_instance_class
  db_allocated_storage = var.db_allocated_storage
  db_username          = var.db_username
  db_password          = var.db_password
}

