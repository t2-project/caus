import os
import time
from caus import CAUS, SimpleCAUS
from config import get_config
from kubernetes import client, config as kubernetes_config
from elasticity import Elasticity
from prometheusclient import PrometheusMonitor
from configparser import ConfigParser

config: ConfigParser = get_config()

DEPLOYMENT_NAME: str = config["deployment"].get("deployment-name", "nginx-deployment")

# Creates default object
def create_deployment() -> client.V1Deployment:

    # Configure default Pod template container
    container = client.V1Container(
        name="nginx",
        image="nginx:1.15.4",
        ports=[client.V1ContainerPort(container_port=80)],
        resources=client.V1ResourceRequirements(
            requests={
                "cpu": config["deployment"].get(
                    "deployment-limits-cpu-requests", "100m"
                ),
                "memory": config["deployment"].get(
                    "deployment-limits-memory-requests", "200Mi"
                ),
            },
            limits={
                "cpu": config["deployment"].get("deployment-limits-cpu-limits", "500m"),
                "memory": config["deployment"].get(
                    "deployment-limits-memory-limits", "500Mi"
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
        kind="Deployment",
        metadata=client.V1ObjectMeta(name=DEPLOYMENT_NAME),
        spec=spec,
    )

    return deployment


def scale_deployment(
    deployment: client.V1Deployment,
    caus: CAUS,
    elasticity: Elasticity,
    publishing_rate: float,
) -> client.V1Deployment:
    desired_replicas, buffered_replicas = caus.calculate_replicas(
        publishing_rate, deployment.spec.replicas
    )
    print(
        f"Computed desired replicas: {desired_replicas} and buffered: {buffered_replicas}"
    )
    deployment.spec.replicas = desired_replicas
    elasticity.buffered_replicas = buffered_replicas
    return deployment


def main():
    print("Load kube config...")
    try:
        kubernetes_config.load_incluster_config()
    except kubernetes_config.ConfigException:
        print("didnt find incluster config, loading file manually...")
        kubernetes_config.load_kube_config(
            config_file=os.environ.get("KUBECONFIG", "k8s-cluster3-admin.conf")
        )

    # setup deployment, prometheus monitoring, scaling method etc
    # initialize necessary apis
    core_api = client.CoreV1Api()
    apis_api = client.AppsV1Api()
    deployment: client.V1Deployment = create_deployment()
    monitor = PrometheusMonitor()
    elasticity = Elasticity(
        capacity=config.getint("elasticity", "elastic-capacity", fallback=8),
        min_replicas=config.getint("elasticity", "elastic-min-replicas", fallback=1),
        max_replicas=config.getint("elasticity", "elastic-max-replicas", fallback=10),
        buffer_threshold=config.getfloat(
            "elasticity", "elastic-buffer-threshold", fallback=50.0
        ),
        initial_buffer=config.getint(
            "elasticity", "elastic-initial-buffer", fallback=1
        ),
        buffered_replicas=config.getint(
            "elasticity", "elastic-buffered-replicas", fallback=1
        ),
    )
    # setup scaling method, e.g: CAUS, ML-CAUS or others
    caus: CAUS = SimpleCAUS(elasticity)
    print(f"start {deployment.spec.replicas} replicas")

    timeout: float = config.getfloat("caus", "update-rate", fallback=10.0)
    # TODO update loop
    while True:
        deployment = scale_deployment(
            deployment,
            caus,
            elasticity,
            float(monitor.getMessagesInPerSec_OneMinuteRate()),
        )
        time.sleep(timeout)


if __name__ == "__main__":
    main()
