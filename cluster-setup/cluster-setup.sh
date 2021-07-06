#!/bin/sh

#launch master node
multipass launch -n master --cpus 4 --mem 2G --disk 100G

#launch worker nodes
for i in 1;  do
  multipass launch -n worker$i --cpus 5 --mem 4G --disk 100G
done

# start master node
multipass exec master -- \
  bash -c "curl -sfL https://get.k3s.io | sh -"

# get TOKEN and IP
TOKEN=$(multipass exec master sudo cat /var/lib/rancher/k3s/server/node-token)
IP=$(multipass info master | grep IPv4 | awk '{print $2}')

echo "TOKEN"
echo $TOKEN
echo "IP"
echo $IP

# Joining worker nodes
for i in 1; do
  multipass exec worker$i -- \
bash -c "curl -sfL https://get.k3s.io | K3S_URL=\"https://$IP:6443\" K3S_TOKEN=\"$TOKEN\" sh -"
done

# get kubeconfig
multipass exec master sudo cat /etc/rancher/k3s/k3s.yaml > config


# replace localhost with assigned IP
sed -i "s/127.0.0.1/$IP/" config

#set kubectl config
export KUBECONFIG=$PWD/config

# verify
kubectl get node

# change to docker executor
kubectl edit configmap workflow-controller-configmap -n kubeflow
# pns -> docker