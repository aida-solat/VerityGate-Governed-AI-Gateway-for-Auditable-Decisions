output "backend_url" {
  value       = "https://${azurerm_container_app.backend.ingress[0].fqdn}"
  description = "Public HTTPS URL for the backend Container App"
}

output "pg_fqdn" {
  value       = azurerm_postgresql_flexible_server.main.fqdn
  description = "PostgreSQL server FQDN"
  sensitive   = true
}

output "redis_hostname" {
  value       = azurerm_redis_cache.main.hostname
  description = "Azure Redis hostname"
}
