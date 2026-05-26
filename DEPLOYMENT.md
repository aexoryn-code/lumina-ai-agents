# Lumina AI Agents - Deployment Guide

Complete guide for deploying Lumina AI Agents to production.

---

## Prerequisites

- Docker & Docker Compose
- Domain name (optional)
- SSL certificate (recommended for production)
- API keys for AI providers

---

## Environment Configuration

### 1. Create Production Environment File

```bash
cp .env.example .env.production
```

### 2. Configure Environment Variables

Edit `.env.production`:

```bash
# Database
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=lumina_prod
POSTGRES_USER=lumina_prod
POSTGRES_PASSWORD=<strong-password>

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=<strong-password>

# Qdrant
QDRANT_HOST=qdrant
QDRANT_PORT=6333

# API Keys (REQUIRED)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
DEEPSEEK_API_KEY=...
MISTRAL_API_KEY=...
GROQ_API_KEY=...

# Application
APP_ENV=production
SECRET_KEY=<generate-strong-secret-key>
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_URL=https://yourdomain.com

# LiteLLM
LITELLM_MASTER_KEY=<generate-strong-key>
LITELLM_LOG_LEVEL=INFO

# Features
ENABLE_MEMORY=true
ENABLE_REFLECTION=true
ENABLE_TOKEN_OPTIMIZATION=true
MAX_PARALLEL_AGENTS=5
```

### 3. Generate Strong Secrets

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate LITELLM_MASTER_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Docker Deployment

### Option 1: Docker Compose (Recommended)

**1. Build and start services:**

```bash
docker-compose -f docker-compose.yml --env-file .env.production up -d --build
```

**2. Check service health:**

```bash
docker-compose ps
docker-compose logs -f
```

**3. Run database migrations:**

```bash
docker-compose exec backend alembic upgrade head
```

### Option 2: Docker Swarm

**1. Initialize swarm:**

```bash
docker swarm init
```

**2. Deploy stack:**

```bash
docker stack deploy -c docker-compose.yml lumina
```

**3. Check services:**

```bash
docker service ls
docker service logs lumina_backend
```

---

## Kubernetes Deployment

### 1. Create Namespace

```bash
kubectl create namespace lumina
```

### 2. Create Secrets

```bash
kubectl create secret generic lumina-secrets \
  --from-literal=postgres-password=<password> \
  --from-literal=redis-password=<password> \
  --from-literal=secret-key=<secret> \
  --from-literal=openai-api-key=<key> \
  --from-literal=anthropic-api-key=<key> \
  -n lumina
```

### 3. Create ConfigMap

```bash
kubectl create configmap lumina-config \
  --from-literal=app-env=production \
  --from-literal=postgres-host=postgres \
  --from-literal=redis-host=redis \
  -n lumina
```

### 4. Deploy Services

```bash
kubectl apply -f k8s/ -n lumina
```

### 5. Check Deployment

```bash
kubectl get pods -n lumina
kubectl get services -n lumina
kubectl logs -f deployment/lumina-backend -n lumina
```

---

## Database Setup

### PostgreSQL

**1. Create database and user:**

```sql
CREATE DATABASE lumina_prod;
CREATE USER lumina_prod WITH PASSWORD 'strong-password';
GRANT ALL PRIVILEGES ON DATABASE lumina_prod TO lumina_prod;
```

**2. Run migrations:**

```bash
# Inside backend container
alembic upgrade head
```

### Redis

**1. Configure persistence:**

```bash
# In redis.conf
appendonly yes
appendfsync everysec
```

**2. Set password:**

```bash
# In redis.conf
requirepass your-strong-password
```

### Qdrant

**1. Configure storage:**

```bash
# In qdrant config
storage:
  storage_path: /qdrant/storage
```

---

## SSL/TLS Configuration

### Using Nginx Reverse Proxy

**1. Install Nginx:**

```bash
sudo apt-get install nginx certbot python3-certbot-nginx
```

**2. Configure Nginx:**

