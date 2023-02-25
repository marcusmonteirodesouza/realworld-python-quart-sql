locals {
  default_compute_sa_email = "${data.google_project.project.number}-compute@developer.gserviceaccount.com"

  secret_ids = [
    google_secret_manager_secret.database_uri.secret_id,
    google_secret_manager_secret.secret_key.secret_id,
  ]
}

data "google_project" "project" {
  project_id = var.project_id
}

resource "random_password" "secret_key" {
  length = 64
}

resource "google_secret_manager_secret" "secret_key" {
  project   = var.project_id
  secret_id = "conduit-secret-key"

  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "secret_key" {
  secret      = google_secret_manager_secret.secret_key.id
  secret_data = random_password.secret_key.result
}

resource "google_secret_manager_secret_iam_member" "compute_sa" {
  for_each  = toset(local.secret_ids)
  project   = var.project_id
  secret_id = each.value
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${local.default_compute_sa_email}"
}

resource "google_cloud_run_service" "conduit" {
  project  = var.project_id
  name     = "conduit"
  location = var.region

  template {
    spec {
      containers {
        image = local.conduit_image

        env {
          name  = "JWT_ACCESS_TOKEN_EXPIRES_SECONDS"
          value = "3600"
        }
        env {
          name  = "JWT_ENCODE_ISSUER"
          value = var.domain
        }
        env {
          name = "DATABASE_URI"
          value_from {
            secret_key_ref {
              key  = "latest"
              name = google_secret_manager_secret.database_uri.secret_id
            }
          }
        }
        env {
          name = "SECRET_KEY"
          value_from {
            secret_key_ref {
              key  = "latest"
              name = google_secret_manager_secret.secret_key.secret_id
            }
          }
        }
      }
    }

    metadata {
      annotations = {
        "run.googleapis.com/cloudsql-instances" = module.postgresql_database.instance_connection_name
      }
    }
  }

  metadata {
    annotations = {
      "run.googleapis.com/client-name" = "terraform"
      "run.googleapis.com/ingress"     = "internal-and-cloud-load-balancing"
    }
  }

  depends_on = [
    null_resource.run_migrations,
    google_secret_manager_secret_iam_member.compute_sa
  ]
}

resource "google_cloud_run_service_iam_member" "allow_unauthenticated" {
  location = google_cloud_run_service.conduit.location
  project  = google_cloud_run_service.conduit.project
  service  = google_cloud_run_service.conduit.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
