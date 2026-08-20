vpc_cidr_block              = "192.168.0.0/16"
public_subnets_cidr_blocks  = ["192.168.0.0/18", "192.168.64.0/18"]
private_subnets_cidr_blocks = ["192.168.128.0/18", "192.168.192.0/18"]
availability_zones          = ["us-east-1a", "us-east-1b"]
ecr_repository_name         = "journal-api"
eks_cluster_name            = "journal-api-eks-cluster"
kubernetes_version          = "1.36"
eks_node_group_name         = "journal-api-nodes"
eks_node_instance_type      = "t3.medium"
eks_node_desired_nodes      = 2
eks_node_min_nodes          = 2
eks_node_max_nodes          = 2
db_identifier               = "journal-api-postgresql"
db_name                     = "journal_api_db"
db_instance_class           = "db.t3.micro"
db_allocated_storage        = 10