```nginx
# /etc/nginx/sites-available/lumina

server {
    listen 80;
    server_name yourdomain.com;

    location / {
        return 301 https://$server_name$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**3. Get SSL certificate:**

```bash
sudo certbot --nginx -d yourdomain.com
```

---

## Monitoring & Logging

### Application Logs

```bash
# Docker Compose
docker-compose logs -f backend
docker-compose logs -f frontend

# Kubernetes
kubectl logs -f deployment/lumina-backend -n lumina
```

### Health Checks

```bash
# Backend health
curl https://yourdomain.com/health

# API docs
curl https://yourdomain.com/docs
```

### Prometheus Metrics (Optional)

Add to `docker-compose.yml`:

```yaml
prometheus:
  image: prom/prometheus
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
  ports:
    - "9090:9090"

grafana:
  image: grafana/grafana
  ports:
    - "3001:3000"
```

---

## Backup & Recovery

### Database Backup

```bash
# Backup PostgreSQL
docker-compose exec postgres pg_dump -U lumina_prod lumina_prod > backup.sql

# Restore
docker-compose exec -T postgres psql -U lumina_prod lumina_prod < backup.sql
```

### Redis Backup

```bash
# Backup Redis
docker-compose exec redis redis-cli SAVE
docker cp lumina-redis:/data/dump.rdb ./redis-backup.rdb

# Restore
docker cp ./redis-backup.rdb lumina-redis:/data/dump.rdb
docker-compose restart redis
```

### Qdrant Backup

```bash
# Backup Qdrant
docker cp lumina-qdrant:/qdrant/storage ./qdrant-backup

# Restore
docker cp ./qdrant-backup lumina-qdrant:/qdrant/storage
docker-compose restart qdrant
```

---

## Scaling

### Horizontal Scaling

**1. Scale backend:**

```bash
docker-compose up -d --scale backend=3
```

**2. Add load balancer:**

```yaml
nginx:
  image: nginx:alpine
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
  ports:
    - "80:80"
  depends_on:
    - backend
```

### Vertical Scaling

Update resource limits in `docker-compose.yml`:

```yaml
backend:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 4G
      reservations:
        cpus: '1'
        memory: 2G
```

---

## Security Checklist

- [ ] Strong passwords for all services
- [ ] SSL/TLS enabled
- [ ] API keys stored securely
- [ ] Firewall configured
- [ ] Regular security updates
- [ ] Database backups automated
- [ ] Rate limiting enabled
- [ ] CORS properly configured
- [ ] Secrets not in version control
- [ ] Monitoring and alerting set up

---

## Troubleshooting

### Backend won't start

```bash
# Check logs
docker-compose logs backend

# Common issues:
# - Database not ready: wait for postgres health check
# - Missing API keys: check .env file
# - Port conflict: change API_PORT
```

### Frontend can't connect to backend

```bash
# Check NEXT_PUBLIC_API_URL
echo $NEXT_PUBLIC_API_URL

# Should be: https://yourdomain.com or http://localhost:8000
```

### Memory issues

```bash
# Check memory usage
docker stats

# Increase limits in docker-compose.yml
```

### Database connection errors

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Test connection
docker-compose exec backend python -c "from app.database import engine; print('OK')"
```

---

## Performance Optimization

### Database

- Enable connection pooling
- Add indexes for frequently queried fields
- Use read replicas for scaling

### Redis

- Enable persistence
- Configure maxmemory policy
- Use Redis Cluster for scaling

### Application

- Enable caching
- Use async operations
- Optimize token usage
- Implement rate limiting

---

## Maintenance

### Regular Tasks

**Daily:**
- Check logs for errors
- Monitor resource usage
- Verify backups

**Weekly:**
- Update dependencies
- Review security alerts
- Analyze performance metrics

**Monthly:**
- Security audit
- Database optimization
- Cost analysis

---

## Support

For issues or questions:
- GitHub Issues: [repository-url]
- Documentation: [docs-url]
- Email: support@yourdomain.com

---

**Deployed with Lumina AI Agents** 🚀
