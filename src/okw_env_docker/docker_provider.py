"""Docker Compose provider for OKW environments."""

from __future__ import annotations

import json
import subprocess
import tempfile
import uuid
from pathlib import Path

import yaml

from okw_env.provider_base import OkwEnvProviderBase


class DockerProvider(OkwEnvProviderBase):
    """Provisions environment components via Docker Compose."""

    def __init__(self):
        self._projects: dict[str, _DockerProject] = {}

    def create(self, component: dict) -> str:
        """Generate a docker-compose.yml and create containers (without starting)."""
        project_name = f"okw-{uuid.uuid4().hex[:8]}"
        compose_dir = Path(tempfile.mkdtemp(prefix=f"okw_env_{project_name}_"))
        compose_file = compose_dir / "docker-compose.yml"

        compose_content = self._build_compose(component, project_name)
        compose_file.write_text(yaml.dump(compose_content, default_flow_style=False), encoding="utf-8")

        self._docker_compose(compose_dir, project_name, ["create"])

        project = _DockerProject(
            name=project_name,
            compose_dir=compose_dir,
            component=component,
        )
        self._projects[project_name] = project
        return project_name

    def start(self, component_id: str) -> None:
        project = self._require_project(component_id)
        self._docker_compose(project.compose_dir, project.name, ["start"])

    def is_ready(self, component_id: str) -> bool:
        project = self._require_project(component_id)
        result = self._docker_compose(
            project.compose_dir, project.name,
            ["ps", "--format", "json"],
            capture=True,
        )
        if not result.stdout.strip():
            return False
        for line in result.stdout.strip().splitlines():
            container = json.loads(line)
            health = container.get("Health", "")
            state = container.get("State", "")
            if health and health != "healthy":
                return False
            if state != "running":
                return False
        return True

    def get_logs(self, component_id: str) -> str:
        project = self._require_project(component_id)
        result = self._docker_compose(
            project.compose_dir, project.name,
            ["logs", "--no-color"],
            capture=True,
        )
        return result.stdout

    def snapshot(self, component_id: str) -> str:
        project = self._require_project(component_id)
        result = self._docker_compose(
            project.compose_dir, project.name,
            ["ps", "-q"],
            capture=True,
        )
        snapshot_ids = []
        for container_id in result.stdout.strip().splitlines():
            snapshot_tag = f"{project.name}-snapshot-{container_id[:12]}"
            subprocess.run(
                ["docker", "commit", container_id, snapshot_tag],
                check=True,
                capture_output=True,
            )
            snapshot_ids.append(snapshot_tag)
        return ",".join(snapshot_ids)

    def stop(self, component_id: str) -> None:
        project = self._require_project(component_id)
        self._docker_compose(project.compose_dir, project.name, ["stop"])

    def destroy(self, component_id: str) -> None:
        project = self._require_project(component_id)
        self._docker_compose(project.compose_dir, project.name, ["down", "-v", "--remove-orphans"])
        del self._projects[component_id]

    def _require_project(self, component_id: str) -> _DockerProject:
        if component_id not in self._projects:
            raise KeyError(f"Unknown project '{component_id}'. Active: {list(self._projects.keys())}")
        return self._projects[component_id]

    @staticmethod
    def _build_compose(component: dict, project_name: str) -> dict:
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
            "version": "3.8",
            "services": {
                project_name: service,
            },
        }

    @staticmethod
    def _docker_compose(compose_dir: Path, project_name: str, args: list[str], capture: bool = False):
        cmd = ["docker", "compose", "-p", project_name, "-f", str(compose_dir / "docker-compose.yml")] + args
        return subprocess.run(
            cmd,
            check=True,
            capture_output=capture,
            text=True,
        )


class _DockerProject:
    """Internal state for a running Docker Compose project."""

    def __init__(self, name: str, compose_dir: Path, component: dict):
        self.name = name
        self.compose_dir = compose_dir
        self.component = component
