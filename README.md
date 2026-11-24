# robotframework-okw-env-docker

[![PyPI](https://img.shields.io/pypi/v/robotframework-okw-env-docker)](https://pypi.org/project/robotframework-okw-env-docker/)
[![Python](https://img.shields.io/pypi/pyversions/robotframework-okw-env-docker)](https://pypi.org/project/robotframework-okw-env-docker/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

Docker Compose provider for [okw-env](https://github.com/Hrabovszki1023/robotframework-okw-env).

> Deutsche Version: [README.de.md](README.de.md)

## What

Implements the OKW Environment Provider Contract using Docker Compose.
Generates `docker-compose.yml` from YAML component definitions and
manages the full container lifecycle (create, start, health check,
logs, snapshot, stop, destroy).

## Why — Signal vs. NOISE

Docker Compose syntax is NOISE. The tester only writes:

```robot
ENV_Start        PostgresDB
ENV_BuildAndRun
ENV_WaitForReady PostgresDB
```

The framework generates the Compose file, starts the container,
and polls the health check. No Docker knowledge required in test code.

## Install

```bash
pip install robotframework-okw-env-docker
```

This automatically installs `robotframework-okw-env` (core) and
`robotframework-docker` (Docker Compose engine).

## Component YAML

```yaml
PostgresDB:
  provider: docker
  image: postgres
  version: "17"
  port: 5432
  env:
    POSTGRES_DB: testdb
    POSTGRES_PASSWORD: testpass
  healthcheck: "pg_isready -U postgres"
  timeout: 30s
```

## Minimal Example

```robot
*** Settings ***
Library    okw_env.library.OkwEnvLibrary    components_dir=components    WITH NAME    ENV

*** Test Cases ***
Database Is Reachable
    ENV_Start        PostgresDB
    ENV_BuildAndRun
    ENV_WaitForReady    PostgresDB
    Log    PostgresDB is ready for testing.
    [Teardown]    ENV_Stop
```

## Architecture

```
okw-env (keywords, YAML loader, registry)
    │
    ▼
okw-env-docker (this library)
    │
    ▼
DockerComposeLibrary (robotframework-docker)
    │
    ▼
Docker Compose CLI → Docker Engine
```

## Runnable Examples

[okw-examples/env-docker/](https://github.com/Hrabovszki1023/okw-examples/tree/main/env-docker/) — PostgreSQL, Redis, full-stack environments.

## Handbuch

[OKW4Robot Handbuch](https://hrabovszki1023.github.io/okw-examples/) — step-by-step guide (German).

## Documentation

- [CONTRACT.md](docs/CONTRACT.md) — How this provider implements the contract
- [SPECIFICATION.md](docs/SPECIFICATION.md) — Lifecycle, isolation, snapshot model
- [KEYWORDS.md](docs/KEYWORDS.md) — Keyword reference with examples
