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
| `create(component)` | `client.images.pull()` + `client.containers.create()` |
| `start(component_id)` | `container.start()` |
| `is_ready(component_id)` | `container.reload()` → check `Health.Status == "healthy"` or `Status == "running"` |
| `get_logs(component_id)` | `container.logs()` |
| `snapshot(component_id)` | `container.commit(repository=...)` |
| `stop(component_id)` | `container.stop(timeout=10)` |
| `destroy(component_id)` | `container.remove(v=True, force=True)` |

## Underlying Library

Uses the [Docker SDK for Python](https://docker-py.readthedocs.io/)
(`docker.DockerClient`) to communicate directly with the Docker Engine
API via REST. No local Docker CLI installation required.

### Connection

The `DockerProvider` constructor accepts an optional `base_url` parameter.
Resolution order:

1. Explicit `base_url` argument
2. `DOCKER_HOST` environment variable
3. Default: `unix:///var/run/docker.sock`

Example for remote Docker host: `tcp://192.168.1.123:2375`

## Component YAML — Docker-specific Keys

| Key | Required | Example | Purpose |
|---|---|---|---|
| `provider` | YES | `docker` | Selects this provider |
| `image` | YES | `postgres` | Docker image name |
| `version` | NO | `17` | Image tag (default: `latest`) |
| `port` | NO | `5432` | Exposed port (host:container same) |
| `env` | NO | `{POSTGRES_DB: test}` | Environment variables |
| `healthcheck` | NO | `pg_isready -U postgres` | Health check command |
| `timeout` | NO | `30s` | Ready-timeout |

## Health Check Logic

If the component YAML defines a `healthcheck`, the provider configures
a Docker health check on the container. `is_ready()` then checks:

1. If `Health` is present in container state → `healthy` = ready
2. Otherwise → `running` = ready

## Snapshot

`container.commit()` creates a Docker image from the running container.
The snapshot tag format is `<component_id>-snapshot`.
