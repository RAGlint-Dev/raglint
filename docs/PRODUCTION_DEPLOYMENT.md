# Production Deployment Guide

## Deploying RAGlint to Production

Complete guide for deploying RAGlint dashboard and API.

---

## Prerequisites

- Python 3.9+
-  PostgreSQL 12+ (recommended) or SQLite
- 2GB RAM minimum (4GB recommended)
- HTTPS certificate (Let's Encrypt recommended)

---

## Option 1: Docker Deployment (Recommended)

### Step 1: Create Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
RUN pip install -e .[dashboard]

# Copy application
COPY raglint/ ./raglint/
COPY examples/ ./examples/

# Create user
RUN useradd -m raglint && chown -R raglint:raglint /app
USER raglint

# Expose port
EXPOSE 8000

# Run dashboard
CMD ["uvicorn", "raglint.dashboard.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 2: Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  raglint:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://raglint:password@db:5432/raglint
      - SECRET_KEY=${SECRET_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - db
    restart: unless-stopped
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=raglint
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=raglint
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - raglint
    restart: unless-stopped

volumes:
  postgres_data:
```

### Step 3: Deploy

```bash
# Generate secret key
export SECRET_KEY=$(openssl rand -hex 32)

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f raglint
```

---

## Option 2: Manual Deployment

### Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3.11 python3.11-venv postgresql nginx

# Create user
sudo useradd -m -s /bin/bash raglint
```

### Step 2: Application Setup

```bash
# Switch to raglint user
sudo su - raglint

# Clone repository
git clone https://github.com/yourusername/raglint.git
cd raglint

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install
pip install -e .[dashboard]

# Set environment variables
cat > .env << EOF
DATABASE_URL=postgresql://raglint:password@localhost:5432/raglint
SECRET_KEY=$(openssl rand -hex 32)
OPENAI_API_KEY=your_key_here
EOF
```

### Step 3: Database Setup

```bash
# Create database
sudo -u postgres psql << EOF
CREATE USER raglint WITH PASSWORD 'secure_password';
CREATE DATABASE raglint OWNER raglint;
GRANT ALL PRIVILEGES ON DATABASE raglint TO raglint;
EOF

# Run migrations (if any)
# python -m raglint migrate
```

### Step 4: Systemd Service

```ini
# /etc/systemd/system/raglint.service
[Unit]
Description=RAGlint Dashboard
After=network.target postgresql.service

[Service]
Type=notify
User=raglint
Group=raglint
WorkingDirectory=/home/raglint/raglint
Environment="PATH=/home/raglint/raglint/venv/bin"
EnvironmentFile=/home/raglint/raglint/.env
ExecStart=/home/raglint/raglint/venv/bin/uvicorn raglint.dashboard.app:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable raglint
sudo systemctl start raglint
sudo systemctl status raglint
```

### Step 5: Nginx Configuration

```nginx
# /etc/nginx/sites-available/raglint
server {
    listen 80;
    server_name raglint.example.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name raglint.example.com;
    
    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/raglint.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/raglint.example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Security headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Proxy to RAGlint
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support  
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # Static files (if needed)
    location /static/ {
        alias /home/raglint/raglint/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/raglint /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Step 6: SSL with Let's Encrypt

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d raglint.example.com

# Auto-renewal
sudo certbot renew --dry-run
```

---

## Option 3: Cloud Platforms

### AWS (Elastic Beanstalk)

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.11 raglint-app

# Create environment
eb create raglint-prod --database.engine postgres

# Deploy
eb deploy

# Open
eb open
```

### Google Cloud (App Engine)

```yaml
# app.yaml
runtime: python311

entrypoint: uvicorn raglint.dashboard.app:app --host 0.0.0.0 --port $PORT

env_variables:
  DATABASE_URL: postgresql://...
  SECRET_KEY: ...
```

```bash
gcloud app deploy
```

### Azure (App Service)

```bash
az webapp up \
  --name raglint-app \
  --resource-group raglint-rg \
  --runtime "PYTHON:3.11"
```

---

## Production Checklist

### Security
- [ ] SECRET_KEY properly set (32+ random chars)
- [ ] HTTPS enabled
- [ ] Security headers configured
- [ ] Database with strong password
- [ ] Firewall rules configured
- [ ] Rate limiting enabled
- [ ] CORS properly configured

### Performance
- [ ] PostgreSQL connection pool configured
- [ ] Static files cached
- [ ] Gzip compression enabled
- [ ] CDN for static assets (optional)
- [ ] Database indexes created
- [ ] Query optimization done

### Monitoring
- [ ] Error tracking (Sentry)
- [ ] Performance monitoring (New Relic/Datadog)
- [ ] Log aggregation (ELK/Splunk)
- [ ] Uptime monitoring (UptimeRobot)
- [ ] Alerts configured

### Backup
- [ ] Database backup strategy
- [ ] Automated daily backups
- [ ] Backup retention policy
- [ ] Restore procedure tested

### Maintenance
- [ ] Update strategy defined
- [ ] Rolling deployment configured
- [ ] Health check endpoint
- [ ] Graceful shutdown
- [ ] Zero-downtime deployment

---

## Environment Variables

**Required:**
```bash
DATABASE_URL=postgresql://user:password@host:5432/dbname
SECRET_KEY=your-secret-key-here
```

**Optional:**
```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=...
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=info
ENVIRONMENT=production
```

---

## Scaling

### Horizontal Scaling

```yaml
# docker-compose.yml with multiple workers
services:
  raglint:
    deploy:
      replicas: 3
    # ... rest of config
```

### Load Balancing

```nginx
# Nginx upstream
upstream raglint_backend {
    least_conn;
    server raglint1:8000;
    server raglint2:8000;
    server raglint3:8000;
}

server {
    location / {
        proxy_pass http://raglint_backend;
    }
}
```

---

## Monitoring & Logging

### Application Logs

```python
# raglint/config.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/raglint/app.log'),
        logging.StreamHandler()
    ]
)
```

### Health Check Endpoint

```python
# Already included in dashboard
GET /health
# Response: {"status": "healthy", "database": "connected"}
```

### Metrics

```python
# Prometheus metrics (if enabled)
GET /metrics
```

---

## Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check connection
psql -U raglint -d raglint -h localhost

# Check logs
sudo journalctl -u postgresql -n 50
```

### Application Not Starting
```bash
# Check logs
sudo journalctl -u raglint -n 50

# Check port
sudo netstat -tlnp | grep 8000

# Test manually
source venv/bin/activate
uvicorn raglint.dashboard.app:app --host 0.0.0.0 --port 8000
```

### High Memory Usage
```bash
# Monitor
htop

# Adjust workers
# In systemd service, add:
# Environment="WORKERS=2"  # Reduce workers
```

---

## Cost Optimization

### Database
- Use managed PostgreSQL (AWS RDS, Google Cloud SQL)
- Configure connection pooling
- Set appropriate instance size

### Compute
- Start with small instance (2GB RAM)
- Scale based on usage
- Use autoscaling if available

### Monitoring
- Use free tiers (New Relic, Datadog trial)
- Set up alerts for budget thresholds

**Estimated Monthly Cost:**
- Small deployment: $15-50/month
- Medium deployment: $100-200/month
- Large deployment: $500+/month

---

## Support

- Documentation: https://raglint.readthedocs.io
- GitHub Issues: https://github.com/yourusername/raglint/issues
- Email: support@raglint.ai
