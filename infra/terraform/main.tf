terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 4.51.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# VPC Network
resource "google_compute_network" "vpc_network" {
  name = "ai-ops-network"
}

# Cloud SQL (Postgres)
resource "google_sql_database_instance" "master" {
  name             = "ai-ops-db-instance"
  database_version = "POSTGRES_15"
  region           = var.region
  settings {
    tier = "db-f1-micro"
  }
}

resource "google_sql_database" "database" {
  name     = "aiops_platform"
  instance = google_sql_database_instance.master.name
}

# Cloud Run Services
# Note: Actual image deployment usually handled via CI/CD, this defines the service shell.

resource "google_cloud_run_service" "backend_core" {
  name     = "backend-core"
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/backend-core:latest"
        env {
          name = "DATABASE_URL"
          value = "postgres://..." # Logic to retrieve from secret manager
        }
      }
    }
  }
}

resource "google_cloud_run_service" "backend_agent" {
  name     = "backend-agent"
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/backend-agent:latest"
        env {
           name = "OLLAMA_BASE_URL" # In cloud, this needs to point to an LLM service
           value = "http://llm-service:11434"
        }
      }
    }
  }
}

resource "google_cloud_run_service" "frontend" {
  name     = "frontend"
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/frontend:latest"
      }
    }
  }
}
