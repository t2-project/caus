import os
import time
import yaml
from caus import CAUS
from kubernetes import client, config
from elasticity import elasticity
from prometheusclient import prometheusMonitor 
DEPLOYMENT_NAME = "kafka-consumer-deployment"

class controller:

    def __init__(self, elasticity):
        #load config
        print("Load kube config...")
        try:
            config.load_incluster_config()
        except config.ConfigException:
            print("didnt find incluster config, loading file manually...")
            config.load_kube_config(config_file='k8s-cluster3-admin.conf')

        print("Initializing...")
        #initialize necessary apis
        self.core_api = client.CoreV1Api()
        self.apis_api = client.AppsV1Api()

        #create deployment
        self.deployment = self.create_deployment_object_from_file()
        self.create_deployment()
        
        #prometheusMonitoring
        self.myMonitor = prometheusMonitor()

        #elasticity and caus
        self.myElasticity = elasticity
        self.myCaus = CAUS(self.myElasticity)



    # Creates an object from a file with the given path or creates default object -> TODO
    def create_deployment_object_from_file(self,path: str=""):

        #check if a path was given -> if it wasnt: create default object
        if not path:
            # Configurate default Pod template container
            container = client.V1Container(
                name="kafka-consumer",
                image="zilchms/consumer:latest",
            )

            # Create and configure a spec section
            template = client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels={"app": "kafka-consumer"}),
                spec=client.V1PodSpec(containers=[container]),
            )

            # Create the specification of deployment
            spec = client.V1DeploymentSpec(
                replicas=2, template=template, selector={
                    "matchLabels":
                    {"app": "kafka-consumer"}})

            # Instantiate the deployment object
            deployment = client.V1Deployment(
                api_version="apps/v1",
                kind="Deployment",
                metadata=client.V1ObjectMeta(name=DEPLOYMENT_NAME),
                spec=spec,
            )

# json file not the same format as above example TODO: conform both and build/access data from there
#    else:
#        with open(path) as f:
#            deployment = yaml.safe_load(f)
#        print("Deployment read from: ", path)

        return deployment

    #create deployment from a given deployment object and api
    def create_deployment(self):
        # Create deployement
        try:
            resp = self.apis_api.create_namespaced_deployment(
                body=self.deployment, namespace="default"
            )

            print("\n[INFO] deployment `kafka-consumer-deployment` created.\n")
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

    def update_deployment(self):
        # patch the deployment
        resp = self.apis_api.patch_namespaced_deployment(
            name=DEPLOYMENT_NAME, namespace="default", body=self.deployment
        )
        print("\n[INFO] deployment's container image updated.\n")

# maybe needed for cleanup -> saved for later
#def delete_deployment(api):
#    # Delete deployment
#    resp = api.delete_namespaced_deployment(
#        name=DEPLOYMENT_NAME,
#        namespace="default",
#        body=client.V1DeleteOptions(
#            propagation_policy="Foreground", grace_period_seconds=5
#        ),
#    )
#    print("\n[INFO] deployment `nginx-deployment` deleted.")

    def scale_deployment_object(self, deployment, scalingobject, elasticityobject, publishingRate):
        #print(scalingobject.elasticityCapacity)
        desiredReplicas, bufferedReplicas = scalingobject.calcReplicas(publishingRate,deployment.spec.replicas)
        print("Computed desired replicas: ", desiredReplicas, " and buffered: ", bufferedReplicas)
        #update elasticity spec of caus
        deployment.spec.replicas = desiredReplicas
        elasticityobject.elasticityBufferedReplicas = bufferedReplicas
        return deployment

    def start(self):
        #check initial spec
        print("start replicas: " + str(self.deployment.spec.replicas))
        print()

        #update loop
        while True:
            #Get Monitoring Data
            publishingRate = float(self.myMonitor.getMessagesInPerSec_OneMinuteRate())
            #build new deployment data on scaling algorithm
            self.deployment = self.scale_deployment_object(self.deployment, self.myCaus, self.myElasticity, publishingRate)
            #update deployment
            self.update_deployment()
            #wait x seconds to rescale again
            time.sleep(15)
