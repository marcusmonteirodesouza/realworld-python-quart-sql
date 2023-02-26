locals {
  top_level_dir                 = "${path.module}/../../../../.."
  commit_sha                    = data.external.git.result["sha"]
  artifact_registry_docker_host = "${var.region}-docker.pkg.dev"
  conduit_image                 = "${local.artifact_registry_docker_host}/${var.project_id}/${google_artifact_registry_repository.conduit.repository_id}/conduit:${local.commit_sha}"
  port                          = 8080
}

data "external" "git" {
  program = [
    "git",
    "log",
    "--pretty=format:{ \"sha\": \"%H\" }",
    "-1",
    "HEAD"
  ]
}
