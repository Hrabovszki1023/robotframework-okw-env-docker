# OKW Environment Docker Provider — Specification

## Overview

`robotframework-okw-env-docker` implements the OKW Environment Provider
Contract using Docker Compose as the underlying technology.

## Architecture

```
okw-env (keywords, manager, registry)
    │
    ▼
okw-env-docker (DockerProvider)
    │
    ▼
DockerComposeLibrary (robotframework-docker)
    │
    ▼
Docker Compose CLI → Docker Engine
```

## Component Lifecycle

```
1. ENV_Start PostgresDB
   → Component YAML loaded, merged with overrides, registered

2. ENV_BuildAndRun
   → DockerProvider.create():
     a. Generate docker-compose.yml in temp directory
     b. DockerComposeLibrary(file=..., project_name=okw-<uuid>)
     c. docker_compose_up(no_start=True) → containers created
   → DockerProvider.start():
     d. docker_compose_start() → containers running

3. ENV_WaitForReady PostgresDB
   → DockerProvider.is_ready():
     e. get_exposed_service() → port reachable = ready
   → Polling with timeout from YAML

4. ... test execution ...

5. ENV_Stop
   → DockerProvider.get_logs() → logs into Robot report
   → DockerProvider.stop() → docker_compose_stop()
   → DockerProvider.destroy() → docker_compose_down(volumes=True)
   → Temp directory and compose file cleaned up
```

## Isolation Model

Each `ENV_BuildAndRun` creates a unique Docker Compose project:

- Project name: `okw-<random-8-hex>`
- Own network (Docker Compose default)
- Own volumes
- Own port mappings

Multiple tests running in parallel get separate projects with
no shared state.

## Snapshot Model

`ENV_SnapshotOnFail` and `ENV_CreateImage` use `docker commit`
to freeze each container as a Docker image:

- Tag: `<project>-snapshot-<container_id_prefix>`
- Images persist after container destruction
- Can be started manually for post-mortem analysis:
  `docker run -it <snapshot_tag> /bin/bash`
