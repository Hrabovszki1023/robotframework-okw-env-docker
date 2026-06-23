"""Unit tests for DockerProvider using mocked Docker SDK."""

from unittest.mock import MagicMock, patch

import pytest

from okw_env_docker.docker_provider import DockerProvider


@pytest.fixture
def mock_client():
    with patch("okw_env_docker.docker_provider.docker.DockerClient") as mock_cls:
        client = MagicMock()
        mock_cls.return_value = client
        yield client


@pytest.fixture
def provider(mock_client):
    return DockerProvider(base_url="tcp://fake:2375")


@pytest.fixture
def component():
    return {
        "image": "postgres",
        "version": "16",
        "port": 5432,
        "env": {"POSTGRES_PASSWORD": "test"},
        "healthcheck": "pg_isready -U postgres",
    }


def test_create_pulls_image_and_creates_container(provider, mock_client, component):
    mock_container = MagicMock()
    mock_client.containers.create.return_value = mock_container

    cid = provider.create(component)

    mock_client.images.pull.assert_called_once_with("postgres", tag="16")
    mock_client.containers.create.assert_called_once()
    assert cid.startswith("okw-")


def test_create_without_healthcheck(provider, mock_client):
    mock_client.containers.create.return_value = MagicMock()

    provider.create({"image": "redis", "version": "7"})

    call_kwargs = mock_client.containers.create.call_args[1]
    assert call_kwargs["healthcheck"] is None


def test_create_default_version(provider, mock_client):
    mock_client.containers.create.return_value = MagicMock()

    provider.create({"image": "nginx"})

    mock_client.images.pull.assert_called_once_with("nginx", tag="latest")


def test_start(provider, mock_client, component):
    mock_container = MagicMock()
    mock_client.containers.create.return_value = mock_container
    cid = provider.create(component)

    provider.start(cid)

    mock_container.start.assert_called_once()


def test_is_ready_healthy(provider, mock_client, component):
    mock_container = MagicMock()
    mock_container.attrs = {"State": {"Health": {"Status": "healthy"}}}
    mock_client.containers.create.return_value = mock_container
    cid = provider.create(component)

    assert provider.is_ready(cid) is True
    mock_container.reload.assert_called_once()


def test_is_ready_unhealthy(provider, mock_client, component):
    mock_container = MagicMock()
    mock_container.attrs = {"State": {"Health": {"Status": "starting"}}}
    mock_client.containers.create.return_value = mock_container
    cid = provider.create(component)

    assert provider.is_ready(cid) is False


def test_is_ready_no_healthcheck_running(provider, mock_client):
    mock_container = MagicMock()
    mock_container.attrs = {"State": {"Status": "running"}}
    mock_client.containers.create.return_value = mock_container
    cid = provider.create({"image": "redis"})

    assert provider.is_ready(cid) is True


def test_is_ready_no_healthcheck_not_running(provider, mock_client):
    mock_container = MagicMock()
    mock_container.attrs = {"State": {"Status": "created"}}
    mock_client.containers.create.return_value = mock_container
    cid = provider.create({"image": "redis"})

    assert provider.is_ready(cid) is False


def test_get_logs(provider, mock_client, component):
    mock_container = MagicMock()
    mock_container.logs.return_value = b"2024-01-01 LOG: ready"
    mock_client.containers.create.return_value = mock_container
    cid = provider.create(component)

    logs = provider.get_logs(cid)

    assert "ready" in logs


def test_snapshot(provider, mock_client, component):
    mock_container = MagicMock()
    mock_client.containers.create.return_value = mock_container
    cid = provider.create(component)

    tag = provider.snapshot(cid)

    mock_container.commit.assert_called_once_with(repository=f"{cid}-snapshot")
    assert tag == f"{cid}-snapshot"


def test_stop(provider, mock_client, component):
    mock_container = MagicMock()
    mock_client.containers.create.return_value = mock_container
    cid = provider.create(component)

    provider.stop(cid)

    mock_container.stop.assert_called_once_with(timeout=10)


def test_destroy(provider, mock_client, component):
    mock_container = MagicMock()
    mock_client.containers.create.return_value = mock_container
    cid = provider.create(component)

    provider.destroy(cid)

    mock_container.remove.assert_called_once_with(v=True, force=True)


def test_destroy_removes_from_tracking(provider, mock_client, component):
    mock_container = MagicMock()
    mock_client.containers.create.return_value = mock_container
    cid = provider.create(component)
    provider.destroy(cid)

    with pytest.raises(KeyError, match="Unknown container"):
        provider.stop(cid)


def test_unknown_container_raises(provider):
    with pytest.raises(KeyError, match="Unknown container"):
        provider.start("nonexistent")


def test_env_var_fallback():
    with patch("okw_env_docker.docker_provider.docker.DockerClient") as mock_cls, \
         patch.dict("os.environ", {"DOCKER_HOST": "tcp://envhost:2375"}):
        mock_cls.return_value = MagicMock()
        p = DockerProvider()
        p._get_client()
        mock_cls.assert_called_once_with(base_url="tcp://envhost:2375")
