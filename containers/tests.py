import asyncio

import pytest
from asgiref.sync import sync_to_async
from channels.testing import WebsocketCommunicator
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from docker.errors import DockerException
from rest_framework.test import APIClient

from containers.consumers import TerminalConsumer
from containers.docker_client import get_docker_client
from containers.models import AllowedImage, PortReservation, Service
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


@pytest.fixture(scope="session")
def docker_client():
    """Cliente Docker compartido para todos los tests."""
    if not DOCKER_AVAILABLE:
        pytest.skip("Docker no esta disponible para las pruebas de contenedores.")
    return get_docker_client()


@pytest.fixture(autouse=True)
def clean_docker(docker_client):
    """Ensure no test containers are left running before each test."""
    for c in docker_client.containers.list(all=True):
        if "test" in c.name:
            c.remove(force=True)


@pytest.mark.django_db
def test_port_reservation_is_unique():
    """Comprueba que dos reservas consecutivas no devuelven el mismo puerto."""
    first = PortReservation.reserve_free_port()
    second = PortReservation.reserve_free_port()
    assert first != second

    PortReservation.objects.filter(port__in=[first, second]).delete()


@pytest.mark.django_db
@pytest.mark.skipif(not DOCKER_AVAILABLE, reason="Docker no disponible para pruebas de contenedores")
def test_container_lifecycle(django_user_model, docker_client):
    """Ejecucion completa: run -> stop -> remove y liberacion de puerto."""
    user = django_user_model.objects.create_user("ci_user", "ci@local", "pass")
    svc = Service.objects.create(owner=user, name="nginx-ci", image="nginx:latest")

    run_container(svc, enqueue=False)
    svc.refresh_from_db()
    assert svc.status == "running"
    assert docker_client.containers.get(svc.container_id).status == "running"

    stop_container(svc)
    svc.refresh_from_db()
    assert svc.status == "stopped"

    assigned_port = svc.assigned_port
    remove_container(svc)
    svc.refresh_from_db()
    assert svc.status == "removed"
    assert svc.container_id is None
    assert not PortReservation.objects.filter(port__in=[assigned_port]).exists()


from django.contrib.auth.models import Group


@pytest.fixture
def student_user(django_user_model):
    """Usuario con rol de 'estudiante' para pruebas de API."""
    group, _ = Group.objects.get_or_create(name="Student")
    user = django_user_model.objects.create_user("student1", "s@test.com", "pass")
    user.groups.add(group)
    return user


@pytest.fixture
def api_client(student_user):
    """Cliente de API autenticado como 'student_user'."""
    client = APIClient()
    client.force_authenticate(user=student_user)
    return client


@pytest.mark.django_db
class TestServiceCreation:
    """Grupo de tests para la creacion de servicios via API."""

    def test_create_with_default_image(self, api_client):
        AllowedImage.objects.create(name="nginx", tag="latest")
        url = reverse("service-list")
        data = {"name": "test-nginx", "image": "nginx:latest", "mode": "default"}

        response = api_client.post(url, data)

        assert response.status_code == 201
        assert Service.objects.filter(name="test-nginx").exists()

    def test_create_with_dockerfile(self, api_client):
        url = reverse("service-list")
        dockerfile = SimpleUploadedFile(
            "Dockerfile", b"FROM nginx:alpine\nCOPY . /usr/share/nginx/html"
        )
        code = SimpleUploadedFile("app.zip", b"dummy zip content")
        data = {
            "name": "test-dockerfile",
            "mode": "custom",
            "dockerfile": dockerfile,
            "code": code,
        }

        response = api_client.post(url, data, format="multipart")
        assert response.status_code == 201
        svc = Service.objects.get(name="test-dockerfile")
        assert svc.dockerfile is not None

    def test_create_with_compose(self, api_client):
        url = reverse("service-list")
        compose = SimpleUploadedFile(
            "docker-compose.yml", b"services:\n  web:\n    image: nginx:alpine"
        )
        data = {"name": "test-compose", "mode": "custom", "compose": compose}
        response = api_client.post(url, data, format="multipart")
        assert response.status_code == 201
        svc = Service.objects.get(name="test-compose")
        assert svc.compose is not None

    def test_create_fails_with_dockerfile_and_compose(self, api_client):
        url = reverse("service-list")
        dockerfile = SimpleUploadedFile("Dockerfile", b"FROM nginx")
        compose = SimpleUploadedFile("docker-compose.yml", b"services:\n  web:\n    image: nginx")
        data = {
            "name": "test-fail",
            "mode": "custom",
            "dockerfile": dockerfile,
            "compose": compose,
        }
        response = api_client.post(url, data, format="multipart")
        assert response.status_code == 400

    def test_create_fails_in_custom_mode_without_files(self, api_client):
        url = reverse("service-list")
        data = {"name": "test-fail-custom", "mode": "custom"}
        response = api_client.post(url, data)
        assert response.status_code == 400

    @pytest.mark.skipif(not DOCKER_AVAILABLE, reason="Docker no disponible")
    def test_get_service_logs(self, api_client, student_user):
        svc = Service.objects.create(
            owner=student_user, name="test-logs", image="hello-world"
        )
        try:
            run_container(svc, enqueue=False)
            url = reverse("service-logs", kwargs={"pk": svc.pk})
            response = api_client.get(url)
            assert response.status_code == 200
            assert "Hello from Docker!" in response.content.decode()
        finally:
            remove_container(svc)


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
@pytest.mark.skipif(not DOCKER_AVAILABLE, reason="Docker not available")
async def test_terminal_websocket(student_user):
    """Tests the interactive terminal via WebSocket."""
    svc = await sync_to_async(Service.objects.create)(
        owner=student_user, name="test-terminal", image="alpine:latest"
    )
    try:
        # Keep the container alive for the test
        await sync_to_async(run_container)(svc, command=["sleep", "60"], enqueue=False)
        await sync_to_async(svc.refresh_from_db)()
        assert svc.status == "running"

        communicator = WebsocketCommunicator(
            TerminalConsumer.as_asgi(), f"/ws/terminal/{svc.pk}/"
        )
        communicator.scope["user"] = student_user
        communicator.scope["url_route"] = {"kwargs": {"service_id": svc.pk}}

        connected, _ = await communicator.connect()
        assert connected

        # Send a command and check for its output
        await communicator.send_to(text_data="echo 'hello from terminal'\n")
        await asyncio.sleep(0.1)  # Give the shell a moment to process
        response = ""
        try:
            while True:
                output = await asyncio.wait_for(communicator.receive_output(), timeout=2)
                if output["type"] == "websocket.close":
                    break
                content = output.get("text", "") or output.get("bytes", b"").decode()
                response += content
                if "hello from terminal" in response:
                    break
        except asyncio.TimeoutError:
            pass

        await communicator.disconnect()
        assert "hello from terminal" in response
    finally:
        await sync_to_async(remove_container)(svc)
