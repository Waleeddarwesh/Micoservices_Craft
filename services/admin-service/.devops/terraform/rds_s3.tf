# =============================================================================
# Handcrafts — RDS (PostgreSQL) & S3 (Media Storage)
# =============================================================================
# Managed database and object storage for the Handcrafts platform.
#
# RDS:
#   - Multi-AZ subnet group for high availability
#   - Encrypted at rest using the default AWS KMS key
#   - Accessible only from within the VPC (not publicly exposed)
#
# S3:
#   - Stores product images and user-uploaded media
#   - Server-side encryption enabled by default
#   - Public access is blocked at the bucket level
# =============================================================================


# ---------------------------------------------------------------------------
# Security Group — Database
# ---------------------------------------------------------------------------
resource "aws_security_group" "database" {
  name        = "${local.name_prefix}-db-sg"
  description = "Allow PostgreSQL traffic from within the VPC only"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "PostgreSQL from VPC"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.main.cidr_block]
  }

  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${local.name_prefix}-db-sg"
  }
}


# ---------------------------------------------------------------------------
# RDS Subnet Group — place the database in private subnets
# ---------------------------------------------------------------------------
resource "aws_db_subnet_group" "main" {
  name       = "${local.name_prefix}-db-subnet-group"
  subnet_ids = [aws_subnet.private_a.id, aws_subnet.private_b.id]

  tags = {
    Name = "${local.name_prefix}-db-subnet-group"
  }
}


# ---------------------------------------------------------------------------
# RDS Instance — PostgreSQL 15
# ---------------------------------------------------------------------------
resource "aws_db_instance" "postgres" {
  identifier     = "${local.name_prefix}-postgres"
  engine         = "postgres"
  engine_version = "15"
  instance_class = var.db_instance_class

  allocated_storage     = 20
  max_allocated_storage = 100
  storage_encrypted     = true

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.database.id]
  publicly_accessible    = false

  # Backups
  backup_retention_period = 7
  backup_window           = "03:00-04:00"
  maintenance_window      = "sun:05:00-sun:06:00"

  # Don't delete the final snapshot when tearing down (safety net)
  skip_final_snapshot       = false
  final_snapshot_identifier = "${local.name_prefix}-final-snapshot"

  tags = {
    Name = "${local.name_prefix}-postgres"
  }
}


# ---------------------------------------------------------------------------
# S3 Bucket — Media Files
# ---------------------------------------------------------------------------
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

resource "aws_s3_bucket" "media" {
  bucket = "${local.name_prefix}-media-${random_id.bucket_suffix.hex}"

  tags = {
    Name = "${local.name_prefix}-media"
  }
}

# Versioning — recover accidentally deleted product images
resource "aws_s3_bucket_versioning" "media" {
  bucket = aws_s3_bucket.media.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Encryption — all objects encrypted at rest using AES-256
resource "aws_s3_bucket_server_side_encryption_configuration" "media" {
  bucket = aws_s3_bucket.media.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Block all public access — media is served through the app, not directly
resource "aws_s3_bucket_public_access_block" "media" {
  bucket = aws_s3_bucket.media.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# CORS — allow the Django app to upload directly from the browser if needed
resource "aws_s3_bucket_cors_configuration" "media" {
  bucket = aws_s3_bucket.media.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "PUT", "POST"]
    allowed_origins = ["https://api.handcrafts.example.com"]
    max_age_seconds = 3600
  }
}
