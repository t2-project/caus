import os
import time
from caus import CAUS, SimpleCAUS
from config import get_config
from kubernetes import client, config as kubernetes_config
from elasticity import Elasticity
from prometheusclient import PrometheusMonitor
from configparser import ConfigParser
from debug_controller import create_deployment

config: ConfigParser = get_config()

def scale_deployment(
    deployment: client.V1Deployment,
    caus: CAUS,
    elasticity: Elasticity,
    publishing_rate: float,
):
    desired_replicas, buffered_replicas = caus.calculate_replicas(
        publishing_rate, deployment.spec.replicas
    )
    print(
        f"Computed desired replicas: {desired_replicas} and buffered: {buffered_replicas}"
    )
    deployment.spec.replicas = desired_replicas
    elasticity.buffered_replicas = buffered_replicas


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
        scale_deployment(
            deployment,
            caus,
            elasticity,
            float(monitor.get_current_metric_value()),
        )
        time.sleep(timeout)


if __name__ == "__main__":
    main()
