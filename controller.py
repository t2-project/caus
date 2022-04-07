import os
from caus import CAUS
from kubernetes import client, config

print("Load kube config")
#os.environ['KUBECONFIG'] = './k8s-cluster3-admin.conf'
#try:
#    config.load_incluster_config()
#except config.ConfigException:
#    config.load_kube_config()
config.load_kube_config(config_file='k8s-cluster3-admin.conf')

v1 = client.CoreV1Api()

#list all pods / test code
#print("Listening pods with their IPs:")
#ret = v1.list_pod_for_all_namespaces(watch=False)
#for i in ret.items:
#    print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

#list all namespaces / test code
print("Finding namespaces: ...")
ret = v1.list_namespace()
for i in ret.items:
# code for finding deployments in a namespace, does not work with corev1api -> needs rest api of kubernetes python client
#    depl_ret = v1.list_namespaced_deployment(namespace=i.metadata.name)
#    for i in depl_ret.items:
    print(i.metadata.name)

#causstuff
myCaus = CAUS()
print(myCaus.elasticityCapacity)
