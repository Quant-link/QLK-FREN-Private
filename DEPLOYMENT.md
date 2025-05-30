# QuantLink FREN Narrator - Deployment Guide

This guide covers the two main deployment strategies: **Render** for quick demos and **Docker** for production.

## Quick Demo Deployment: Render

**Perfect for:** Internal demos, prototypes, sharing with team
**Setup time:** 5 minutes
**Cost:** Free tier available

### Steps:
1. Push your code to GitHub
2. Connect your GitHub repo to [Render](https://render.com)
3. Create a new Web Service
4. Render will automatically detect the `render.yaml` configuration
5. Deploy with one click ✅

**Your API will be available at:** `https://your-app-name.onrender.com`

### Render Configuration (render.yaml)
```yaml
services:
  - type: web
    name: quantlink-fren-narrator
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn --bind 0.0.0.0:$PORT --workers 4 wsgi:app
    healthCheckPath: /api/health
```

**Render Features:**
- ✅ Automatic SSL certificates
- ✅ Auto-deploy on git push
- ✅ Built-in monitoring
- ✅ Easy environment variables
- ✅ Free tier (with sleep after 15min inactivity)

## Production Deployment: Docker

**Perfect for:** Production environments, full control, consistent deployments
**Setup time:** 15 minutes
**Cost:** Variable (depends on hosting)

### Option 1: Quick Local Test

```bash
# Test the Docker setup locally
./quick-deploy.sh

# Or manually:
docker build -t quantlink-narrator .
docker run -p 8000:8000 quantlink-narrator
```

### Option 2: Docker Compose (Recommended for Production)

```bash
# On your production server
git clone https://github.com/yourusername/quantlink-fren-narrator.git
cd quantlink-fren-narrator

# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

### Option 3: Cloud Container Services

#### Google Cloud Run
```bash
# Build and deploy to Cloud Run
gcloud builds submit --tag gcr.io/PROJECT_ID/quantlink-narrator
gcloud run deploy quantlink-narrator \
  --image gcr.io/PROJECT_ID/quantlink-narrator \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### AWS App Runner / ECS
1. Push Docker image to ECR
2. Create App Runner service pointing to your image
3. Configure auto-scaling and health checks

### Docker Production Features
- ✅ Consistent environment across dev/prod
- ✅ Easy scaling with orchestration
- ✅ Built-in health checks
- ✅ Resource isolation
- ✅ Easy rollbacks

## Configuration

### Environment Variables
Copy `env.example` to `.env` for local development:

```bash
# Production settings
FLASK_ENV=production
DEFAULT_CRYPTO_ID=bitcoin
DEFAULT_VS_CURRENCY=usd

# Server settings (Docker only)
HOST=0.0.0.0
PORT=8000
WORKERS=4
```

### Render Environment Variables
Set these in the Render dashboard:
- `FLASK_ENV=production`
- `PYTHONPATH=/opt/render/project/src`

## Testing Your Deployment

### Automated Testing
```bash
# Test any deployment
python test_deployment.py <base_url>

# Examples:
python test_deployment.py http://localhost:8000
python test_deployment.py https://your-app.onrender.com
```

### Manual Testing
```bash
# Health check
curl https://your-domain.com/api/health

# Price endpoint
curl "https://your-domain.com/api/crypto/price?crypto=bitcoin"

# Text narration
curl -X POST "https://your-domain.com/api/narrator/text" \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello world"}'
```

## Monitoring & Maintenance

### Health Checks
Both deployments include automatic health monitoring at `/api/health`

### Logs
```bash
# Render: Built-in log viewer in dashboard
# Docker: docker-compose logs -f
# Cloud: Provider-specific log viewers
```

### Updates
```bash
# Render: Auto-deploy on git push
# Docker: git pull && docker-compose up -d --build
```

## Cost Comparison

| Platform | Setup Time | Monthly Cost | Best For |
|----------|------------|--------------|----------|
| Render | 5 minutes | $0 (free tier) | Demos, prototypes |
| Docker + VPS | 15 minutes | $5-20 | Production |
| Cloud Run | 10 minutes | Pay-per-use | Variable traffic |

## Troubleshooting

### Render Issues
- Check the build logs in Render dashboard
- Ensure `render.yaml` is properly configured
- Verify environment variables are set

### Docker Issues
- Check container logs: `docker logs <container_id>`
- Ensure all dependencies in requirements.txt
- Verify port mapping is correct

### Common API Issues
- Test health endpoint first: `/api/health`
- Check network connectivity to CoinGecko API
- Verify gTTS can connect for audio generation

## Which Should I Choose?

**Use Render when:**
- 🎯 Quick internal demos
- 🎯 Prototyping and testing
- 🎯 Want zero-config deployment
- 🎯 Don't need 24/7 uptime

**Use Docker when:**
- 🎯 Production environments
- 🎯 Need full control over environment
- 🎯 Scaling requirements
- 🎯 Want consistent dev/prod environments

## Next Steps

1. **For quick demo:** Push to GitHub → Connect to Render → Deploy
2. **For production:** Set up Docker on your preferred cloud provider
3. **Set up monitoring:** Configure alerts for health checks
4. **Plan scaling:** Consider load balancing for high traffic

Both options are production-ready and include all necessary security features, health checks, and monitoring capabilities. 