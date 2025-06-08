# GitHub Data Pipeline Setup Guide

This guide provides step-by-step instructions to set up and deploy the GitHub Data Pipeline. The pipeline uses Dagster for orchestration, PostgreSQL for metadata storage, AWS S3 for artifact storage, and Nginx for proxying the Dagster UI.

---

## Prerequisites

Before you begin, ensure you have:

- **`sudo`** privileges on your Linux machine.
- **AWS credentials** (Access Key ID, Secret Access Key, Default Region) for S3 access.
- **PostgreSQL RDS endpoint** details (host, port, user, password, database name).
- **GitHub Personal Access Token** with appropriate permissions.
- A minimum of a `t3.medium` EC2 instance is required to ensure adequate CPU and memory resources for the deployment.

---

## Setup Instructions

Follow these steps sequentially to set up the GitHub Data Pipeline.

### 1. Update System and Install Dependencies

This command updates your system's package list and installs necessary dependencies, including Python 3.10, virtual environment tools, pip, Docker, Docker Compose, and Git.

`sudo apt update
sudo apt install -y python3.10 python3.10-venv python3-pip docker.io docker-compose git`

### 2. Clone the Repository

Clone the GitHub Data Pipeline repository from GitHub and navigate into its directory.

`git clone https://github.com/Shuvam-M-Astro/Github-Data-Pipeline.git
cd Github-Data-Pipeline`

### 3. Create and Activate Virtual Environment

Create a Python virtual environment to isolate project dependencies and activate it.

`python3.10 -m venv venv
source venv/bin/activate`

### 4. Install Poetry and Configure It

Install Poetry, a dependency management tool, and configure it to create virtual environments within the project directory, using Python 3.10.

`pip install poetry
poetry config virtualenvs.in-project true
poetry env use python3.10`

### 5. Install Additional Required Packages

Install the necessary Python packages using Poetry, including `dagster`, `dagster-postgres`, `dagster-aws`, `psycopg2-binary`, and `boto3`.

`poetry add dagster dagster-postgres dagster-aws psycopg2-binary boto3
poetry install`

### 6. Create Necessary Directories

Create the `dagster_local` directory, which will be used for Dagster's local configuration.

`mkdir -p dagster_local`

### 7. Create Environment File

Create a `.env` file to store your GitHub token. This file no longer includes AWS or PostgreSQL configurations. 

```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_DEFAULT_REGION=us-east-1                     # e.g., us-west-2, eu-central-1
S3_BUCKET_NAME=your-s3-bucket-name               # e.g., github-pipeline-data

# PostgreSQL Configuration
POSTGRES_HOST=your-db-host                       # e.g., localhost or RDS endpoint
POSTGRES_PORT=5432                               # default PostgreSQL port
POSTGRES_USER=your-db-username
POSTGRES_PASSWORD=your-db-password
POSTGRES_DB=your-database-name

# GitHub API Configuration
GITHUB_TOKEN=your-github-personal-access-token   # with repo read permissions

# Instance Configuration
HOST_UID=1000                                     # UID of the user running the service
HOST_GID=1000                                     # GID of the group running the service
```

### 8. Create Dagster Configuration

Create the `dagster.yaml` file within the `dagster_local` directory. This configuration tells Dagster to use local filesystem storage for compute logs and artifacts, and it will default to an SQLite database within `DAGSTER_HOME` for run history and event logs.

```bash
cat << EOF > dagster_local/dagster.yaml
telemetry:
  enabled: false

storage:
  postgres: # This block connects Dagster's metadata to PostgreSQL RDS
    postgres_db:
      hostname: ${POSTGRES_HOST}
      username: ${POSTGRES_USER}
      password: ${POSTGRES_PASSWORD}
      db_name: ${POSTGRES_DB}
      port: ${POSTGRES_PORT}

compute_logs:
  module: dagster.core.storage.local_compute_log_manager
  class: LocalComputeLogManager
  config:
    base_dir: /var/log/dagster/compute_logs

local_artifact_storage: # This is for local temporary storage, not S3
  module: dagster.core.storage.root
  class: LocalArtifactStorage
  config:
    base_dir: /tmp/dagster/artifacts
EOF
```

### 9. Create Systemd Service

Create a systemd service unit file for the GitHub Pipeline. This allows Dagster to run as a background service and restart automatically. The service runs as your current user and sources environment variables from the `.env` file.

```bash
sudo tee /etc/systemd/system/github-pipeline.service << EOF
[Unit]
Description=GitHub Pipeline Dagster Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PWD
EnvironmentFile=$PWD/.env
Environment=DAGSTER_HOME=$PWD/dagster_local
ExecStart=$PWD/venv/bin/poetry run dagster dev -h 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
EOF
```

### 10. Set up Nginx

Install Nginx and configure it to act as a reverse proxy for the Dagster UI, which typically runs on port `3000`. This makes the Dagster UI accessible via standard HTTP (port 80).

```bash
sudo apt install -y nginx

sudo tee /etc/nginx/sites-available/github-pipeline << EOF
server {
    listen 80;
    server_name \$host;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF
```

### 11. Enable Nginx Configuration

Enable the Nginx configuration by creating a symbolic link, test the configuration for syntax errors, and then restart Nginx to apply the changes.

`sudo ln -s /etc/nginx/sites-available/github-pipeline /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx`

### 12. Start Dagster Service

Reload the systemd manager configuration, start the Dagster service, and enable it to start automatically on boot.

`sudo systemctl daemon-reload
sudo systemctl start github-pipeline
sudo systemctl enable github-pipeline`

### 13. Create Log Directories

Create the necessary log directories for Dagster compute logs and set appropriate ownership to your user.

`sudo mkdir -p /var/log/dagster/compute_logs
sudo chown -R $USER:$USER /var/log/dagster`