FROM python:3.10-slim AS build-env

ARG POETRY_VERSION=1.3.2
ARG PORT

# Copy files
COPY . /app
WORKDIR /app

# Install production dependencies
RUN pip install --upgrade pip && \
    pip install poetry==$POETRY_VERSION && \
    poetry install --without dev

# Runtime
FROM python:3.10-slim
COPY --from=build-env /app /app
WORKDIR /app
CMD /app/.venv/bin/hypercorn conduit:app --bind "0.0.0.0:$PORT" --access-logfile "-" --error-logfile "-"
