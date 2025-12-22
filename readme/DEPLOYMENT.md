# Deployment Guide

Complete instructions for deploying AutoML System in various environments.

## Local Development

### Quick Start (5 minutes)

**Backend:**
```bash
# Navigate to project root
cd AutoML_System

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Start backend
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Access:**
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Docker Deployment

### Backend Docker

**Dockerfile (create in root):**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build & Run:**
```bash
# Build
docker build -t automl-backend .

# Run
docker run -p 8000:8000 \
  -v $(pwd)/artifacts:/app/artifacts \
  -v $(pwd)/uploads:/app/uploads \
  automl-backend
```

### Frontend Docker

**Dockerfile (in frontend/):**
```dockerfile
# Build stage
FROM node:18 AS builder
WORKDIR /app
COPY package.json package-lock.json .
RUN npm install
COPY . .
RUN npm run build

# Serve stage
FROM node:18-alpine
WORKDIR /app
RUN npm install -g serve
COPY --from=builder /app/dist ./dist
EXPOSE 3000
CMD ["serve", "-s", "dist", "-l", "3000"]
```

**Build & Run:**
```bash
cd frontend
docker build -t automl-frontend .
docker run -p 3000:3000 automl-frontend
```

### Docker Compose

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./artifacts:/app/artifacts
      - ./uploads:/app/uploads
      - ./results_api:/app/results_api
    environment:
      - DEBUG=false
    depends_on:
      - postgres

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: automl
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

**Run:**
```bash
docker-compose up -d
```

---

## Production Deployment

### Python Server (Gunicorn)

**Install gunicorn:**
```bash
pip install gunicorn
```

**Run with gunicorn:**
```bash
gunicorn -w 4 -b 0.0.0.0:8000 \
  --timeout 300 \
  --access-logfile - \
  app:app
```

**With process manager (systemd):**

Create `/etc/systemd/system/automl.service`:
```ini
[Unit]
Description=AutoML Backend
After=network.target

[Service]
User=www-data
WorkingDirectory=/home/www-data/automl
ExecStart=/home/www-data/automl/.venv/bin/gunicorn \
  -w 4 -b 0.0.0.0:8000 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable:**
```bash
sudo systemctl enable automl
sudo systemctl start automl
```

### Nginx Reverse Proxy

**Config (/etc/nginx/sites-available/automl):**
```nginx
upstream automl_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name automl.example.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Backend API
    location /api/ {
        proxy_pass http://automl_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Long timeout for ML jobs
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
    }

    # Static files
    location /static/ {
        alias /home/www-data/automl/frontend/dist/;
    }
}
```

**Enable:**
```bash
sudo ln -s /etc/nginx/sites-available/automl /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### SSL/TLS with Let's Encrypt

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d automl.example.com
```

---

## Cloud Deployment

### AWS EC2

**1. Launch EC2 instance:**
```bash
# Ubuntu 22.04, t3.medium or larger
# Security group: Allow 80, 443, 8000 (if direct)
```

**2. Connect and setup:**
```bash
# SSH into instance
ssh -i key.pem ubuntu@instance-ip

# Install dependencies
sudo apt update && sudo apt upgrade -y
sudo apt install python3.11 python3-pip python3-venv \
  nodejs npm nginx postgresql git -y

# Clone repo
git clone <repo-url>
cd AutoML_System

# Setup backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Setup frontend
cd frontend
npm install
npm run build
cd ..

# Start backend with gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app &

# Configure nginx (see above)
```

**3. Configure artifacts storage:**
```bash
# Use EBS volume
mkdir -p /mnt/artifacts
chmod 755 /mnt/artifacts

# Update app.py
ARTIFACTS_DIR = Path("/mnt/artifacts")
```

### Google Cloud Run

**Create Dockerfile and deploy:**
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/automl-backend
gcloud run deploy automl-backend \
  --image gcr.io/PROJECT_ID/automl-backend \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --timeout 300
```

**For frontend:**
```bash
cd frontend
npm run build

