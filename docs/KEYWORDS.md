# Keyword Reference — OKW Environment Docker Provider

> Keywords are defined in `okw-env` (the core library).
> This provider implements the backend for Docker Compose.
>
> See [okw-env CONTRACT.md](http://192.168.1.130:3000/Hrabovszki1023/robotframework-okw-env)
> for the full keyword contract.

## Keywords

| Keyword | Arguments | Purpose |
|---|---|---|
| `ENV_Start` | `name`, `**overrides` | Register a Docker component from YAML |
| `ENV_BuildAndRun` | — | Generate docker-compose.yml, create and start all containers |
| `ENV_WaitForReady` | `name`, `timeout` (optional) | Poll until container port is reachable |
| `ENV_Stop` | — | Log output, stop and remove all containers + volumes |
| `ENV_CreateImage` | `name` | `docker commit` all containers for reuse |
| `ENV_StartFromImage` | `image_name`, `fallback_keyword` | Start from snapshot or run fallback |
| `ENV_SnapshotOnFail` | — | `docker commit` all containers on test failure |

## Usage

```robot
*** Settings ***
Library    okw_env.library.OkwEnvLibrary    components_dir=components    WITH NAME    ENV

*** Test Cases ***
Database Is Reachable
    ENV_Start        PostgresDB
    ENV_BuildAndRun
    ENV_WaitForReady    PostgresDB
    Log    PostgresDB is ready.
    [Teardown]    ENV_Stop

Snapshot On Failure
    ENV_Start        PostgresDB
    ENV_Start        WebShop
    ENV_BuildAndRun
    ENV_WaitForReady    PostgresDB
    ENV_WaitForReady    WebShop
    # ... test steps ...
    [Teardown]    Run Keywords    ENV_SnapshotOnFail    ENV_Stop
```
