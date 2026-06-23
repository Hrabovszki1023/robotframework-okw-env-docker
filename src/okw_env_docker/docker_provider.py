"""Docker provider for OKW environments.

Uses the Docker Python SDK (docker-py) to communicate directly with the
Docker Engine API. No local Docker CLI installation required.
"""

from __future__ import annotations

import os
import uuid

import docker

from okw_env.provider_base import OkwEnvProviderBase


class DockerProvider(OkwEnvProviderBase):
    """Provisions environment components as Docker containers via the Engine API."""

    def __init__(self, base_url: str | None = None):
        self._base_url = base_url or os.environ.get("DOCKER_HOST", "unix:///var/run/docker.sock")
        self._client: docker.DockerClient | None = None
        self._containers: dict[str, docker.models.containers.Container] = {}

    def _get_client(self) -> docker.DockerClient:
        if self._client is None:
            self._client = docker.DockerClient(base_url=self._base_url)
        return self._client

    def create(self, component: dict) -> str:
        """Pull image and create a container (without starting)."""
        image = component.get("image", "")
        version = component.get("version", "latest")
        full_image = f"{image}:{version}"
        port = component.get("port")
        env = component.get("env", {})
        healthcheck_cmd = component.get("healthcheck")
        name = f"okw-{uuid.uuid4().hex[:8]}"

        self._get_client().images.pull(image, tag=version)

        ports = {f"{port}/tcp": port} if port else {}
        env_list = [f"{k}={v}" for k, v in env.items()]

        healthcheck = None
        if healthcheck_cmd:
            healthcheck = docker.types.Healthcheck(
                test=["CMD-SHELL", healthcheck_cmd],
                interval=5_000_000_000,
                timeout=3_000_000_000,
                retries=10,
            )

        container = self._get_client().containers.create(
            full_image,
            name=name,
            ports=ports,
            environment=env_list,
            healthcheck=healthcheck,
            detach=True,
        )
        self._containers[name] = container
        return name

    def start(self, component_id: str) -> None:
        container = self._require_container(component_id)
        container.start()

    def is_ready(self, component_id: str) -> bool:
        container = self._require_container(component_id)
        container.reload()
        state = container.attrs.get("State", {})

        health = state.get("Health", {})
        if health:
            return health.get("Status") == "healthy"

        return state.get("Status") == "running"

    def get_logs(self, component_id: str) -> str:
        container = self._require_container(component_id)
        return container.logs().decode("utf-8", errors="replace")

    def snapshot(self, component_id: str) -> str:
        container = self._require_container(component_id)
        snapshot_tag = f"{component_id}-snapshot"
        container.commit(repository=snapshot_tag)
        return snapshot_tag

    def stop(self, component_id: str) -> None:
        container = self._require_container(component_id)
        container.stop(timeout=10)

    def destroy(self, component_id: str) -> None:
        container = self._require_container(component_id)
        container.remove(v=True, force=True)
        del self._containers[component_id]

    def _require_container(self, component_id: str):
        if component_id not in self._containers:
            raise KeyError(f"Unknown container '{component_id}'. Active: {list(self._containers.keys())}")
        return self._containers[component_id]
