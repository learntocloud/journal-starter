resource "aws_security_group" "postgresql" {
  name        = "postgresql"
  description = "Allow PostgreSQL access"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [var.eks_cluster_security_group_id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_subnet_group" "journal-api-db-subnet-group" {
  name       = "journal-api-db-subnet-group"
  subnet_ids = var.private_subnet_ids
}

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
