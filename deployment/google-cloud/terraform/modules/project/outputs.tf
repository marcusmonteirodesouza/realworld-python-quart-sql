output "project_id" {
  value = google_project.project.project_id

  depends_on = [
    google_project_service.enable_apis
  ]
}
