terraform {
  required_providers { aws = { source = "hashicorp/aws", version = "~> 5.0" } }
}
provider "aws" { region = "eu-central-1" }
resource "aws_s3_bucket" "isa" { bucket = "isa-esg-v2-1-data" }
