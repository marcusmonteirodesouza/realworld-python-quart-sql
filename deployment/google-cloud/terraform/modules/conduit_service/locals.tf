locals {
  top_level_dir                 = "${path.module}/../../../../.."
  dir_sha1                      = sha1(join("", [for f in fileset(local.top_level_dir, "*") : filesha1("${local.top_level_dir}/${f}")]))
  artifact_registry_docker_host = "${var.region}-docker.pkg.dev"
  conduit_image                 = "${local.artifact_registry_docker_host}/${var.project_id}/${google_artifact_registry_repository.conduit.repository_id}/conduit:${local.dir_sha1}"
  port                          = 8080
}
