from kubernetes import client, config

#Example code
config.load_kube_config()

v1 = client.CoreV1Api()
print("Listing pods with their IPs:")
ret = v1.list_pod_for_all_namespaces(watch=False)
for i in ret.items:
    print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

# our code starts here
def main():
    #abstract steps to get this running
    #1. build kubeconfig richtig
    #2. build elasticity client
    #3. build kubernetes client
    #4. informer und listener korrekt bauen (?)
    #5. prometheus monitor bauen
    #6. controller für alles zusammenschweißen
