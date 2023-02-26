variable "project_id" {
  type        = string
  description = "The project ID."
}

variable "project_number" {
  type        = string
  description = "The numeric identifier of the project."
}

variable "region" {
  type        = string
  description = "The default Google Cloud region in which resources will be created at."
}

variable "domain" {
  type        = string
  description = "Your application's domain name."
}

variable "postgresql_database_authorized_networks" {
  type        = list(map(string))
  description = "List of mapped public networks authorized to access to the PostgreSQL database instances."
}
