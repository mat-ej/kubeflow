import kfp
from pathlib import Path

# CLUSTER = 'http://147.251.253.24'

# requires port forward.
CLUSTER = 'http://localhost:3000'
PIPE_DIR = '../pipes-compiled/'
client = kfp.Client(CLUSTER)
