resource "google_artifact_registry_repository" "conduit" {
  project       = var.project_id
  location      = var.region
  repository_id = "conduit"
  description   = "Conduit application docker repository"
  format        = "DOCKER"
}

resource "null_resource" "docker_build_and_push" {
  triggers = {
    conduit_image = local.conduit_image
  }

  provisioner "local-exec" {
    command     = "docker build --build-arg PORT=${local.port} --tag ${local.conduit_image} . && gcloud auth configure-docker ${local.artifact_registry_docker_host} --quiet && docker push ${local.conduit_image}"
    working_dir = local.top_level_dir
  }
}
