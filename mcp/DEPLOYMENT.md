# MCP Server Deployment Guide

**Feature**: 004-mcp-task-tools
**Date**: 2026-02-09
**Status**: Production Ready

## Overview

This guide provides instructions for deploying the MCP Server to a production environment.

## Prerequisites

- Python 3.11+
- Neon PostgreSQL database (configured and accessible)
- Server with at least 1GB RAM
- Network access to database

## Deployment Steps

### 1. Server Setup

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python 3.11+
sudo apt install python3.11 python3.11-venv python3-pip -y

# Create application directory
sudo mkdir -p /opt/mcp-server
sudo chown $USER:$USER /opt/mcp-server
cd /opt/mcp-server
```

### 2. Application Installation

```bash
# Clone repository or copy files
git clone <repository-url> .
cd mcp

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

```bash
# Create production .env file
cp .env.example .env

# Edit .env with production values
nano .env
```

**Production .env**:
```bash
DATABASE_URL=postgresql://user:password@ep-xxx.region.aws.neon.tech/neondb?sslmode=require
MCP_SERVER_PORT=8002
LOG_LEVEL=INFO
```

### 4. Database Verification

```bash
# Test database connection
python -c "from src.database import init_db; init_db()"
```

Expected output:
```
[INFO] Database connection established
```

### 5. Service Configuration (systemd)

Create systemd service file:

```bash
sudo nano /etc/systemd/system/mcp-server.service
```

**Service file content**:
```ini
[Unit]
Description=MCP Server for Task Management
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/mcp-server/mcp
Environment="PATH=/opt/mcp-server/mcp/venv/bin"
ExecStart=/opt/mcp-server/mcp/venv/bin/python src/server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable mcp-server
sudo systemctl start mcp-server
sudo systemctl status mcp-server
```

### 6. Firewall Configuration

```bash
# Allow MCP server port
sudo ufw allow 8002/tcp
sudo ufw reload
```

### 7. Monitoring Setup

```bash
# View logs
sudo journalctl -u mcp-server -f

# Check server status
sudo systemctl status mcp-server

# View application logs
tail -f /opt/mcp-server/mcp/logs/server.log
```

## Health Checks

### Manual Health Check

```bash
# Test server is running
curl http://localhost:8002/health

# Expected response
{"status": "healthy", "tools": 5, "database": "connected"}
```

### Automated Monitoring

Set up monitoring with your preferred tool (e.g., Prometheus, Datadog):

```bash
# Example: Check server every 60 seconds
*/1 * * * * curl -f http://localhost:8002/health || systemctl restart mcp-server
```

## Backup and Recovery

### Database Backups

Neon PostgreSQL provides automatic backups. Verify backup configuration:

```bash
# Check Neon dashboard for backup settings
# Recommended: Daily backups with 7-day retention
```

### Application Backups

```bash
# Backup configuration
sudo cp /opt/mcp-server/mcp/.env /opt/mcp-server/mcp/.env.backup

# Backup logs
sudo tar -czf mcp-logs-$(date +%Y%m%d).tar.gz /opt/mcp-server/mcp/logs/
```

## Scaling

### Horizontal Scaling

The MCP server is stateless and can be scaled horizontally:

```bash
# Deploy multiple instances behind a load balancer
# Each instance connects to the same database
# No session affinity required
```

### Vertical Scaling

Adjust connection pool size based on load:

```python
# In src/database.py
engine = create_engine(
    DATABASE_URL,
    pool_size=20,  # Increase for higher load
    max_overflow=40
)
```

## Security

### SSL/TLS Configuration

```bash
# Use reverse proxy (nginx) for SSL termination
sudo apt install nginx -y

# Configure nginx
sudo nano /etc/nginx/sites-available/mcp-server
```

**Nginx configuration**:
```nginx
server {
    listen 443 ssl;
    server_name mcp.example.com;

    ssl_certificate /etc/ssl/certs/mcp.crt;
    ssl_certificate_key /etc/ssl/private/mcp.key;

    location / {
        proxy_pass http://localhost:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Firewall Rules

```bash
# Allow only necessary ports
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 443/tcp
sudo ufw enable
```

## Troubleshooting

### Server Won't Start

```bash
# Check logs
sudo journalctl -u mcp-server -n 50

# Common issues:
# 1. Database connection failed - verify DATABASE_URL
# 2. Port already in use - check MCP_SERVER_PORT
# 3. Permission denied - check file ownership
```

### High Memory Usage

```bash
# Check memory usage
free -h

# Reduce connection pool size if needed
# Edit src/database.py: pool_size=5
```

### Database Connection Errors

```bash
# Test database connectivity
psql $DATABASE_URL -c "SELECT 1"

# Check Neon dashboard for database status
# Verify SSL mode is set to 'require'
```

## Rollback Procedure

```bash
# Stop service
sudo systemctl stop mcp-server

# Restore previous version
cd /opt/mcp-server
git checkout <previous-commit>

# Restart service
sudo systemctl start mcp-server
```

## Performance Tuning

### Database Optimization

```sql
-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_user_task ON tasks(user_id, id);
```

### Connection Pool Tuning

Monitor connection usage and adjust:

```python
# Increase for high concurrency
pool_size=20
max_overflow=40

# Decrease for low memory environments
pool_size=5
max_overflow=10
```

## Maintenance

### Log Rotation

```bash
# Configure logrotate
sudo nano /etc/logrotate.d/mcp-server
```

**Logrotate configuration**:
```
/opt/mcp-server/mcp/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

### Updates

```bash
# Pull latest changes
cd /opt/mcp-server
git pull origin main

# Restart service
sudo systemctl restart mcp-server
```

## Support

For issues or questions:
1. Check server logs: `/opt/mcp-server/mcp/logs/server.log`
2. Review systemd logs: `sudo journalctl -u mcp-server`
3. Verify database connectivity
4. Check MCP SDK version compatibility
