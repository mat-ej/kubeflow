import kfp
# Ingressed
# CLUSTER = 'http://147.251.253.24'

# requires port forward.
IMG = 'matejcvut/kubeflow-pod:0' #default component env.
CLUSTER = 'http://localhost:8080'
PIPE_DIR = '/home/m/repo/inflow/kubeflow/pipes-compiled/'
client = kfp.Client(CLUSTER)


