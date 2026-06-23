# OKW Environment Docker Provider — Contract Compliance

> The authoritative contract is defined in
> [robotframework-okw-env/docs/CONTRACT.md](http://192.168.1.130:3000/Hrabovszki1023/robotframework-okw-env).
> This document describes how `okw-env-docker` implements it.

## Provider Registration

```toml
[project.entry-points."okw_env.providers"]
docker = "okw_env_docker:DockerProvider"
```

## Method Implementation

| Contract Method | Docker Implementation |
|---|---|
| `create(component)` | Generate `docker-compose.yml`, call `DockerComposeLibrary.docker_compose_up(no_start=True)` |
| `start(component_id)` | `DockerComposeLibrary.docker_compose_start()` |
| `is_ready(component_id)` | `DockerComposeLibrary.get_exposed_service()` — service reachable = ready |
| `get_logs(component_id)` | `DockerComposeLibrary.docker_compose_logs()` |
| `snapshot(component_id)` | `docker commit` per container (via subprocess — no library equivalent) |
| `stop(component_id)` | `DockerComposeLibrary.docker_compose_stop()` |
| `destroy(component_id)` | `DockerComposeLibrary.docker_compose_down(volumes=True)` |

## Underlying Library

Uses [robotframework-docker](https://github.com/vogoltsov/robotframework-docker)
(`DockerComposeLibrary`) as the engine for all Docker Compose operations.

## Component YAML — Docker-specific Keys

| Key | Required | Example | Purpose |
|---|---|---|---|
| `provider` | YES | `docker` | Selects this provider |
| `image` | YES | `postgres` | Docker image name |
| `version` | NO | `17` | Image tag (default: `latest`) |
| `port` | NO | `5432` | Exposed port |
| `env` | NO | `{POSTGRES_DB: test}` | Environment variables |
| `healthcheck` | NO | `pg_isready -U postgres` | Health check command |
| `timeout` | NO | `30s` | Ready-timeout |
| `depends_on` | NO | `[PostgresDB]` | Service dependencies |

## Generated docker-compose.yml

From:

```yaml
PostgresDB:
  provider: docker
  image: postgres
  version: "17"
  port: 5432
  env:
    POSTGRES_DB: testdb
  healthcheck: "pg_isready -U postgres"
```

Generated:

```yaml
services:
  PostgresDB:
    image: postgres:17
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: testdb
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 3s
      retries: 10
```

## Snapshot

Snapshot uses `docker commit` to create an image from each running
container. The snapshot tag format is `<project>-snapshot-<container_id>`.

This is the only operation that bypasses `DockerComposeLibrary`
(no library equivalent for `docker commit`).
