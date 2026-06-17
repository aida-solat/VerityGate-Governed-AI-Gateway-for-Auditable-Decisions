variable "location" {
  default = "westeurope"
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "pg_sku" {
  default = "B_Standard_B1ms"
}

variable "acr_login_server" {
  type        = string
  description = "Azure Container Registry login server, e.g. veritygate.azurecr.io"
}

variable "max_replicas" {
  default = 5
}

variable "otel_endpoint" {
  default = "http://localhost:4317"
}
