*** Settings ***
Documentation    Integrationstest: YAML-Daten als $MEM{} Variablen verfügbar.
Library          okw_env_docker.library.OkwEnvDockerLibrary
...              components_dir=${CURDIR}${/}components
Test Teardown    Run Keywords    ENV_SnapshotOnFail    ENV_Stop

*** Test Cases ***
Umgebungsdaten Per MEM Verfuegbar
    [Documentation]    Nach ENV_BuildAndRun sind alle YAML-Daten als Variablen zugreifbar.
    ENV_Start          PostgresShop
    ENV_BuildAndRun
    ENV_WaitForReady   PostgresShop

    Log    Image: ${PostgresShop.image}
    Log    Version: ${PostgresShop.version}
    Log    Port: ${PostgresShop.port}
    Log    DB-Name: ${PostgresShop.env.POSTGRES_DB}
    Log    Passwort: ${PostgresShop.env.POSTGRES_PASSWORD}
    Log    Container-ID: ${PostgresShop.ID}

    Should Be Equal    ${PostgresShop.image}               postgres
    Should Be Equal    ${PostgresShop.version}              16
    Should Be Equal    ${PostgresShop.port}                 5433
    Should Be Equal    ${PostgresShop.env.POSTGRES_DB}      shop
    Should Be Equal    ${PostgresShop.env.POSTGRES_PASSWORD}    shop_test
    Should Not Be Empty    ${PostgresShop.ID}

    ENV_Stop
