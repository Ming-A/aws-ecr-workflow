variable "aws_region" {
  description = "Set region for ECR"
  type = string
  default = "ap-southeast-1"
}

variable "ecr_repository_names" {
  description = "Name of the ECR images"
  type = list(string)
  default = [ "test-nodejs-app_1", "test-python-app_1" ]
}

variable "image_tag_mutability" {
  description = "States whether the images are mutable"
  type = string
  default = "IMMUTABLE"
}

variable "scan_on_push" {
  description = "Check the images for vulnerability"
  type = bool
  default = true
}