# caus-python
Python implementation of CAUS

## Requirements ##
### Python Libraries ###
kuberentes python client: https://github.com/kubernetes-client/python
install with 'pip install kubernetes' onto machine or into a fitting virtual env

Prometheus Api Client
https://pypi.org/project/prometheus-api-client/
pip install prometheus\_api\_client

### Running Services ###
Prometheus for Kubernetes; Metrics need to be accessible from inside the cluster (see monitoring module code)
Kafka for Kubernetes

### Kubernetes Deployment ###
The caus-deployment.yaml has to be altered.
$imagename has to be replace with the official name of the image you generate with the Dockerfile
We used Dockerhub for saving the generated image and access it with the kubernetes deployment.

CAUS can then be applied with kubectl apply -f caus-deployment.yaml

