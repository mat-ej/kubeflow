https://docs.k0sproject.io/v1.21.2+k0s.1/install/

curl -sSLf https://get.k0s.sh | sudo sh
sudo k0s install controller --single
sudo k0s start
sudo k0s status
sudo k0s kubectl get nodes

sudo cp /var/lib/k0s/pki/admin.conf ~/.kube/config
export KUBECONFIG=~/.kube/config
kubectl get node