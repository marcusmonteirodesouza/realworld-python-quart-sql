resource "google_compute_region_network_endpoint_group" "serverless_neg" {
  project               = var.project_id
  name                  = "conduit-neg"
  region                = var.region
  network_endpoint_type = "SERVERLESS"
  cloud_run {
    service = var.conduit_service_name
  }
}

module "https_load_balancer" {
  source         = "GoogleCloudPlatform/lb-http/google//modules/serverless_negs"
  version        = "~> 6.2.0"
  name           = "https-load-balancer"
  project        = var.project_id
  address        = var.ip_address
  create_address = false

  ssl                             = true
  managed_ssl_certificate_domains = [var.domain]
  https_redirect                  = true

  backends = {
    default = {
      description = null
      groups = [
        {
          group = google_compute_region_network_endpoint_group.serverless_neg.id
        }
      ]
      enable_cdn              = false
      security_policy         = null
      custom_request_headers  = null
      custom_response_headers = null

      iap_config = {
        enable               = false
        oauth2_client_id     = null
        oauth2_client_secret = null
      }
      log_config = {
        enable      = false
        sample_rate = null
      }
    }
  }
}
