import os
import time
from caus import SimpleCAUS
from config import get_config
from kubernetes import client, config as kubernetes_config
from elasticity import Elasticity
from prometheusclient import PrometheusMonitor

config = get_config()

DEPLOYMENT_NAME = config['deployment'].get('deployment-name', 'nginx-deployment')

# Creates an object from a file with the given path or creates default object -> TODO
def create_deployment_object_from_file(fullpath: str="") -> client.V1Deployment :

    #check if a path was given -> if it wasnt: create default object
    if not fullpath:
        # Configure default Pod template container
        container = client.V1Container(
            name="nginx",
            image="nginx:1.15.4",
            ports=[client.V1ContainerPort(container_port=80)],
            resources=client.V1ResourceRequirements(
                requests={
                    "cpu": config['deployment'].get('deployment-limits-cpu-requests', "100m"),
                    "memory": config['deployment'].get('deployment-limits-memory-requests', "200Mi")},
                limits={
                    "cpu": config['deployment'].get('deployment-limits-cpu-limits', "500m"),
                    "memory": config['deployment'].get('deployment-limits-memory-limits', "500Mi")},
            ),
        )

        # Create and configure a spec section
        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels={"app": "nginx"}),
            spec=client.V1PodSpec(containers=[container]),
        )

        # Create the specification of deployment
        spec = client.V1DeploymentSpec(
            replicas=2, template=template, selector={
                "matchLabels":
                {"app": "nginx"}})

        # Instantiate the deployment object
        deployment = client.V1Deployment(
            api_version="apps/v1",
            kind="Deployment",
            metadata=client.V1ObjectMeta(name=DEPLOYMENT_NAME),
            spec=spec,
        )
    else:
        #TODO read deployment configuration from path (might be out of scope)
        pass

    return deployment

#create deployment from a given deployment object and api
def create_deployment(api, deployment):
    try:
        resp = api.create_namespaced_deployment(body=deployment, namespace="default")

        print("[INFO] deployment `nginx-deployment` created.")
        print(f"{'NAMESPACE':<20} {'NAME':<20} {'REVISION':<20} {'IMAGE':<20}")
        print(f"{resp.metadata.namespace:<20} {resp.metadata.name:<20} {resp.metadata.generation:<20} {resp.spec.template.spec.containers[0].image:<20}")
    except Exception as ex:
        print("Creating deployment failed")
        print(f"Caught exception: {format(ex)}")
        print("Continuing with stack deployment")

def update_deployment(api, deployment):
    api.patch_namespaced_deployment(name=DEPLOYMENT_NAME, namespace="default", body=deployment)
    print("[INFO] deployment's container image updated.")

# TODO: Unused. Delete?
def list_pods(api):
    print("Listing pods with their IPs:")
    print(f"{'IP':<20} {'Namespace':<20} {'Name':<20}")
    for i in api.list_pod_for_all_namespaces(watch=False).items:
        print(f"{i.status.pod_ip:<20} {i.metadata.namespace:<20} {i.metadata.name:<20}")

def scale_deployment_object(deployment, scalingobject, elasticityobject, publishingRate):
    desiredReplicas, bufferedReplicas = scalingobject.calcReplicas(publishingRate,deployment.spec.replicas)
    print(f"Computed desired replicas: {desiredReplicas} and buffered: {bufferedReplicas}")
    deployment.spec.replicas = desiredReplicas
    elasticityobject.elasticityBufferedReplicas = bufferedReplicas
    return deployment

def main():
    print("Load kube config...")
    try:
        kubernetes_config.load_incluster_config()
    except kubernetes_config.ConfigException:
        print("didnt find incluster config, loading file manually...")
        kubernetes_config.load_kube_config(config_file=os.environ.get('KUBECONFIG','k8s-cluster3-admin.conf'))

    #setup deployment, prometheus monitoring, scaling method etc
    #initialize necessary apis
    core_api = client.CoreV1Api()
    apis_api = client.AppsV1Api()
    deployment = create_deployment_object_from_file()
    myMonitor = PrometheusMonitor()
    myElasticity = Elasticity(
            capacity          = config.getint('elasticity', 'elastic-capacity',           fallback = 8),
            min_replicas      = config.getint('elasticity', 'elastic-min-replicas',       fallback = 1),
            max_replicas      = config.getint('elasticity', 'elastic-max-replicas',       fallback = 10),
            buffer_threshold  = config.getfloat('elasticity', 'elastic-buffer-threshold', fallback = 50.0),
            initial_buffer    = config.getint('elasticity', 'elastic-initial-buffer',     fallback = 1),
            buffered_replicas = config.getint('elasticity', 'elastic-buffered-replicas',  fallback = 1)
            )
    #setup scaling method, e.g: CAUS, ML-CAUS or others
    myCaus: CAUS = SimpleCAUS(myElasticity)
    print(f"start {deployment.spec.replicas} replicas")

    #TODO update loop
    while True:
        deployment = scale_deployment_object(deployment, myCaus, myElasticity, float(myMonitor.getMessagesInPerSec_OneMinuteRate()))
        time.sleep(15)

if __name__ == "__main__":
    main()
