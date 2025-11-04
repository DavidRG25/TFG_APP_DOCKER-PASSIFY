import pytest
from docker.errors import DockerException

from containers.docker_client import get_docker_client
from containers.models import PortReservation, Service
from containers.services import remove_container, run_container, stop_container


def _docker_available() -> bool:
    client = get_docker_client()
    if client is None:
        return False
    try:
        client.ping()
        return True
    except DockerException:
        return False


DOCKER_AVAILABLE = _docker_available()


# ───────────────────────── FIXTURES ──────────────────────────
@pytest.fixture(scope="session")
def docker_client():
    """Cliente Docker compartido para todos los tests."""
    if not DOCKER_AVAILABLE:
        pytest.skip("Docker no está disponible para las pruebas de contenedores.")
    return get_docker_client()


# ───────────────────────── TESTS ─────────────────────────────
@pytest.mark.django_db
def test_port_reservation_is_unique():
    """
    reserve_free_port() nunca debe devolver el mismo puerto
    mientras la reserva exista en BD.
    """
    first = PortReservation.reserve_free_port()
    second = PortReservation.reserve_free_port()
    assert first != second

    # limpieza
    PortReservation.objects.filter(port__in=[first, second]).delete()


@pytest.mark.django_db
@pytest.mark.skipif(not DOCKER_AVAILABLE, reason="Docker no disponible para pruebas de contenedores")
def test_container_lifecycle(django_user_model, docker_client):
    """
    run → stop → remove debe reflejarse tanto en Docker
    como en los campos del modelo Service.
    """
    user = django_user_model.objects.create_user("ci_user", "ci@local", "pass")
    svc  = Service.objects.create(owner=user, name="nginx-ci", image="nginx:latest")

    # run
    run_container(svc)
    assert svc.status == "running"
    assert docker_client.containers.get(svc.container_id).status == "running"

    # stop
    stop_container(svc)
    assert svc.status == "stopped"

    # remove
    remove_container(svc)
    assert svc.status == "removed"
    assert svc.container_id is None

    # Asegúrate de que el puerto se liberó
    assert not PortReservation.objects.filter(port=svc.assigned_port).exists()