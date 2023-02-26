# ![RealWorld Example App](logo.png)

> ### [Quart](https://quart.palletsprojects.com/) codebase containing real world examples (CRUD, auth, advanced patterns, etc) that adheres to the [RealWorld](https://github.com/gothinkster/realworld) spec and API.

### [Demo](https://demo.realworld.io/)&nbsp;&nbsp;&nbsp;&nbsp;[RealWorld](https://github.com/gothinkster/realworld)

This codebase was created to demonstrate a fully fledged backend application built with **[Quart](https://quart.palletsprojects.com/)** including CRUD operations, authentication, routing, pagination, and more.

We've gone to great lengths to adhere to the **[Quart](https://quart.palletsprojects.com/)** community styleguides & best practices.

For more information on how to this works with other frontends/backends, head over to the [RealWorld](https://github.com/gothinkster/realworld) repo.

# How it works

# Getting started

## Pre-Requisites

1. Install [Docker](https://docs.docker.com/get-docker/).
1. Install [GNU Make](https://www.gnu.org/software/make/). It is used to run scripts.
1. Install [Poetry](https://python-poetry.org/).
1. Run [poetry install](https://python-poetry.org/docs/cli/#install).

## Running

To start the server, you can run:

```commandline
make run
```

It will stand up a [PostgreSQL container](https://hub.docker.com/_/postgres) using [Docker Compose](https://docs.docker.com/compose/) and run the [Quart](http://pgjones.gitlab.io/quart/) application using [Poetry](https://python-poetry.org/docs/cli/#run).

## Testing

The approach I followed is this:

1. I only test the external API.
1. I don't mock things that are under my control, such as databases.

I believe that doing so allow for:

1. More opportunities for refactoring. Testing only the external API and not any of the internals allowed me more freedom to move things around, provided the tests keep green.
1. More confidence that the application actually works.

To run the tests, you can run:

```commandline
make test
```

It uses [pytest](https://docs.pytest.org/) with [pytest-asyncio](https://pytest-asyncio.readthedocs.io) as the test runner.

You can also run the API tests from the [realworld repository](https://github.com/gothinkster/realworld/tree/main/api) by running:

```commandline
make api-test
```

It requires that you install [Node.js](https://nodejs.org/en/download/).

# Deployment

## [Google Cloud](https://cloud.google.com/)

### System Architecture

![System Architecture Diagram](./images/google-cloud-system-architecture-diagram.svg)

### Components

1. [HTTPS Load Balancer](https://cloud.google.com/load-balancing/docs/https).
1. A [Cloud Run](https://cloud.google.com/run/docs/overview/what-is-cloud-run) service running the application as a [Docker container](https://www.docker.com/resources/what-container/#:~:text=A%20Docker%20container%20image%20is,tools%2C%20system%20libraries%20and%20settings.).
1. A [Cloud SQL instance running PostgreSQL](https://cloud.google.com/sql/docs/postgres/features).

### Deployment

1. Install [terraform](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli).
1. Install [openssl](https://www.openssl.org/). The deployment generates and uses certificates to [connect with the Cloud SQL using SSL/TLS](https://cloud.google.com/sql/docs/postgres/configure-ssl-instance) and run migrations using [flyway](https://github.com/flyway/flyway-docker).
1. Have registered [domain](https://domains.google/intl/en_ca/learn/web-terms-101/). You will need to [connect your domain](https://cloud.google.com/load-balancing/docs/https/setup-global-ext-https-serverless#update_dns) to set up HTTPS.
1. `cd` into [deployment/google-cloud/terraform](deployment/google-cloud/terraform).
1. Run `terraform init`.
1. Run `terraform apply`.
