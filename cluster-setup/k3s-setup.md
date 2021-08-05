# K3s install
curl -sfL https://get.k3s.io | sh -

## set up kubectl
sudo cat /etc/rancher/k3s/k3s.yaml > .kube/config
curl -sfL https://get.k3s.io | sh -
kubectl get nodes

## k3ai install traefik 
k3ai apply -g kubeflow-pipelines-traefik

kubectl get ingresses -n kubeflow



