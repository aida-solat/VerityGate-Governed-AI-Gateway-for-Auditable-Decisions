terraform {
  required_version = ">= 1.5"
  required_providers {
    azurerm = { source = "hashicorp/azurerm", version = "~> 4.0" }
  }
  backend "azurerm" {
    resource_group_name  = "veritygate-state-rg"
    storage_account_name = "veritygatestate"
    container_name       = "tfstate"
    key                  = "prod.terraform.tfstate"
  }
}

provider "azurerm" {
  features {}
}

# --- Resource Group ---
resource "azurerm_resource_group" "main" {
  name     = "veritygate-rg"
  location = var.location
}

# --- Azure Database for PostgreSQL Flexible Server (pgvector) ---
resource "azurerm_postgresql_flexible_server" "main" {
  name                = "veritygate-pg"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku_name            = var.pg_sku
  version             = "16"

  administrator_login    = "veritygate"
  administrator_password = var.db_password

  storage_mb = 32768
  zone       = "1"

  tags = { Project = "VerityGate" }
}

resource "azurerm_postgresql_flexible_server_database" "main" {
  name      = "veritygate"
  server_id = azurerm_postgresql_flexible_server.main.id
}

# Enable pgvector extension
resource "azurerm_postgresql_flexible_server_configuration" "extensions" {
  name      = "azure.extensions"
  server_id = azurerm_postgresql_flexible_server.main.id
  value     = "vector"
}

# --- Azure Cache for Redis ---
resource "azurerm_redis_cache" "main" {
  name                = "veritygate-redis"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  capacity            = 0
  family              = "C"
  sku_name            = "Basic"
  minimum_tls_version = "1.2"

  tags = { Project = "VerityGate" }
}

# --- Container App Environment ---
resource "azurerm_log_analytics_workspace" "main" {
  name                = "veritygate-logs"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

resource "azurerm_container_app_environment" "main" {
  name                       = "veritygate-env"
  resource_group_name        = azurerm_resource_group.main.name
  location                   = azurerm_resource_group.main.location
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
}

# --- Container App: Backend ---
resource "azurerm_container_app" "backend" {
  name                         = "veritygate-backend"
  container_app_environment_id = azurerm_container_app_environment.main.id
  resource_group_name          = azurerm_resource_group.main.name
  revision_mode                = "Single"

  template {
    min_replicas = 1
    max_replicas = var.max_replicas

    container {
      name   = "backend"
      image  = "${var.acr_login_server}/veritygate-backend:latest"
      cpu    = 0.5
      memory = "1Gi"

      env {
        name  = "DATABASE_URL"
        value = "postgresql+psycopg://veritygate:${var.db_password}@${azurerm_postgresql_flexible_server.main.fqdn}/veritygate?sslmode=require"
      }
      env {
        name  = "REDIS_URL"
        value = "rediss://:${azurerm_redis_cache.main.primary_access_key}@${azurerm_redis_cache.main.hostname}:6380/0"
      }
      env {
        name  = "OTEL_ENABLED"
        value = "true"
      }
      env {
        name  = "OTEL_EXPORTER_ENDPOINT"
        value = var.otel_endpoint
      }
      env {
        name  = "ENVIRONMENT"
        value = "production"
      }
    }
  }

  ingress {
    external_enabled = true
    target_port      = 8009
    traffic_weight {
      percentage      = 100
      latest_revision = true
    }
  }

  tags = { Project = "VerityGate" }
}
