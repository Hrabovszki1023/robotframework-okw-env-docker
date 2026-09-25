# robotframework-okw-env-docker

[![PyPI](https://img.shields.io/pypi/v/robotframework-okw-env-docker)](https://pypi.org/project/robotframework-okw-env-docker/)
[![Python](https://img.shields.io/pypi/pyversions/robotframework-okw-env-docker)](https://pypi.org/project/robotframework-okw-env-docker/)
[![License](https://img.shields.io/badge/License-OKW_Community-orange.svg)](LICENSE)

Docker-Compose-Provider für [okw-env](https://github.com/Hrabovszki1023/robotframework-okw-env).

> **English version:** [README.md](README.md)

## Was

Implementiert den OKW-Environment-Provider-Vertrag mit Docker Compose.
Generiert `docker-compose.yml` aus YAML-Komponentendefinitionen und
verwaltet den gesamten Container-Lebenszyklus (Erstellen, Starten,
Health-Check, Logs, Snapshot, Stoppen, Zerstören).

## Warum — Signal vs. NOISE

Docker-Compose-Syntax ist NOISE. Der Tester schreibt nur:

```robot
ENV_Start        PostgresDB
ENV_BuildAndRun
ENV_WaitForReady PostgresDB
```

Das Framework generiert die Compose-Datei, startet den Container
und pollt den Health-Check. Kein Docker-Wissen im Testcode nötig.

## Installation

```bash
pip install robotframework-okw-env-docker
```

Dies installiert automatisch `robotframework-okw-env` (Core) und
`robotframework-docker` (Docker-Compose-Engine).

## Komponenten-YAML

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

## Minimalbeispiel

```robot
*** Settings ***
Library    okw_env.library.OkwEnvLibrary    components_dir=components    WITH NAME    ENV

*** Test Cases ***
Datenbank ist erreichbar
    ENV_Start        PostgresDB
    ENV_BuildAndRun
    ENV_WaitForReady    PostgresDB
    Log    PostgresDB ist bereit fuer Tests.
    [Teardown]    ENV_Stop
```

## Architektur

```
okw-env (Keywords, YAML-Loader, Registry)
    │
    ▼
okw-env-docker (diese Bibliothek)
    │
    ▼
DockerComposeLibrary (robotframework-docker)
    │
    ▼
Docker Compose CLI → Docker Engine
```

## Lauffähige Beispiele

[okw-examples/env-docker/](https://github.com/Hrabovszki1023/okw-examples/tree/main/env-docker/) — PostgreSQL, Redis, Full-Stack-Umgebungen.

## Handbuch

[OKW4Robot Handbuch](https://hrabovszki1023.github.io/okw-examples/) — Schritt-für-Schritt-Anleitung.

## Dokumentation

- [CONTRACT.md](docs/CONTRACT.md) — Wie dieser Provider den Vertrag implementiert
- [SPECIFICATION.md](docs/SPECIFICATION.md) — Lebenszyklus, Isolation, Snapshot-Modell
- [KEYWORDS.md](docs/KEYWORDS.md) — Keyword-Referenz mit Beispielen
