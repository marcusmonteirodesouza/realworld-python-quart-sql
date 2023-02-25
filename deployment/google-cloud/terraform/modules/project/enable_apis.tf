locals {
  enable_apis = [
    "artifactregistry.googleapis.com",
    "run.googleapis.com",
    "secretmanager.googleapis.com",
    "sqladmin.googleapis.com",
  ]
}

# Enable APIs
resource "google_project_service" "enable_apis" {
  for_each                   = toset(local.enable_apis)
  project                    = google_project.project.project_id
  service                    = each.value
  disable_dependent_services = true
}
