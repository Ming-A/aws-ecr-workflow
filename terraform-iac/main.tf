resource "aws_ecr_repository" "app_ecr_repo" {
    for_each = toset(var.ecr_repository_names)
    name = each.key
    image_tag_mutability = var.image_tag_mutability
  
    image_scanning_configuration {
      scan_on_push = var.scan_on_push
    }

    tags = {
        Enviroment = "Dev"
        ManagedBy = "Terraform"
        Project = "aws-ecr-workflow-github"
    }
}