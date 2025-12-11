# Deployment Guide for ContextIQ Backend

## Option 1: DigitalOcean (Simplest & Cost-Effective)

DigitalOcean is often easier to use than AWS or GCP.

### A. App Platform (Easiest - PaaS)
This is like Vercel/Heroku. You don't manage servers.
1.  Push your code to **GitHub**.
2.  Go to DigitalOcean -> **Apps** -> **Create App**.
3.  Select **GitHub** and choose your repository.
4.  It will detect the `Dockerfile`.
5.  Edit the service:
    - **HTTP Port**: Set to `8000`.
6.  Click **Launch**.

### B. Droplet (Virtual Server - Cheaper)
Similar to EC2 but with a simpler UI. Starts at ~$4/mo.
1.  Create a **Droplet** (Ubuntu 22.04).
2.  **SSH** into it: `ssh root@your_droplet_ip`
3.  Run the setup (same as EC2):
    ```bash
    # Install Docker
    snap install docker

    # Clone & Run
    git clone https://github.com/your-username/your-repo.git
    cd your-repo/backend/backend 
    # (Note: Adjust path if you cloned the root. Inside root, go to backend/)
    cd backend
    docker build -t backend .
    docker run -d -p 8000:8000 --restart always --name contextiq-backend backend
    ```

---

## Option 2: Amazon EC2 (Flexible)

Deploying to EC2 free-tier (t2.micro/t3.micro).

### 1. Launch Instance
- Launch an **Ubuntu 22.04 LTS** instance.
- **Security Group**: Allow TCP **8000** and **22** (SSH).

### 2. Connect & Install
```bash
ssh -i "key.pem" ubuntu@ip-address

# Install Docker
sudo apt-get update && sudo apt-get install -y docker.io
sudo usermod -aG docker $USER && newgrp docker
```

### 3. Deploy
```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo/backend
# Enter the backend directory
cd backend
docker build -t backend .
docker run -d -p 8000:8000 --restart always --name backend backend
```

---

## Option 3: Google Cloud Run (Serverless)

*Requires Billing Enabled.*

### Setup
```bash
# 1. Login (opens browser)
~/google-cloud-sdk/bin/gcloud auth login

# 2. Set your specific project
~/google-cloud-sdk/bin/gcloud config set project docanalyzer-470219
```

### Deploy
Run the following command (ensure you are in the `backend` directory):

```bash
cd backend
~/google-cloud-sdk/bin/gcloud run deploy contextiq-backend \
  --source . \
  --port 8000 \
  --region us-central1 \
  --allow-unauthenticated
```
