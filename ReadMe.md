# Dockerized Flask + Nginx + MariaDB

In this repository each service runs in its own Docker container and communicates over a container network.

The application can be deployed using **Docker Compose** (local development) or **Kubernetes** (production-like setup).

---

## Architecture (Kubernetes)

```
User Browser
   |
   v
Kubernetes Ingress
   |
   v
nginx-service (ClusterIP)
   |
   v
Nginx Pods
   |
   |  /view
   v
flask-service (ClusterIP)
   |
   v
Flask Pods
   |
   v
mariadb-service (ClusterIP)
   |
   v
MariaDB Pod (PVC)
```

- External traffic enters the cluster through **Ingress**
- **Nginx Service** is the internal entry point
- **Flask** and **MariaDB** are internal-only services
- **MariaDB** uses persistent storage via a PVC

---

## Services

- **Nginx**
  - Serves static HTML/CSS
  - Acts as a reverse proxy for the Flask API
  - Single entry point inside the cluster

- **Flask**
  - Exposes `/view`
    - increments a counter
    - reads the counter value
  - Communicates with MariaDB via Kubernetes Services

- **MariaDB**
  - Stores a persistent counter
  - Initialized automatically using SQL scripts

---

## Project Structure

```
.
├── docker-compose.yml
├── nginx/
│   ├── Dockerfile
│   ├── default.conf
│   └── html/
│       └── index.html
├── flask/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
├── mariadb/
│   └── init.sql
└── kubedefs/
    ├── dbdeployment.yaml
    ├── dbservice.yaml
    ├── flaskdeployment.yaml
    ├── flaskservice.yaml
    ├── nginxdeployment.yaml
    ├── nginxservice.yaml
    ├── ingress.yaml
    ├── pvc.yaml
    └── secret.yaml
```

---

## How to Run (Docker Compose)

```bash
docker compose up -d --build
```

- Only **Nginx** exposes a public port
- Services communicate using Docker service names

---

## How to Run (Kubernetes)

### Prerequisites
- Kubernetes cluster
- Nginx Ingress Controller installed
- Docker images pushed to a registry (Docker Hub)

### Deploy

```bash
kubectl apply -f kubedefs/
```

### Access

- Application is exposed via **Ingress**
- Nginx Service is the cluster entry point
- Flask and MariaDB are internal services (`ClusterIP`)

---