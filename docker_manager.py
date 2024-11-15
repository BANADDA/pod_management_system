# docker_manager.py
import docker
import uuid

client = docker.from_env()


def create_container(user_id, image="python:3.8-slim", command="sleep infinity"):
    """
    Create a new Docker container (pod) for the user.
    """
    container_name = f"pod_{user_id}_{uuid.uuid4()}"
    container = client.containers.run(
        image,
        command,
        name=container_name,
        detach=True,
        labels={"user": user_id},
    )
    return container.id


def stop_container(container_id):
    """
    Stop and remove a Docker container.
    """
    try:
        container = client.containers.get(container_id)
        container.stop()
        container.remove()
        return True
    except docker.errors.NotFound:
        return False
    except docker.errors.APIError as e:
        print(f"Error stopping container {container_id}: {e}")
        return False


def get_container_status(container_id):
    """
    Get the status of a Docker container.
    """
    try:
        container = client.containers.get(container_id)
        return container.status
    except docker.errors.NotFound:
        return "not found"
