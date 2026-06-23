"""OKW Environment Docker Library – Robot Framework keywords for Docker-based environments."""

from __future__ import annotations

from robot.api.deco import library

from okw_env.library import OkwEnvLibrary

from .docker_provider import DockerProvider


@library(scope="GLOBAL")
class OkwEnvDockerLibrary(OkwEnvLibrary):
    """OKW Environment provisioning for Docker.

    = Zero-Install Architecture =

    This library communicates with the Docker Engine API directly via
    the [https://docker-py.readthedocs.io/|Docker SDK for Python].
    **No Docker CLI, no Docker Desktop, no docker-compose installation
    required** — only ``pip install robotframework-okw-env-docker``
    and a reachable Docker host.

    This dramatically reduces installation NOISE: every machine that can
    run Python and reach a Docker host over the network can provision
    test environments — no admin rights, no platform-specific installers.

    = Connection =

    The Docker host is configured **per component in the YAML file** via
    the ``docker_host`` key. This is intentional: the connection target is
    a property of the test environment, not of the test machine. A test
    suite can mix components on different Docker hosts — or even different
    providers (Docker + Proxmox) — without any local configuration.

    Resolution order for ``docker_host``:

    | 1. | ``docker_host`` key in component YAML (recommended) |
    | 2. | ``docker_host`` parameter on the Library constructor (fallback) |
    | 3. | Environment variable ``DOCKER_HOST`` |
    | 4. | Default: ``unix:///var/run/docker.sock`` (Linux only) |

    *Why YAML and not a Library parameter?*

    The test machine (Windows laptop, Linux CI runner) should not determine
    where Docker runs. A developer on Windows and a CI runner on Linux use
    the same YAML — the connection target stays the same. No ``DOCKER_HOST``
    environment variable, no platform-specific config, no surprises.

    = Installation =

    | ``pip install robotframework-okw-env-docker`` |

    That's it. One ``pip install``, one IP address in the YAML, test environments ready.

    = Usage =

    | **Settings** |
    | Library | OkwEnvDockerLibrary | components_dir=components |

    | **Test Cases** |
    | Webshop mit Datenbank |
    |     | ENV_Start       | PostgresDB |
    |     | ENV_BuildAndRun |            |
    |     | ENV_WaitForReady | PostgresDB |
    |     | # ... test steps ... |        |
    |     | [Teardown] | Run Keywords | ENV_SnapshotOnFail | ENV_Stop |

    = Component YAML =

    Each environment component is defined in a YAML file.
    The ``docker_host`` tells the provider where to connect:

    | ``PostgresDB.yaml`` |
    | provider: docker |
    | docker_host: tcp://192.168.1.123:2375 |
    | image: postgres |
    | version: "17" |
    | port: 5432 |
    | env: |
    |     POSTGRES_DB: testdb |
    | healthcheck: "pg_isready -U postgres" |
    | timeout: 30s |

    = Environment Variables via $MEM{} =

    After ``ENV_BuildAndRun``, **all YAML keys** are published as Robot
    Framework test variables using dot-notation. This bridges environment
    provisioning with test keywords — the test knows where to connect
    without hardcoding anything.

    | *Variable* | *Source* | *Example value* |
    | ``${PostgresDB.image}`` | YAML key | ``postgres`` |
    | ``${PostgresDB.version}`` | YAML key | ``17`` |
    | ``${PostgresDB.port}`` | YAML key | ``5432`` |
    | ``${PostgresDB.env.POSTGRES_DB}`` | YAML nested key | ``testdb`` |
    | ``${PostgresDB.env.POSTGRES_PASSWORD}`` | YAML nested key | ``secret`` |
    | ``${PostgresDB.docker_host}`` | YAML key | ``tcp://192.168.1.123:2375`` |
    | ``${PostgresDB.ID}`` | Runtime (container ID) | ``okw-3df2dcc8`` |

    Usage in test:

    | ENV_Start       | PostgresDB |
    | ENV_BuildAndRun |            |
    | ENV_WaitForReady | PostgresDB |
    | Log | DB name: ${PostgresDB.env.POSTGRES_DB} |
    | Log | Port: ${PostgresDB.port} |

    In OKW GUI/API keywords, use ``$MEM{}`` syntax:

    | SetValue | DB_Host | $MEM{PostgresDB.docker_host} |
    | SetValue | DB_Name | $MEM{PostgresDB.env.POSTGRES_DB} |

    *Design rationale:* The connection data lives in the YAML — not in
    environment variables, not in CI config, not hardcoded in the test.
    The same test runs against any Docker host by changing one YAML file.

    = Signal vs. NOISE =

    | *Signal* | *NOISE (hidden)* |
    | ``ENV_Start PostgresDB`` | Docker API calls, image pull, container config |
    | ``ENV_WaitForReady PostgresDB`` | Health check polling, timeout logic |
    | ``${PostgresDB.env.POSTGRES_DB}`` | YAML parsing, variable publishing |
    | ``ENV_Stop`` | Container stop, remove, volume cleanup |

    The test case reads like a specification. The infrastructure is invisible.

    = Runnable Examples =

    See [https://github.com/Hrabovszki1023/okw-examples|okw-examples]
    for complete working test suites.
    """

    ROBOT_LIBRARY_SCOPE = "GLOBAL"

    def __init__(self, components_dir: str | None = None, docker_host: str | None = None):
        super().__init__(components_dir=components_dir)
        provider = DockerProvider(base_url=docker_host)
        self._manager.set_provider(provider)
