terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "ap-southeast-1" # Jakarta / Singapore Region
}

# 1. Production Data Lakehouse Bucket (S3)
resource "aws_s3_bucket" "enterprise_datalake" {
  bucket        = "godmode-enterprise-datalake-prod-001"
  force_destroy = false

  tags = {
    Environment = "Production"
    ManagedBy   = "Terraform"
    DataTier    = "Lakehouse"
  }
}

# 2. Enkripsi Data S3 Standar Perbankan (KMS AES-256)
resource "aws_s3_bucket_server_side_encryption_configuration" "datalake_enc" {
  bucket = aws_s3_bucket.enterprise_datalake.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# 3. Lifecycle Policy: Otomatis arsipkan data lawas ke Glacier
resource "aws_s3_bucket_lifecycle_configuration" "datalake_lifecycle" {
  bucket = aws_s3_bucket.enterprise_datalake.id

  rule {
    id     = "archive_old_partitions"
    status = "Enabled"

    transition {
      days          = 90
      storage_class = "STANDARD_IA"
    }
    transition {
      days          = 365
      storage_class = "GLACIER"
    }
  }
}