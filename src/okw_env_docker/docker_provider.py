"""Docker Compose provider for OKW environments.

Uses robotframework-docker (DockerComposeLibrary) as the underlying engine.
"""

from __future__ import annotations

import subprocess
import tempfile
import uuid
from pathlib import Path

import yaml
from DockerComposeLibrary import DockerComposeLibrary

from okw_env.provider_base import OkwEnvProviderBase


class DockerProvider(OkwEnvProviderBase):
    """Provisions environment components via Docker Compose.

    Generates a docker-compose.yml from the OKW component definition
    and delegates all operations to DockerComposeLibrary.
    """

    def __init__(self):
        self._projects: dict[str, _DockerProject] = {}

    def create(self, component: dict) -> str:
        """Generate a docker-compose.yml and create containers (without starting)."""
        project_name = f"okw-{uuid.uuid4().hex[:8]}"
        compose_dir = Path(tempfile.mkdtemp(prefix=f"okw_env_{project_name}_"))
        compose_file = compose_dir / "docker-compose.yml"

        service_name = component.get("_name", project_name)
        compose_content = self._build_compose(component, service_name)
        compose_file.write_text(
            yaml.dump(compose_content, default_flow_style=False),
            encoding="utf-8",
        )

        lib = DockerComposeLibrary(
            file=str(compose_file),
            project_name=project_name,
            project_directory=str(compose_dir),
        )
        lib.docker_compose_up(no_start=True)

        project = _DockerProject(
            name=project_name,
            service_name=service_name,
            compose_dir=compose_dir,
            compose_file=compose_file,
            library=lib,
            component=component,
        )
        self._projects[project_name] = project
        return project_name

    def start(self, component_id: str) -> None:
        project = self._require_project(component_id)
        project.library.docker_compose_start()

    def is_ready(self, component_id: str) -> bool:
        project = self._require_project(component_id)
        try:
            service = project.library.get_exposed_service(
                project.service_name,
                project.component.get("port", 0),
            )
            return service is not None
        except Exception:
            return False

    def get_logs(self, component_id: str) -> str:
        project = self._require_project(component_id)
        return project.library.docker_compose_logs()

    def snapshot(self, component_id: str) -> str:
        project = self._require_project(component_id)
        result = subprocess.run(
            ["docker", "compose", "-p", project.name,
             "-f", str(project.compose_file), "ps", "-q"],
            check=True, capture_output=True, text=True,
        )
        snapshot_ids = []
        for container_id in result.stdout.strip().splitlines():
            snapshot_tag = f"{project.name}-snapshot-{container_id[:12]}"
            subprocess.run(
                ["docker", "commit", container_id, snapshot_tag],
                check=True, capture_output=True,
            )
            snapshot_ids.append(snapshot_tag)
        return ",".join(snapshot_ids)

    def stop(self, component_id: str) -> None:
        project = self._require_project(component_id)
        project.library.docker_compose_stop()

    def destroy(self, component_id: str) -> None:
        project = self._require_project(component_id)
        project.library.docker_compose_down(volumes=True, remove_orphans=True)
        del self._projects[component_id]

    def _require_project(self, component_id: str) -> _DockerProject:
        if component_id not in self._projects:
            raise KeyError(f"Unknown project '{component_id}'. Active: {list(self._projects.keys())}")
        return self._projects[component_id]

    @staticmethod
    def _build_compose(component: dict, service_name: str) -> dict:
        """Build a docker-compose.yml dict from a component definition."""
        image = component.get("image", "")
        version = component.get("version", "latest")
        port = component.get("port")
        env = component.get("env", {})
        healthcheck = component.get("healthcheck")
        depends_on = component.get("depends_on", [])

        service: dict = {
            "image": f"{image}:{version}",
        }
        if port:
            service["ports"] = [f"{port}:{port}"]
        if env:
            service["environment"] = env
        if healthcheck:
            service["healthcheck"] = {
                "test": ["CMD-SHELL", healthcheck],
                "interval": "5s",
                "timeout": "3s",
                "retries": 10,
            }
        if depends_on:
            service["depends_on"] = depends_on

        return {
            "services": {
                service_name: service,
            },
        }


class _DockerProject:
    """Internal state for a running Docker Compose project."""

    def __init__(self, name: str, service_name: str, compose_dir: Path,
                 compose_file: Path, library: DockerComposeLibrary, component: dict):
        self.name = name
        self.service_name = service_name
        self.compose_dir = compose_dir
        self.compose_file = compose_file
        self.library = library
        self.component = component
