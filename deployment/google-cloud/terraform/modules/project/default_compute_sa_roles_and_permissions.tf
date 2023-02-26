locals {
  default_compute_sa_email = "${google_project.project.number}-compute@developer.gserviceaccount.com"

  default_compute_sa_roles = [
    "roles/cloudsql.client"
  ]
}

resource "google_project_iam_member" "defaul_compute_sa" {
  for_each = toset(local.default_compute_sa_roles)
  project  = google_project.project.project_id
  role     = each.value
  member   = "serviceAccount:${local.default_compute_sa_email}"
}
