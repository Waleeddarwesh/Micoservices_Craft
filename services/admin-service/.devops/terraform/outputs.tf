# =============================================================================
# Handcrafts — Terraform Outputs
# =============================================================================
# These values are printed after `terraform apply` and can be referenced
# by other Terraform configurations or CI/CD pipelines.
# =============================================================================

output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = [aws_subnet.public_a.id, aws_subnet.public_b.id]
}

output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value       = [aws_subnet.private_a.id, aws_subnet.private_b.id]
}

output "rds_endpoint" {
  description = "Endpoint of the RDS PostgreSQL instance"
  value       = aws_db_instance.postgres.endpoint
}

output "rds_database_name" {
  description = "Name of the database"
  value       = aws_db_instance.postgres.db_name
}

output "s3_media_bucket" {
  description = "Name of the S3 bucket for media files"
  value       = aws_s3_bucket.media.bucket
}

output "s3_media_bucket_arn" {
  description = "ARN of the S3 media bucket"
  value       = aws_s3_bucket.media.arn
}
