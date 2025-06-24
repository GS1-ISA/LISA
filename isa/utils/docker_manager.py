import docker
from docker.models.containers import Container
from typing import Dict, Any, Optional

class DockerManager:
    """
    Manages Docker container lifecycle for sandboxed browser environments.
    Handles creation, execution, and cleanup of Docker containers.
    """

    def __init__(self, image_name: str = "selenium/standalone-chrome", network_mode: str = "bridge"):
        """
        Initializes the DockerManager.

        Args:
            image_name (str): The Docker image to use for browser environments.
            network_mode (str): The network mode for the containers (e.g., "bridge", "host", "none").
        """
        self.client = docker.from_env()
        self.image_name = image_name
        self.network_mode = network_mode
        self._ensure_image_pulled()

    def _ensure_image_pulled(self):
        """Ensures the specified Docker image is available locally."""
        try:
            self.client.images.get(self.image_name)
            print(f"Docker image '{self.image_name}' already exists locally.")
        except docker.errors.ImageNotFound:
            print(f"Pulling Docker image '{self.image_name}'...")
            self.client.images.pull(self.image_name)
            print(f"Docker image '{self.image_name}' pulled successfully.")
        except Exception as e:
            print(f"Error ensuring Docker image: {e}")
            raise

    def create_browser_container(self, name: Optional[str] = None, ports: Optional[Dict[str, Any]] = None,
                                 environment: Optional[Dict[str, str]] = None,
                                 resource_limits: Optional[Dict[str, Any]] = None) -> Container:
        """
        Creates and starts a Docker container for a browser environment.

        Args:
            name (Optional[str]): The name for the container. If None, Docker generates one.
            ports (Optional[Dict[str, Any]]): Port mappings, e.g., {"4444/tcp": 4444}.
            environment (Optional[Dict[str, str]]): Environment variables for the container.
            resource_limits (Optional[Dict[str, Any]]): Resource limits (e.g., {"memory": "512m", "cpus": 0.5}).

        Returns:
            Container: The created and running Docker container object.
        """
        print(f"Creating Docker container from image '{self.image_name}'...")
        container = self.client.containers.run(
            self.image_name,
            detach=True,
            name=name,
            ports=ports,
            environment=environment,
            network_mode=self.network_mode,
            # user="selenium", # Run as non-root user if image supports it
            # mem_limit=resource_limits.get("memory"),
            # cpu_period=int(100000 * resource_limits.get("cpus")) if resource_limits and "cpus" in resource_limits else None,
            # cpu_quota=int(100000 * resource_limits.get("cpus")) if resource_limits and "cpus" in resource_limits else None,
            # auto_remove=True # Automatically remove container when it exits
        )
        print(f"Container '{container.name}' ({container.id}) created and started.")
        return container

    def stop_and_remove_container(self, container: Container):
        """
        Stops and removes a Docker container.

        Args:
            container (Container): The Docker container object to stop and remove.
        """
        print(f"Stopping container '{container.name}' ({container.id})...")
        container.stop()
        print(f"Removing container '{container.name}' ({container.id})...")
        container.remove()
        print(f"Container '{container.name}' removed.")

    def execute_command_in_container(self, container: Container, command: str, **kwargs) -> tuple[int, str]:
        """
        Executes a command inside a running container.

        Args:
            container (Container): The Docker container object.
            command (str): The command to execute.
            **kwargs: Additional arguments for `exec_run` (e.g., `stream=True`, `demux=True`).

        Returns:
            tuple[int, str]: A tuple containing the exit code and the command output.
        """
        print(f"Executing command '{command}' in container '{container.name}'...")
        exit_code, output = container.exec_run(command, **kwargs)
        return exit_code, output.decode('utf-8')

if __name__ == "__main__":
    # Example Usage:
    docker_manager = DockerManager()
    container = None
    try:
        # Create a container with specific ports and resource limits
        container = docker_manager.create_browser_container(
            name="isa-browser-env",
            ports={"4444/tcp": 4444, "7900/tcp": 7900}, # Selenium default ports
            resource_limits={"memory": "1g", "cpus": 1.0}
        )

        # You would typically connect to the browser inside the container here
        # For example, using Selenium WebDriver connected to http://localhost:4444/wd/hub

        # Simulate some interaction (e.g., checking if chrome is running)
        exit_code, output = docker_manager.execute_command_in_container(container, "ps aux | grep chrome")
        print(f"Command exit code: {exit_code}")
        print(f"Command output:\n{output}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if container:
            docker_manager.stop_and_remove_container(container)