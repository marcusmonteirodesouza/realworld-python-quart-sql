module "project" {
  source = "./modules/project"

  project_id      = var.project_id
  org_id          = var.org_id
  billing_account = var.billing_account
}

module "conduit_service" {
  source = "./modules/conduit_service"

  project_id                              = module.project.project_id
  project_number                          = module.project.project_number
  region                                  = var.region
  domain                                  = var.domain
  postgresql_database_authorized_networks = var.postgresql_database_authorized_networks
}

resource "google_compute_global_address" "https_load_balancer" {
  project = module.project.project_id
  name    = "https-load-balancer-address"
}

module "https_load_balancer" {
  source = "./modules/https_load_balancer"

  project_id           = module.project.project_id
  region               = var.region
  ip_address           = google_compute_global_address.https_load_balancer.address
  domain               = var.domain
  conduit_service_name = module.conduit_service.name
}
