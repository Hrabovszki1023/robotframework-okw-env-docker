"""Integration test against a real Docker host.

Requires: Docker Engine at tcp://192.168.1.123:2375
Run with: pytest tests/test_integration_docker.py -v -s
"""

import pytest

from okw_env_docker.docker_provider import DockerProvider

DOCKER_HOST = "tcp://192.168.1.123:2375"


@pytest.fixture
def provider():
    return DockerProvider(base_url=DOCKER_HOST)


@pytest.fixture
def redis_component():
    return {
        "image": "redis",
        "version": "7",
        "port": 6379,
        "healthcheck": "redis-cli ping",
    }


@pytest.fixture
def redis_container(provider, redis_component):
    cid = provider.create(redis_component)
    yield cid
    try:
        provider.stop(cid)
    except Exception:
        pass
    try:
        provider.destroy(cid)
    except Exception:
        pass


def test_full_lifecycle(provider, redis_component, redis_container):
    cid = redis_container
    print(f"\n  Container: {cid}")

    # Start
    provider.start(cid)
    print("  Started.")

    # Wait for ready (poll)
    import time
    for i in range(30):
        if provider.is_ready(cid):
            print(f"  Ready after {i + 1} poll(s).")
            break
        time.sleep(1)
    else:
        pytest.fail("Container not ready after 30s")

    # Logs
    logs = provider.get_logs(cid)
    print(f"  Logs ({len(logs)} chars): {logs[:200]}")
    assert len(logs) > 0

    # Snapshot
    tag = provider.snapshot(cid)
    print(f"  Snapshot: {tag}")
    assert "snapshot" in tag

    # Stop
    provider.stop(cid)
    print("  Stopped.")
