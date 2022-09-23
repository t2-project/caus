# caus-python
Python implementation of CAUS

## Requirements
### Python Libraries
You can install everything using `pip install -r requirements.txt` (either inside a virtual env or globally).

Alternatively, you can install the needed libraries manually:

- Kuberentes Python Client
  - homepage: <https://github.com/kubernetes-client/python>
  - `pip install kubernetes`
- Prometheus Api Client
  - homepage: <https://pypi.org/project/prometheus-api-client/>
  - `pip install prometheus_api_client`.


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

## Developing the CAUS

The CAUS currently uses [black](https://github.com/psf/black) as its formatter.
If you followed the requirements above, it will already be downloaded and can be called using `black *.py`.
