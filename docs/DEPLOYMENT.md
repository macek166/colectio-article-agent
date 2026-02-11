# Trading Card Content Generator - Deployment Guide

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Deployment Environments](#deployment-environments)
4. [Production Deployment](#production-deployment)
5. [Configuration Management](#configuration-management)
6. [Database Setup](#database-setup)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)
8. [Scaling Considerations](#scaling-considerations)
9. [Security Best Practices](#security-best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Overview

This guide provides comprehensive instructions for deploying the Trading Card Content Generator system to production environments. The system is designed to run as a Streamlit web application with backend integration to Neon PostgreSQL, OpenAI API, and Serper.dev.

### Architecture Summary
- **Frontend**: Streamlit web interface
- **Backend**: Python multi-agent system using CrewAI
- **Database**: Neon PostgreSQL (serverless)
- **External APIs**: OpenAI, Serper.dev, Context7 MCP
- **Integration Layer**: Kiro Power for Neon database access

---

## Prerequisites

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+ recommended), macOS, or Windows Server
- **Python**: Version 3.9 or higher
- **Memory**: Minimum 2GB RAM (4GB+ recommended for production)
- **Disk Space**: Minimum 1GB free space
- **Network**: Stable internet connection with access to external APIs

### Required Accounts
1. **Neon Database** - PostgreSQL hosting
   - Sign up: https://neon.tech
   - Free tier available for development
   - Paid plans for production workloads

2. **OpenAI Platform** - AI model access
   - Sign up: https://platform.openai.com
   - Requires payment method for API usage
   - Monitor usage and set billing limits

3. **Serper.dev** - SEO and web research
   - Sign up: https://serper.dev
   - Free tier: 2,500 searches/month
   - Paid plans for higher volume

4. **Kiro IDE** (for Kiro Power integration)
   - Ensure Kiro Power for Neon is activated
   - Power name: `neon`

---

## Deployment Environments

### Development Environment
- Local machine with Python virtual environment
- SQLite or local PostgreSQL for testing (optional)
- Development API keys with rate limits
- Debug logging enabled

### Staging Environment
- Cloud VM or container
- Neon database (development branch)
- Staging API keys
- INFO level logging
- Mirrors production configuration

### Production Environment
- Cloud VM, container, or serverless platform
- Neon database (production branch)
- Production API keys with monitoring
- WARNING level logging
- High availability configuration

---

## Production Deployment

### Option 1: Cloud VM Deployment (AWS EC2, Google Compute, Azure VM)

#### Step 1: Provision VM
```bash
# Example: AWS EC2 Ubuntu 22.04 LTS
# Instance type: t3.medium (2 vCPU, 4GB RAM)
# Storage: 20GB SSD
# Security group: Allow inbound on port 8501 (Streamlit)
```

#### Step 2: Install Dependencies
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python 3.9+
sudo apt install python3.9 python3.9-venv python3-pip -y

# Install system dependencies
sudo apt install build-essential libpq-dev -y
```

#### Step 3: Deploy Application
```bash
# Create application user
sudo useradd -m -s /bin/bash tcgapp
sudo su - tcgapp

# Clone repository
git clone <repository-url> tcg-content-generator
cd tcg-content-generator

# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 4: Configure Environment
```bash
# Create production .env file
cp .env.example .env
nano .env

# Set production values:
# - NEON_CONNECTION_STRING (production database)
# - OPENAI_API_KEY (production key)
# - SERPER_API_KEY (production key)
# - LOGGING_LEVEL=WARNING
# - MAX_RETRIES=3
```

#### Step 5: Initialize Database
```bash
# Run migrations
python -c "from src.tools.neon_db_client import NeonDBClient; from src.config.settings import Config; client = NeonDBClient(Config()); client.run_migrations()"

# Verify connection
python -c "from src.tools.neon_db_client import NeonDBClient; from src.config.settings import Config; print('Connected!' if NeonDBClient(Config()).verify_connection() else 'Failed')"
```

#### Step 6: Create Systemd Service
```bash
# Create service file
sudo nano /etc/systemd/system/tcg-generator.service
```

```ini
[Unit]
Description=TCG Content Generator
After=network.target

[Service]
Type=simple
User=tcgapp
WorkingDirectory=/home/tcgapp/tcg-content-generator
Environment="PATH=/home/tcgapp/tcg-content-generator/venv/bin"
ExecStart=/home/tcgapp/tcg-content-generator/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable tcg-generator
sudo systemctl start tcg-generator

# Check status
sudo systemctl status tcg-generator
```

#### Step 7: Configure Reverse Proxy (Nginx)
```bash
# Install Nginx
sudo apt install nginx -y

# Create Nginx configuration
sudo nano /etc/nginx/sites-available/tcg-generator
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/tcg-generator /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### Step 8: Configure SSL (Let's Encrypt)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
```

### Option 2: Docker Deployment

#### Step 1: Create Dockerfile
```dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Run application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### Step 2: Create docker-compose.yml
```yaml
version: '3.8'

services:
  tcg-generator:
    build: .
    ports:
      - "8501:8501"
    environment:
      - NEON_CONNECTION_STRING=${NEON_CONNECTION_STRING}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - SERPER_API_KEY=${SERPER_API_KEY}
      - KIRO_POWER_NAME=neon
      - LOGGING_LEVEL=WARNING
      - MAX_RETRIES=3
    volumes:
      - ./logs:/app/logs
      - ./docs:/app/docs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

#### Step 3: Deploy with Docker Compose
```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Option 3: Serverless Deployment (AWS Lambda + API Gateway)

**Note**: Streamlit is not ideal for serverless. Consider refactoring to use FastAPI for serverless deployments.

---

## Configuration Management

### Environment Variables

#### Production Configuration
```bash
# Database
NEON_CONNECTION_STRING=postgresql://user:password@prod-host.neon.tech/dbname?sslmode=require

# APIs
OPENAI_API_KEY=sk-prod-key-here
SERPER_API_KEY=prod-serper-key-here

# Kiro Power
KIRO_POWER_NAME=neon

# Topic Distribution
TOPIC_DISTRIBUTION_POKEMON=5
TOPIC_DISTRIBUTION_HOCKEY=3
TOPIC_DISTRIBUTION_SOCCER=2

# System
MAX_RETRIES=3
LOGGING_LEVEL=WARNING
PYLINT_MIN_SCORE=8.0

# Agent Configuration
AGENT_TEMPERATURE=0.7
AGENT_MAX_TOKENS=2000
```

### Secrets Management

#### Option 1: Environment Variables (Basic)
```bash
# Set in systemd service file or docker-compose.yml
# Not recommended for sensitive production data
```

#### Option 2: AWS Secrets Manager
```python
import boto3
import json

def get_secret(secret_name):
    client = boto3.client('secretsmanager', region_name='us-east-1')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

# Usage in config
secrets = get_secret('tcg-generator/prod')
OPENAI_API_KEY = secrets['openai_api_key']
```

#### Option 3: HashiCorp Vault
```bash
# Install Vault CLI
# Authenticate and retrieve secrets
vault kv get -field=openai_api_key secret/tcg-generator/prod
```

---

## Database Setup

### Neon Database Configuration

#### Step 1: Create Production Database
1. Log in to Neon console: https://console.neon.tech
2. Create new project: "TCG Generator Production"
3. Select region closest to your application
4. Note connection string

#### Step 2: Configure Connection Pooling
```bash
# Neon provides built-in connection pooling
# Use pooled connection string for better performance
# Format: postgresql://user:password@host/dbname?sslmode=require&pooler=true
```

#### Step 3: Run Migrations
```bash
# Execute migration scripts in order
psql $NEON_CONNECTION_STRING -f migrations/001_create_topics_table.sql
psql $NEON_CONNECTION_STRING -f migrations/002_create_content_table.sql
psql $NEON_CONNECTION_STRING -f migrations/003_create_context_table.sql
```

#### Step 4: Verify Schema
```bash
# Check tables
psql $NEON_CONNECTION_STRING -c "\dt"

# Check indexes
psql $NEON_CONNECTION_STRING -c "\di"

# Verify constraints
psql $NEON_CONNECTION_STRING -c "\d topics"
```

### Database Backup Strategy

#### Automated Backups (Neon)
- Neon provides automatic daily backups
- Retention: 7 days (free tier), 30 days (paid)
- Point-in-time recovery available

#### Manual Backup
```bash
# Export database
pg_dump $NEON_CONNECTION_STRING > backup_$(date +%Y%m%d).sql

# Restore from backup
psql $NEON_CONNECTION_STRING < backup_20231214.sql
```

---

## Monitoring and Maintenance

### Application Monitoring

#### Health Checks
```bash
# Streamlit health endpoint
curl http://localhost:8501/_stcore/health

# Database connectivity check
python -c "from src.tools.neon_db_client import NeonDBClient; from src.config.settings import Config; print('OK' if NeonDBClient(Config()).verify_connection() else 'FAIL')"
```

#### Log Monitoring
```bash
# View application logs
tail -f logs/tcg_generator.log

# View systemd service logs
sudo journalctl -u tcg-generator -f

# View Docker logs
docker-compose logs -f tcg-generator
```

#### Metrics to Track
- **Application Metrics**:
  - Topics processed per hour
  - Average processing time per topic
  - Success/failure rates by category
  - Agent execution times

- **System Metrics**:
  - CPU usage
  - Memory usage
  - Disk I/O
  - Network bandwidth

- **External API Metrics**:
  - OpenAI API calls and latency
  - Serper.dev API calls and quota
  - Neon database query performance

### Alerting

#### Basic Alerting (Email)
```python
# Add to src/utils/logger.py
import smtplib
from email.mime.text import MIMEText

def send_alert(subject, message):
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = 'alerts@your-domain.com'
    msg['To'] = 'admin@your-domain.com'
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('your-email', 'your-password')
        server.send_message(msg)
```

#### Advanced Monitoring (Prometheus + Grafana)
- Export metrics in Prometheus format
- Visualize with Grafana dashboards
- Set up alerting rules

### Maintenance Tasks

#### Daily
- Check application logs for errors
- Monitor API usage and costs
- Verify database connectivity

#### Weekly
- Review PROBLEMS.md for recurring issues
- Check disk space usage
- Update dependencies if security patches available

#### Monthly
- Review and optimize database queries
- Analyze topic generation patterns
- Update category-specific web sources if needed
- Review API costs and optimize usage

---

## Scaling Considerations

### Vertical Scaling
- Increase VM instance size (more CPU/RAM)
- Upgrade Neon database plan for better performance
- Optimize Python code for memory efficiency

### Horizontal Scaling
- Deploy multiple instances behind load balancer
- Use Redis for shared context management
- Implement message queue (Celery) for async processing
- Distribute topic processing across workers

### Database Scaling
- Neon automatically scales compute and storage
- Use read replicas for query-heavy workloads
- Implement caching layer (Redis) for frequently accessed data

### API Rate Limiting
- Implement request queuing for OpenAI API
- Use multiple Serper.dev API keys for higher throughput
- Cache web scraping results to reduce redundant requests

---

## Security Best Practices

### API Key Management
- Never commit API keys to version control
- Use environment variables or secrets manager
- Rotate API keys regularly (quarterly)
- Set up billing alerts to prevent unexpected charges

### Database Security
- Use SSL/TLS for all database connections
- Implement least-privilege access control
- Enable Neon IP allowlist if possible
- Regularly audit database access logs

### Application Security
- Keep dependencies up to date
- Run security scans (pip-audit, safety)
- Implement rate limiting on Streamlit interface
- Use HTTPS for all external communication

### Network Security
- Configure firewall rules (allow only necessary ports)
- Use VPC/private networks where possible
- Implement DDoS protection (Cloudflare, AWS Shield)
- Enable fail2ban for SSH brute-force protection

---

## Troubleshooting

### Common Production Issues

#### Issue 1: High Memory Usage
**Symptoms**: Application crashes, OOM errors

**Solutions**:
- Reduce topic distribution (fewer concurrent topics)
- Clear context more frequently
- Increase VM memory
- Implement pagination for large result sets

#### Issue 2: Slow Performance
**Symptoms**: Long processing times, timeouts

**Solutions**:
- Optimize database queries (add indexes)
- Implement caching for web scraping results
- Use Neon connection pooling
- Reduce AGENT_MAX_TOKENS if possible

#### Issue 3: API Rate Limiting
**Symptoms**: 429 errors from OpenAI or Serper.dev

**Solutions**:
- Implement exponential backoff (already in place)
- Reduce concurrent requests
- Upgrade API plan for higher limits
- Implement request queuing

#### Issue 4: Database Connection Failures
**Symptoms**: psycopg2.OperationalError

**Solutions**:
- Verify Neon database is active (auto-suspend after inactivity)
- Check connection string format
- Verify network connectivity
- Ensure Kiro Power is activated

#### Issue 5: Streamlit Session Issues
**Symptoms**: UI freezes, session state errors

**Solutions**:
- Restart Streamlit service
- Clear browser cache
- Check for memory leaks in session state
- Implement session timeout

### Emergency Procedures

#### Application Crash
```bash
# Check service status
sudo systemctl status tcg-generator

# View recent logs
sudo journalctl -u tcg-generator -n 100

# Restart service
sudo systemctl restart tcg-generator
```

#### Database Emergency
```bash
# Check database status in Neon console
# Restore from backup if needed
psql $NEON_CONNECTION_STRING < backup_latest.sql
```

#### API Key Compromise
1. Immediately revoke compromised key
2. Generate new API key
3. Update environment variables
4. Restart application
5. Review access logs for unauthorized usage

---

## Rollback Procedures

### Application Rollback
```bash
# Git rollback
git checkout <previous-commit-hash>

# Rebuild and restart
pip install -r requirements.txt
sudo systemctl restart tcg-generator
```

### Database Rollback
```bash
# Restore from backup
psql $NEON_CONNECTION_STRING < backup_before_migration.sql
```

---

## Performance Optimization

### Database Optimization
```sql
-- Add indexes for common queries
CREATE INDEX idx_topics_category ON topics(category);
CREATE INDEX idx_topics_status ON topics(status);
CREATE INDEX idx_content_topic_id ON content(topic_id);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM topics WHERE category = 'pokemon';
```

### Application Optimization
- Use connection pooling for database
- Implement caching for Context7 documentation
- Batch database operations where possible
- Optimize Pydantic model validation

### Monitoring Query Performance
```bash
# Enable slow query logging in Neon
# Review slow queries in Neon console
# Optimize queries with high execution time
```

---

## Disaster Recovery

### Backup Strategy
- **Database**: Daily automated backups via Neon
- **Application Code**: Version controlled in Git
- **Configuration**: Stored in secrets manager
- **Logs**: Archived to S3 or similar storage

### Recovery Time Objective (RTO)
- Target: 1 hour
- Steps: Provision new VM, deploy application, restore database

### Recovery Point Objective (RPO)
- Target: 24 hours
- Daily database backups ensure maximum 24-hour data loss

---

## Compliance and Auditing

### Data Retention
- Topics: Retained indefinitely
- Content: Retained indefinitely
- Logs: Retained for 90 days
- Backups: Retained for 30 days

### Audit Logging
- All database operations logged
- API calls tracked in DOCUMENTATION.md
- Errors tracked in PROBLEMS.md
- System events logged to syslog

---

## Support and Escalation

### Support Tiers
1. **Level 1**: Application logs and PROBLEMS.md
2. **Level 2**: System administrator review
3. **Level 3**: Developer intervention required

### Contact Information
- **Application Issues**: Check PROBLEMS.md and DOCUMENTATION.md
- **Database Issues**: Neon support (https://neon.tech/docs/introduction/support)
- **API Issues**: OpenAI support, Serper.dev support

---

**Last Updated:** December 2025  
**Version:** 1.0  
**Maintainer:** TCG Content Generator Team
