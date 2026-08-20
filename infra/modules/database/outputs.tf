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
  sensitive   = true
}
