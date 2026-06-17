variable "aws_region" {
  default = "us-east-1"
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "db_instance_class" {
  default = "db.t4g.micro"
}

variable "redis_node_type" {
  default = "cache.t4g.micro"
}

variable "ecr_repo_url" {
  type        = string
  description = "ECR repository URL for the backend image"
}

variable "ecs_cpu" {
  default = "512"
}

variable "ecs_memory" {
  default = "1024"
}

variable "desired_count" {
  default = 2
}

variable "otel_endpoint" {
  default = "http://localhost:4317"
}
