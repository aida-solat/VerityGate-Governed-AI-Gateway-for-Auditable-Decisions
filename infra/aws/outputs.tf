output "alb_dns" {
  value       = aws_lb.main.dns_name
  description = "Public DNS for the ALB fronting the backend"
}

output "db_endpoint" {
  value       = aws_db_instance.postgres.endpoint
  description = "RDS Postgres endpoint"
  sensitive   = true
}

output "redis_endpoint" {
  value       = aws_elasticache_cluster.redis.cache_nodes[0].address
  description = "ElastiCache Redis endpoint"
}

output "ecs_cluster" {
  value = aws_ecs_cluster.main.name
}
