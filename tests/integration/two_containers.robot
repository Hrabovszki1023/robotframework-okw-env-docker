*** Settings ***
Documentation    Integrationstest: Redis + PostgreSQL parallel auf einem Docker-Host.
Library          okw_env_docker.library.OkwEnvDockerLibrary
...              components_dir=${CURDIR}${/}components
Test Teardown    Run Keywords    ENV_SnapshotOnFail    ENV_Stop

*** Test Cases ***
Zwei Container Parallel
    [Documentation]    Startet Redis und PostgreSQL, wartet bis beide bereit sind.
    ENV_Start          Redis
    ENV_Start          PostgresDB
    ENV_BuildAndRun
    ENV_WaitForReady   Redis
    ENV_WaitForReady   PostgresDB
    Log                Beide Container bereit — Testlogik würde hier starten.
    ENV_Stop
