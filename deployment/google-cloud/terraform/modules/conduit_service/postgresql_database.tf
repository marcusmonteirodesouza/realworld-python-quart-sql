locals {
  database_name       = "conduit"
  database_port       = 5432
  certs_dir           = abspath("${path.module}/certs")
  migrations_dir      = abspath("${local.top_level_dir}/flyway/sql")
  migrations_dir_sha1 = sha1(join("", [for f in fileset(local.migrations_dir, "*") : filesha1("${local.migrations_dir}/${f}")]))
}

data "google_compute_zones" "available" {
  project = var.project_id
  region  = var.region
  status  = "UP"
}

resource "random_password" "database_user" {
  length  = 32
  special = false
}

module "postgresql_database" {
  source               = "GoogleCloudPlatform/sql-db/google//modules/postgresql"
  version              = "14.0.1"
  availability_type    = "REGIONAL"
  database_version     = "POSTGRES_14"
  db_name              = local.database_name
  enable_default_user  = true
  name                 = local.database_name
  project_id           = var.project_id
  random_instance_name = true
  region               = var.region
  zone                 = data.google_compute_zones.available.names[0]
  tier                 = "db-f1-micro"
  user_name            = random_password.database_user.result

  deletion_protection = false

  ip_configuration = {
    ipv4_enabled        = true
    require_ssl         = true
    private_network     = null
    allocated_ip_range  = null
    authorized_networks = var.postgresql_database_authorized_networks
  }

  create_timeout = "60m"
  delete_timeout = "60m"
  update_timeout = "60m"

}

# Database secrets
resource "google_secret_manager_secret" "database_uri" {
  project   = var.project_id
  secret_id = "conduit-database-uri"

  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "database_uri" {
  secret      = google_secret_manager_secret.database_uri.id
  secret_data = "postgres:///${local.database_name}?host=/cloudsql/${module.postgresql_database.instance_connection_name}&user=${random_password.database_user.result}&password=${module.postgresql_database.generated_user_password}"
}

# Configure SSL/TLS certificates
resource "google_sql_ssl_cert" "postgres_client_cert" {
  project     = var.project_id
  instance    = module.postgresql_database.instance_name
  common_name = "conduit_postgres_common_name"
}

resource "local_sensitive_file" "sslrootcert" {
  content  = google_sql_ssl_cert.postgres_client_cert.server_ca_cert
  filename = "${local.certs_dir}/root.crt"
}

resource "local_sensitive_file" "sslcert" {
  content  = google_sql_ssl_cert.postgres_client_cert.cert
  filename = "${local.certs_dir}/postgresql.crt"
}

resource "local_sensitive_file" "sslkey_pem" {
  content  = google_sql_ssl_cert.postgres_client_cert.private_key
  filename = "${local.certs_dir}/client-key.pem"
}

resource "null_resource" "sslkey" {
  triggers = {
    always_run = "${timestamp()}"
  }

  provisioner "local-exec" {
    command     = "openssl pkcs8 -topk8 -inform PEM -in client-key.pem -outform DER -out postgresql.pk8 -nocrypt"
    working_dir = local.certs_dir
  }

  depends_on = [
    local_sensitive_file.sslkey_pem
  ]
}

# Migrations
resource "null_resource" "run_migrations" {
  triggers = {
    commit_sha = local.commit_sha
  }

  provisioner "local-exec" {
    command = "docker run --rm -v ${local.certs_dir}:/root/.postgresql -v ${local.migrations_dir}:/flyway/sql flyway/flyway -url=jdbc:postgresql://${module.postgresql_database.public_ip_address}:${local.database_port}/${local.database_name}?sslmode=verify-ca -user=${random_password.database_user.result} -password=${module.postgresql_database.generated_user_password} migrate"
  }

  depends_on = [
    local_sensitive_file.sslrootcert,
    local_sensitive_file.sslcert,
    null_resource.sslkey
  ]
}
