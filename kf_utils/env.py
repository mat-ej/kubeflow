import kfp
# Ingressed
# CLUSTER = 'http://147.251.253.24'

# requires port forward.
CLUSTER = 'http://localhost:8080'
PIPE_DIR = '/home/m/repo/inflow/kubeflow/pipes-compiled/'
client = kfp.Client(CLUSTER)


