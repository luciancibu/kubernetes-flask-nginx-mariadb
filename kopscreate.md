### Commands: ###
docker login

docker build -t luciancibu/flask-counter:1.0 .
docker tag luciancibu/flask-counter:1.0 luciancibu/flask-counter:latest
docker push luciancibu/flask-counter:1.0
docker push luciancibu/flask-counter:latest

docker build -t luciancibu/nginx-resume:1.0 .
docker tag luciancibu/nginx-resume:1.0 luciancibu/nginx-resume:latest
docker push luciancibu/nginx-resume:1.0
docker push luciancibu/nginx-resume:latest


kubectl rollout restart deployment appnginx
kubectl rollout restart deployment appflask

### Install docker Linux ###

# Add Docker's official GPG key:
sudo apt update
sudo apt install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt update

sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y


### Install kubectl ###
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.irelease/stable.txt)/bin/linux/amd64/kubectl"

sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl


### Install kops ###
curl -Lo kops https://github.com/kubernetes/kops/releases/download/$(curl -s https://api.github.com/repos/kubernetes/kops/releases/latest | grep tag_name | cut -d '"' -f 4)/kops-linux-amd64
chmod +x kops
sudo mv kops /usr/local/bin/kops


### Ingress Nginx controller ###
Doc: https://kubernetes.github.io/ingress-nginx/deploy/#aws
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.14.1/deploy/static/provider/cloud/deploy.yaml

kubectl delete -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.14.1/deploy/static/provider/cloud/deploy.yaml




### Create Cluster ###
kops create cluster --name=resume.kakosnita.xyz --state=s3://kopsstate0731910497 \
--zones=us-east-1a,us-east-1b --node-count=2 --node-size=t3.small --control-plane-size=t3.medium \
--dns-zone=resume.kakosnita.xyz --node-volume-size=12 --control-plane-volume-size=12 \
--ssh-public-key ~/.ssh/id_ed25519.pub

kops update cluster --name=resume.kakosnita.xyz --state=s3://kopsstate0731910497 --yes --admin


### Validate: ###
kops validate cluster --name=resume.kakosnita.xyz --state=s3://kopsstate0731910497


### Delete: ###
kops delete cluster --name=resume.kakosnita.xyz --state=s3://kopsstate0731910497 --yes


### K8 Objects: ###
- Pod
- Service
- Replica Service
- Deployment
- Config Map
- Secret
- Volume


### Pod: ###
---
apiVersion: v1
kind: Pod
metadata:
  name: vproapp
  labels:
    app: vproapp
spec:
  containers:
  - name: appcontainer
    image: luciancibu/nanoimg:V2
    ports:
    - name: vproapp-port
      containerPort: 80

kubectl create -f file.yaml
kubectl get pod
kubectl describe pod
kubectl delete pod <pod_name>


### Namespaces ###
---
apiVersion: v1
kind: Pod
metadata:
  name: nginx12           ->  <pod_name>
  namespace: kubecart     ->  <namespace_name>
spec:
  containers:
  - name: nginx           -> <container_name>
    image: nginx:1.14.2   -> <image_name_to_pull>
    ports:
    - containerPort: 80

kubectl create ns <namespce_name>   -> create a namespace
kubectl get namespaces

kubectl create -f <pod1.yml>
kubectl apply -f <pod1.yml>   -> apply the changes, first need to create the pod
kubectl get pod -n <namespce_name>   -> to get all pods from a specific namespace       
kubectl delete ns <namespce_name>    -> delete namespace + <everything> from that namespace!!

kubectl get all
kubectl get all --all-namespaces
kubectl get svc -n <namespce_name>   -> to get all services from a specific namespace
kubectl run <pod_name> --image=<image_name>> -n <namespce_name>  -> run a pod in a specific namespace


### Logging ###

kubectl get pod -o wide
kubectl get pod <pod_name> -o yaml     -> print yaml
kubectl describe pod <pod_name>


### Service ###
- NodePort -> expose node to outside network -> not for production
- ClusterIP -> internal comunication
- LoadBalacer -> expose node to outside network -> for production

apiVersion: v1
kind: Service
metadata:
  name: helloworld-service
spec:
  ports:
    - port: 80                     -> external port
      targetPort: vproapp-port
      protocol: TCP
  selector:
    app: vproapp
  type: LoadBalancer

#################################
#################################
#################################

apiVersion: v1
kind: Service
metadata:
  name: helloworld-service
spec:
  ports:
    - port: 8090         -> frontend interbal port
      nodePort: 30001    -> external port
      targetPort: vproapp-port  -> target port (eg 80 in our case)
      protocol: TCP
  selector:
    app: vproapp
  type: NodePort


### Replica ###

apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: frontend
  labels:
    app: guestbook
    tier: frontend
spec:
  # modify replicas according to your case
  replicas: 3
  selector:
    matchLabels:
      tier: frontend
  template:
    metadata:
      labels:
        tier: frontend
    spec:
      containers:
      - name: php-redis
        image: us-docker.pkg.dev/google-samples/containers/gke/gb-frontend:v5

kubectl scale --replicas=1 rs <replica_name>
kubectl edit rs <replica_name>


### Deployment ###

apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.14.2
        ports:
        - containerPort: 80

kubectl set image deployment.v1.apps/nginx-deployment nginx=nginx:1.16.1  -> will update image. Will create a new replica for undated image

kubectl rollout undo deployment/nginx-deployment  -> rollback to old deployment, will use again old replica

kubectl rollout undo deployment/nginx-deployment --to-revision=2 -> same as above but you can specify the number of revision e.g. 2 deployments behind


### Arguments ###

apiVersion: v1
kind: Pod
metadata:
  name: command-demo
  labels:
    purpose: demonstrate-command
spec:
  containers:
  - name: command-demo-container
    image: debian
    command: ["printenv"]
    args: ["HOSTNAME", "KUBERNETES_PORT"]
  restartPolicy: OnFailure

kubectl logs command-demo   -> this will print the logs


### Connect to pod ###
kubectl exec --stdin --tty <pod_name> --bin/bash   --> connect to a pod  


### Secrets ###
echo -n "secretpass" | base64                    -> encode base64
echo -n "encoded_password" | base64 --decode     -> encode base64



### For EKS ###

aws eks update-kubeconfig \
  --region <region> \
  --name <eks_name>

kubectl get endpoints flask-nginx-mariadb-nginx
kubectl get endpoints flask-nginx-mariadb-flask
kubectl logs deploy/flask-nginx-mariadb-nginx
kubectl logs deploy/flask-nginx-mariadb-flask

kubectl get pods | grep mariadb
kubectl logs deploy/flask-nginx-mariadb-mariadb

kubectl exec -it deploy/flask-nginx-mariadb-nginx -- sh
curl -v http://flask-nginx-mariadb-flask:5000/view

kubectl exec -it deploy/flask-nginx-mariadb-flask -- sh
