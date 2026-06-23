*** Settings ***
Documentation    Integrationstest: Redis-Container Lifecycle über Docker Engine API.
Library          okw_env_docker.library.OkwEnvDockerLibrary
...              components_dir=${CURDIR}${/}components
Test Teardown    Run Keywords    ENV_SnapshotOnFail    ENV_Stop

*** Test Cases ***
Redis Container Lifecycle
    [Documentation]    Startet einen Redis-Container, wartet auf Ready, stoppt und räumt auf.
    ENV_Start          Redis
    ENV_BuildAndRun
    ENV_WaitForReady   Redis
    Log                Redis ist bereit — Testlogik würde hier starten.
    ENV_Stop
