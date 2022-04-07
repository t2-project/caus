import os
from caus import CAUS
from kubernetes import client, config

print("Load kube config")
os.environ['KUBECONFIG'] = './k8s-cluster3-admin.conf'
config.load_kube_config()

#list all pods / test code
v1 = client.CoreV1Api()
print("Listening pods with their IPs:")
ret = v1.list_pod_for_all_namespaces(watch=False)
for i in ret.items:
    print("%s\%t\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

#causstuff
myCaus = CAUS()
print(myCaus.elasticityCapacity)
