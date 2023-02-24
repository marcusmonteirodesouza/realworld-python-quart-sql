# ![RealWorld Example App](logo.png)

> ### [Quart](https://quart.palletsprojects.com/) codebase containing real world examples (CRUD, auth, advanced patterns, etc) that adheres to the [RealWorld](https://github.com/gothinkster/realworld) spec and API.

### [Demo](https://demo.realworld.io/)&nbsp;&nbsp;&nbsp;&nbsp;[RealWorld](https://github.com/gothinkster/realworld)

This codebase was created to demonstrate a fully fledged backend application built with **[Quart](https://quart.palletsprojects.com/)** including CRUD operations, authentication, routing, pagination, and more.

We've gone to great lengths to adhere to the **[Quart](https://quart.palletsprojects.com/)** community styleguides & best practices.

For more information on how to this works with other frontends/backends, head over to the [RealWorld](https://github.com/gothinkster/realworld) repo.

# How it works

## System Overview

# Getting started

## Pre-Requisites

1. Install [Docker](https://docs.docker.com/get-docker/).
2. Install [Poetry](https://python-poetry.org/).
3. Run [poetry install](https://python-poetry.org/docs/cli/#install).

## Running

To start the server, you can run:

```commandline
make run
```

It will stand up a [PostgreSQL container](https://hub.docker.com/_/postgres) using [Docker Compose](https://docs.docker.com/compose/) and run the [Quart](http://pgjones.gitlab.io/quart/) application using [Poetry](https://python-poetry.org/docs/cli/#run).

## Testing

The approach I followed is this:

1. I only test the external API.
2. I don't mock things that are under my control, such as databases.

I believe that doing so allow for:

1. Greater opportunities for refactoring. Testing only the external API and not any of the internals allowed me more freedom to move things around, provided the tests still kept green.
2. More confidence that the application actually works.

To run the tests, you can run:

```commandline
make test
```

It uses [pytest](https://docs.pytest.org/) with [pytest-asyncio](https://pytest-asyncio.readthedocs.io) as the test runner.

You can also run the API tests from the [realworld repository](https://github.com/gothinkster/realworld/tree/main/api) by running:

```commandline
make api-test
```

It will require that you install [Node.js](https://nodejs.org/en/download/).

# Deployment

## [Google Cloud](https://cloud.google.com/)

### Bootstrap

### Deployment
