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

    The library connects to a Docker Engine via REST API.
    Configure the host in one of three ways (in priority order):

    | 1. | Constructor parameter ``docker_host`` |
    | 2. | Environment variable ``DOCKER_HOST`` |
    | 3. | Default: ``unix:///var/run/docker.sock`` |

    Example for a remote Docker host on Proxmox:

    | ``docker_host=tcp://192.168.1.123:2375`` |

    = Installation =

    | ``pip install robotframework-okw-env-docker`` |

    That's it. One ``pip install``, one IP address, test environments ready.

    = Usage =

    | **Settings** |
    | Library | OkwEnvDockerLibrary | components_dir=components | docker_host=tcp://192.168.1.123:2375 |

    | **Test Cases** |
    | Webshop mit Datenbank |
    |     | ENV_Start       | PostgresDB |
    |     | ENV_BuildAndRun |            |
    |     | ENV_WaitForReady | PostgresDB |
    |     | # ... test steps ... |        |
    |     | [Teardown] | Run Keywords | ENV_SnapshotOnFail | ENV_Stop |

    = Component YAML =

    Each environment component is defined in a YAML file:

    | ``PostgresDB.yaml`` |
    | provider: docker |
    | image: postgres |
    | version: "17" |
    | port: 5432 |
    | env: |
    |     POSTGRES_DB: testdb |
    | healthcheck: "pg_isready -U postgres" |
    | timeout: 30s |

    = Signal vs. NOISE =

    | *Signal* | *NOISE (hidden)* |
    | ``ENV_Start PostgresDB`` | Docker API calls, image pull, container config |
    | ``ENV_WaitForReady PostgresDB`` | Health check polling, timeout logic |
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
