# =============================================================================
# Handcrafts — Terraform Variables
# =============================================================================
# Centralized variable definitions. Override values in terraform.tfvars
# or via CLI:  terraform apply -var="environment=staging"
# =============================================================================

variable "aws_region" {
  description = "AWS region to deploy resources into"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment (dev, staging, production)"
  type        = string
  default     = "production"

  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be one of: dev, staging, production."
  }
}

variable "db_instance_class" {
  description = "RDS instance type"
  type        = string
  default     = "db.t3.micro"
}

variable "db_name" {
  description = "Name of the PostgreSQL database"
  type        = string
  default     = "handcrafts_db"
}

variable "db_username" {
  description = "Master username for the database"
  type        = string
  default     = "handcrafts_admin"
}

variable "db_password" {
  description = "Master password for the database"
  type        = string
  sensitive   = true
}
