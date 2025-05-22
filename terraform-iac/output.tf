output "ecr_repository_url" {
  description = "URL created for the ECR repo"
  value = { for name, repo in aws_ecr_repository.app_ecr_repo : name => repo.repository_url }
}

output "ecr_repository_arns" {
  description = "value"
  value = { for name, repo in aws_ecr_repository.app_ecr_repo : name => repo.arn }
}