gsutil -m cp -r dist/* gs://PROJECT_ID-automl/
```

### Azure App Service

**Backend:**
```bash
# Create App Service
az appservice plan create --name automl-plan --resource-group mygroup --sku B2

az webapp create --resource-group mygroup \
  --plan automl-plan --name automl-backend \
  --runtime "PYTHON:3.11"

# Deploy
az webapp deployment source config-zip --resource-group mygroup \
  --name automl-backend --src package.zip
```

**Frontend:**
```bash
# Static Web Apps
az staticwebapp create --name automl-frontend \
  --resource-group mygroup \
  --source https://github.com/your/repo
```

---

## Database Setup (Optional)

For job history and artifact metadata:

```bash
# PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb automl
sudo -u postgres createuser automl_user
sudo -u postgres psql -c "ALTER USER automl_user WITH PASSWORD 'password';"

# In app.py, add SQLAlchemy
from sqlalchemy import create_engine
engine = create_engine('postgresql://automl_user:password@localhost/automl')
```

---

## Monitoring

### Logs

```bash
# Gunicorn logs
tail -f /var/log/automl.log

# Systemd logs
journalctl -u automl -f

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Metrics

**Install Prometheus:**
```bash
sudo apt install prometheus
```

**Add to FastAPI (optional):**
```python
from prometheus_client import Counter, Histogram, generate_latest

pipeline_runs = Counter('pipeline_runs_total', 'Total pipeline runs')
pipeline_duration = Histogram('pipeline_duration_seconds', 'Pipeline duration')

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### Uptime Monitoring

```bash
# Health check endpoint
curl http://automl.example.com/api/health

# Automated monitoring
# Use: Datadog, New Relic, CloudWatch, etc.
```

---

## Performance Tuning

### Backend

```python
# In app.py
app = FastAPI()

# Increase worker threads
# gunicorn -w 8 --threads 4 app:app

# Enable compression
from fastapi.middleware.gzip import GZIPMiddleware
app.add_middleware(GZIPMiddleware, minimum_size=1000)

# Connection pooling
# sqlalchemy engine with pool_size
```

### Frontend

```bash
# Build optimization
npm run build

# Serve with compression
serve -s dist -l 3000 -c ./serve.json
```

---

## Backup & Disaster Recovery

### Backup Strategy

```bash
# Backup artifacts (daily)
*/0 * * * * tar -czf /backup/artifacts-$(date +%Y%m%d).tar.gz /app/artifacts

# Backup uploads (weekly)
0 0 * * 0 tar -czf /backup/uploads-$(date +%Y%m%d).tar.gz /app/uploads

# Backup database (daily)
0 1 * * * pg_dump automl | gzip > /backup/db-$(date +%Y%m%d).sql.gz
```

### Restore

```bash
# Restore artifacts
tar -xzf /backup/artifacts-20251222.tar.gz -C /app

# Restore database
gunzip -c /backup/db-20251222.sql.gz | psql automl
```

---

## Troubleshooting

### Issue: Backend won't start
```bash
# Check port
lsof -i :8000

# Check dependencies
pip list | grep -E "fastapi|scikit-learn"

# Run with debug
python app.py  # If development mode
```

### Issue: Frontend can't reach backend
```bash
# Check CORS
curl -H "Origin: http://localhost:3000" http://localhost:8000/api/health

# Update frontend .env
VITE_API_BASE_URL=http://localhost:8000/api
```

### Issue: Memory spike
```bash
# Reduce sample size
MAX_SAMPLE_ROWS=1000

# Limit workers
gunicorn -w 2 app:app

# Monitor memory
watch -n 1 free -h
```

### Issue: Slow inference
```bash
# Check artifact loading time
import time
start = time.time()
artifacts = load_artifacts(run_id)
print(f"Load time: {time.time() - start}s")

# Cache artifacts in memory
from functools import lru_cache

@lru_cache(maxsize=10)
def get_cached_model(run_id):
    return load_artifacts(run_id)
```

---

## Checklist Before Production

- [ ] Environment variables configured
- [ ] Database backed up
- [ ] SSL/TLS certificates installed
- [ ] Nginx configured and tested
- [ ] Gunicorn workers tuned for your hardware
- [ ] Error logging configured
- [ ] Monitoring/alerting setup
- [ ] Backup scripts scheduled
- [ ] Firewall rules configured
- [ ] CORS properly configured
- [ ] Artifact storage is persistent
- [ ] Load tested with expected traffic

---

## Useful Commands

```bash
# Check Python version
python3 --version

# Check available memory
free -h

# Monitor process
htop

# Check disk usage
du -sh *

# Check open ports
netstat -tuln

# View system logs
dmesg | tail -20
```

---

## Support

For deployment issues, check:
- Application logs
- System logs
- Network connectivity
- Resource limits (CPU, memory, disk)
- Firewall rules
- CORS headers

