*** Settings ***
Documentation    Integrationstest: Zwei Postgres-Instanzen aus gemeinsamer Basis via extends.
Library          okw_env_docker.library.OkwEnvDockerLibrary
...              components_dir=${CURDIR}${/}components
Test Teardown    Run Keywords    ENV_SnapshotOnFail    ENV_Stop

*** Test Cases ***
Zwei Datenbanken Aus Gemeinsamer Basis
    [Documentation]    PostgresShop und PostgresPayment erben von PostgresBase.
    ...                Selbes Image, selber Host — nur DB-Name und Port unterscheiden sich.
    ENV_Start          PostgresShop
    ENV_Start          PostgresPayment
    ENV_BuildAndRun
    ENV_WaitForReady   PostgresShop
    ENV_WaitForReady   PostgresPayment
    Log                Beide Datenbanken bereit — gleiche Basis, unterschiedliche Daten.
    ENV_Stop
