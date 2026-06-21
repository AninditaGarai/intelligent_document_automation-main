# Deployment Guide

This document provides comprehensive instructions for deploying the Intelligent Document Automation application to production environments.

## Table of Contents

1. [Deployment Prerequisites](#deployment-prerequisites)
2. [Environment Configuration](#environment-configuration)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Monitoring and Maintenance](#monitoring-and-maintenance)
6. [Troubleshooting](#troubleshooting)

---

## Deployment Prerequisites

### System Requirements

- **CPU**: 2+ cores recommended
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 10GB free space
- **OS**: Linux (Ubuntu 20.04+ recommended), Windows Server 2019+, or macOS

### Software Requirements

- Docker 20.10+
- Docker Compose 1.29+
- Python 3.9+ (for non-Docker deployment)
- Tesseract OCR
- Poppler utilities

---

## Environment Configuration

### Production Environment Variables

Create a `.env` file in the project root with the following production-ready configuration:

```bash
# Application
APP_NAME=Intelligent Document Automation
APP_VERSION=1.0.0
DEBUG=false

# Server
HOST=0.0.0.0
PORT=5000
MAX_CONTENT_LENGTH=26214400

# Security
SECRET_KEY=your-secret-key-here-generate-with-openssl-rand-hex-32

# File Upload
MAX_FILE_SIZE=26214400
MAX_FILES_PER_UPLOAD=10

# Processing
OCR_ENGINE=tesseract
OCR_DPI=200
OCR_LANGUAGE=eng

# Matching
PATTERN_SCORE_WEIGHT=0.6
SEMANTIC_SCORE_WEIGHT=0.4
MATCH_DECISION_THRESHOLD=0.75

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### Generating a Secure Secret Key

```bash
# Generate a secure random secret key
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Docker Deployment

### Building the Production Image

```bash
# Build the image
docker build -t intelligent-document-automation:latest .

# Tag with version
docker tag intelligent-document-automation:latest intelligent-document-automation:1.0.0
```

### Running with Docker Compose

```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

### Docker Compose Production Configuration

Update `docker-compose.yml` for production:

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./web_runs:/app/web_runs
      - ./logs:/app/logs
    environment:
      - DEBUG=false
      - LOG_LEVEL=INFO
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

---

## Cloud Deployment

### AWS Deployment

#### Using AWS ECS

1. **Push Docker Image to ECR**
   ```bash
   # Login to ECR
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
   
   # Tag image
   docker tag intelligent-document-automation:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/intelligent-document-automation:latest
   
   # Push image
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/intelligent-document-automation:latest
   ```

2. **Create ECS Task Definition**
   ```json
   {
     "family": "intelligent-document-automation",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "512",
     "memory": "2048",
     "containerDefinitions": [
       {
         "name": "app",
         "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/intelligent-document-automation:latest",
         "portMappings": [
           {
             "containerPort": 5000,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {
             "name": "DEBUG",
             "value": "false"
           }
         ],
         "logConfiguration": {
           "logDriver": "awslogs",
           "options": {
             "awslogs-group": "/ecs/intelligent-document-automation",
             "awslogs-region": "us-east-1",
             "awslogs-stream-prefix": "ecs"
           }
         }
       }
     ]
   }
   ```

#### Using AWS EC2

1. **Launch EC2 Instance**
   - Choose Ubuntu 20.04 LTS
   - Select t3.medium or larger instance type
   - Configure security group to allow port 5000

2. **Install Docker**
   ```bash
   sudo apt-get update
   sudo apt-get install -y docker.io docker-compose
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

3. **Deploy Application**
   ```bash
   git clone <repository-url>
   cd intelligent-document-automation
   docker-compose up -d
   ```

### Google Cloud Platform Deployment

#### Using Google Cloud Run

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/<project-id>/intelligent-document-automation

# Deploy to Cloud Run
gcloud run deploy intelligent-document-automation \
  --image gcr.io/<project-id>/intelligent-document-automation \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Azure Deployment

#### Using Azure Container Instances

```bash
# Create resource group
az group create --name intelligent-doc-automation --location eastus

# Create container instance
az container create \
  --resource-group intelligent-doc-automation \
  --name intelligent-document-automation \
  --image <your-registry>/intelligent-document-automation:latest \
  --cpu 2 \
  --memory 4 \
  --ports 5000 \
  --environment-variables DEBUG=false LOG_LEVEL=INFO
```

---

## Monitoring and Maintenance

### Health Checks

The application provides a health check endpoint at `/health`:

```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "service": "Intelligent Document Automation",
  "checks": {
    "database": "not_configured",
    "storage": "available",
    "logging": "available"
  }
}
```

### Log Management

Logs are stored in the `logs/` directory:
- `document_automation.log`: General application logs
- `errors.log`: Error-specific logs

View logs:
```bash
# View recent logs
tail -f logs/document_automation.log

# View error logs
tail -f logs/errors.log
```

### Backup Strategy

1. **Backup Configuration Files**
   ```bash
   tar -czf config-backup-$(date +%Y%m%d).tar.gz .env config.yaml
   ```

2. **Backup Processed Documents**
   ```bash
   tar -czf documents-backup-$(date +%Y%m%d).tar.gz web_runs/
   ```

3. **Automated Backup Script**
   ```bash
   # Create backup script
   cat > backup.sh << 'EOF'
   #!/bin/bash
   DATE=$(date +%Y%m%d)
   tar -czf /backup/config-$DATE.tar.gz .env config.yaml
   tar -czf /backup/documents-$DATE.tar.gz web_runs/
   # Keep last 7 days of backups
   find /backup -name "*.tar.gz" -mtime +7 -delete
   EOF
   
   chmod +x backup.sh
   
   # Add to crontab for daily backups
   crontab -e
   # Add: 0 2 * * * /path/to/backup.sh
   ```

---

## Troubleshooting

### Common Issues

#### 1. Tesseract Not Found

**Error**: `TesseractNotFoundError`

**Solution**:
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows
# Download from https://github.com/UB-Mannheim/tesseract/wiki
```

#### 2. Memory Issues

**Error**: `MemoryError` or application crashes

**Solution**:
- Increase Docker memory limit
- Reduce `MAX_FILES_PER_UPLOAD` in configuration
- Process files in smaller batches

#### 3. Port Already in Use

**Error**: `Address already in use`

**Solution**:
```bash
# Find process using port 5000
lsof -i :5000

# Kill the process
kill -9 <PID>

# Or change the port in .env
PORT=5001
```

#### 4. Permission Denied

**Error**: `PermissionError` when accessing directories

**Solution**:
```bash
# Fix permissions
chmod -R 755 web_runs/
chmod -R 755 logs/
```

### Performance Optimization

1. **Enable Caching**
   - Configure Redis for session caching
   - Use CDN for static assets

2. **Load Balancing**
   - Deploy multiple instances behind a load balancer
   - Use Nginx as reverse proxy

3. **Database Optimization**
   - Add database for persistent storage
   - Implement connection pooling

---

## Security Considerations

### Production Security Checklist

- [ ] Change default `SECRET_KEY`
- [ ] Enable HTTPS/TLS
- [ ] Configure firewall rules
- [ ] Set up regular security updates
- [ ] Enable audit logging
- [ ] Implement rate limiting
- [ ] Use environment variables for sensitive data
- [ ] Regular security scans

### SSL/TLS Configuration

Using Nginx as reverse proxy with SSL:

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Scaling Strategy

### Horizontal Scaling

1. **Deploy Multiple Instances**
   ```bash
   docker-compose up -d --scale app=3
   ```

2. **Load Balancer Configuration**
   - Use Nginx, HAProxy, or cloud load balancer
   - Configure health checks
   - Implement session affinity if needed

### Vertical Scaling

1. **Increase Resources**
   - Upgrade to larger instance types
   - Add more CPU cores
   - Increase RAM allocation

2. **Optimize Processing**
   - Implement parallel processing
   - Use GPU acceleration for OCR
   - Optimize image processing pipeline

---

## Support and Maintenance

### Getting Help

- Check the [README.md](README.md) for general information
- Review logs in `logs/` directory
- Check health status at `/health` endpoint
- Review GitHub Issues for known problems

### Maintenance Schedule

- **Daily**: Monitor logs and health checks
- **Weekly**: Review error logs and performance metrics
- **Monthly**: Security updates and dependency updates
- **Quarterly**: Full system audit and backup verification

---

## Version Updates

### Updating to New Versions

1. **Backup Current Version**
   ```bash
   docker-compose down
   tar -czf backup-$(date +%Y%m%d).tar.gz .
   ```

2. **Pull Latest Code**
   ```bash
   git pull origin main
   ```

3. **Rebuild and Deploy**
   ```bash
   docker-compose build
   docker-compose up -d
   ```

4. **Verify Deployment**
   ```bash
   curl http://localhost:5000/health
   ```

### Rollback Procedure

If issues occur after update:

```bash
# Stop current deployment
docker-compose down

# Restore from backup
tar -xzf backup-YYYYMMDD.tar.gz

# Restart previous version
docker-compose up -d
```

---

## Contact and Support

For deployment issues or questions:
- Create an issue on GitHub
- Contact the development team
- Review troubleshooting section above
