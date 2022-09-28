from config import get_config
from kubernetes import client
from configparser import ConfigParser

config: ConfigParser = get_config()

DEPLOYMENT_NAME: str = config["debug-deployment"].get("debug-deployment-name", "nginx-deployment")

# Creates default object
def create_deployment() -> client.V1Deployment:

    # Configure default Pod template container
    container = client.V1Container(
        name="nginx",
        image="nginx:1.15.4",
        ports=[client.V1ContainerPort(container_port=80)],
        resources=client.V1ResourceRequirements(
            requests={
                "cpu": config["debug-deployment"].get(
                    "debug-deployment-limits-cpu-requests", "100m"
                ),
                "memory": config["debug-deployment"].get(
                    "debug-deployment-limits-memory-requests", "200Mi"
                ),
            },
            limits={
                "cpu": config["debug-deployment"].get("debug-deployment-limits-cpu-limits", "500m"),
                "memory": config["debug-deployment"].get(
                    "debug-deployment-limits-memory-limits", "500Mi"
                ),
            },
        ),
    )

    # Create and configure a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": "nginx"}),
        spec=client.V1PodSpec(containers=[container]),
    )

    # Create the specification of deployment
    spec = client.V1DeploymentSpec(
        replicas=2, template=template, selector={"matchLabels": {"app": "nginx"}}
    )

    # Instantiate the deployment object
    deployment = client.V1Deployment(
        api_version="apps/v1",
        kind="debug-deployment",
        metadata=client.V1ObjectMeta(name=DEPLOYMENT_NAME),
        spec=spec,
    )

    return deployment

