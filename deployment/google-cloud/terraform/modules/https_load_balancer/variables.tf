variable "project_id" {
  type        = string
  description = "The project ID."
}

variable "region" {
  type        = string
  description = "The default Google Cloud region in which resources will be created at."
}

variable "ip_address" {
  type        = string
  description = "The HTTPS Load Balancer's IP address."
}

variable "domain" {
  type        = string
  description = "Your application's domain name."
}

variable "conduit_service_name" {
  type        = string
  description = "The Conduit Cloud Run service name."
}
