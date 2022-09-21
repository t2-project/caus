# caus-python
Python implementation of CAUS

## Requirements
### Python Libraries
kuberentes python client: <https://github.com/kubernetes-client/python>
Install with `pip install kubernetes` onto machine or into a fitting virtual env.

Prometheus Api Client: <https://pypi.org/project/prometheus-api-client/>
Install with `pip install prometheus_api_client`.

Alternatively, install everything using `pip install -r requirements.txt`.

### Running Services
`Prometheus` for Kubernetes. Metrics must be accessible from inside the cluster.  
`Kafka` for Kubernetes

Adapt the `config.ini` config file to your needs.  
Alternatively, you can set a custom path for your config file by setting the `CAUS_CONFIG` environment variable.  
Run by calling `python controller.py`.

### Kubernetes Deployment
The `caus-deployment.yaml` has to be altered.  
`$imagename` has to be replaced with the official name of the image you generate with the Dockerfile.  
We used Dockerhub for saving the generated image and access it with the kubernetes deployment.

CAUS can then be applied using `kubectl apply -f caus-deployment.yaml`.

