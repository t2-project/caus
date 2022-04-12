import os
from caus import CAUS
from kubernetes import client, config


DEPLOYMENT_NAME = "nginx-deployment"

# Creates an object from a file with the given path or creates default object
def create_deployment_object_from_file(fullpath: str=""):

    #check if a path was given -> if it wasnt: create default object
    if not fullpath:
        # Configurate default Pod template container
        container = client.V1Container(
            name="nginx",
            image="nginx:1.15.4",
            ports=[client.V1ContainerPort(container_port=80)],
            resources=client.V1ResourceRequirements(
                requests={"cpu": "100m", "memory": "200Mi"},
                limits={"cpu": "500m", "memory": "500Mi"},
            ),
        )

        # Create and configure a spec section
        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels={"app": "nginx"}),
            spec=client.V1PodSpec(containers=[container]),
        )

        # Create the specification of deployment
        spec = client.V1DeploymentSpec(
            replicas=3, template=template, selector={
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
        print("Not implemented yet")

    return deployment

#create deployment from a given deployment object and api
def create_deployment(api, deployment):
    # Create deployement
    try:
        resp = api.create_namespaced_deployment(
            body=deployment, namespace="default"
        )

        print("\n[INFO] deployment `nginx-deployment` created.\n")
        print("%s\t%s\t\t\t%s\t%s" % ("NAMESPACE", "NAME", "REVISION", "IMAGE"))
        print(
            "%s\t\t%s\t%s\t\t%s\n"
            % (
               resp.metadata.namespace,
                resp.metadata.name,
                resp.metadata.generation,
                resp.spec.template.spec.containers[0].image,
            )
        )
    except Exception as ex:
        print("Creating deployment failed")
        print("Caught exception:" + format(ex))
        print("Continuing with stack deployment")

def update_deployment(api, deployment):
    # Update container image
    deployment.spec.template.spec.containers[0].image = "nginx:1.16.0"

    # patch the deployment
    resp = api.patch_namespaced_deployment(
        name=DEPLOYMENT_NAME, namespace="default", body=deployment
    )

    print("\n[INFO] deployment's container image updated.\n")
    print("%s\t%s\t\t\t%s\t%s" % ("NAMESPACE", "NAME", "REVISION", "IMAGE"))
    print(
        "%s\t\t%s\t%s\t\t%s\n"
        % (
            resp.metadata.namespace,
            resp.metadata.name,
            resp.metadata.generation,
            resp.spec.template.spec.containers[0].image,
        )
    )

def restart_deployment(api, deployment):
    # update `spec.template.metadata` section
    # to add `kubectl.kubernetes.io/restartedAt` annotation
    deployment.spec.template.metadata.annotations = {
        "kubectl.kubernetes.io/restartedAt": datetime.datetime.utcnow()
        .replace(tzinfo=pytz.UTC)
        .isoformat()
    }

    # patch the deployment
    resp = api.patch_namespaced_deployment(
        name=DEPLOYMENT_NAME, namespace="default", body=deployment
    )

    print("\n[INFO] deployment `nginx-deployment` restarted.\n")
    print("%s\t\t\t%s\t%s" % ("NAME", "REVISION", "RESTARTED-AT"))
    print(
        "%s\t%s\t\t%s\n"
        % (
            resp.metadata.name,
            resp.metadata.generation,
            resp.spec.template.metadata.annotations,
        )
    )

def delete_deployment(api):
    # Delete deployment
    resp = api.delete_namespaced_deployment(
        name=DEPLOYMENT_NAME,
        namespace="default",
        body=client.V1DeleteOptions(
            propagation_policy="Foreground", grace_period_seconds=5
        ),
    )
    print("\n[INFO] deployment `nginx-deployment` deleted.")

def list_pods(api):
    print("Listing pods with their IPs:")
    ret = api.list_pod_for_all_namespaces(watch=False)
    for i in ret.items:
        print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

def create_changed_deployment_specs_based_on_scaling_object(deployment, scalingobject):
    print(scalingobject.elasticityCapacity)
    print(scalingobject.calcReplicas(30.0,deployment.spec.replicas))
    return deployment

def main():
    print("Load kube config")
    try:
        config.load_incluster_config()
    except config.ConfigException:
        config.load_kube_config(config_file='k8s-cluster3-admin.conf')

    #setup deployment, prometheus monitoring, scaling method etc
    #initialize necessary apis
    core_api = client.CoreV1Api()
    apis_api = client.AppsV1Api()

    #create and deploy deploymentspecifications
    deployment = create_deployment_object_from_file()
    create_deployment(apis_api, deployment)

    #TODO setup prometheus (monitoring and api interface)
    #setup scaling method, e.g.: CAUS,ML-CAUS and others
    myCaus = CAUS()
# changing replicas in spec part of deployment
#    spec = deployment.spec
#    spec.replicas = 4
#    print(spec)
#    print(deployment.spec)
#
# other useful code
#    update_deployment(apis_api, deployment)
#    delete_deployment(apis_api)
#    list_pods(core_api)

    #check initial spec
    print("start replicas: " + str(deployment.spec.replicas))

    #update loop
    deployment = create_changed_deployment_specs_based_on_scaling_object(deployment, myCaus)
    #update_deployment(apis_api, deployment)
    print("updated replicas: " + str(deployment.spec.replicas))

if __name__ == "__main__":
    main()
