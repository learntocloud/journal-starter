terraform {
  backend "s3" {
    bucket       = "journal-api-bucket"
    key          = "journal-api/terraform.tfstate"
    region       = "us-east-1"
    use_lockfile = true
    encrypt      = true
  }
}
