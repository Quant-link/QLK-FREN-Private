# QuantLink FREN Narrator - Deployment Guide

## Overview

This guide covers deployment options for the QuantLink FREN Narrator Web API. We focus on two primary deployment strategies:

1. **Docker** - For production deployments with full control
2. **Render** - For quick demos and testing

## Docker Deployment (Production)

### Prerequisites
- Docker installed on your system
- Basic familiarity with Docker commands

### Quick Start

1. **Clone and navigate to the project:**
```bash
git clone <repository-url>
cd quantlink-fren-core-narrator
```

2. **Run the quick deployment script:**
```bash
./quick-deploy.sh
```

This script will:
- Build the Docker image
- Start the container on port 8000
- Run health checks
- Test API endpoints

### Manual Docker Deployment

1. **Build the image:**
```bash
docker build -t quantlink-narrator .
```

2. **Run the container:**
```bash
docker run -d -p 8000:8000 quantlink-narrator
```

3. **Access the application:**
- API: http://localhost:8000/api/health
- Web Interface: http://localhost:8000

### Production Considerations

- The application runs with 4 gunicorn workers
- Audio system uses dummy SDL driver for headless environments
- Health checks are configured for container orchestration
- All dependencies are pinned for reproducible builds

## Render Deployment (Demo/Testing)

Render provides a simple platform for deploying web applications with minimal configuration.

### Prerequisites
- Render account (free tier available)
- GitHub repository with your code

### Deployment Steps

1. **Connect GitHub repository to Render:**
   - Go to Render dashboard
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure the service:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT --workers 4 wsgi:app`

3. **Set environment variables:**
   - `FLASK_ENV=production`
   - `SDL_AUDIODRIVER=dummy` (Required for audio system)

4. **Deploy:**
   - Click "Create Web Service"
   - Wait for build and deployment to complete

### Using render.yaml (Automated)

The project includes a `render.yaml` file for automated deployment:

```yaml
services:
  - type: web
    name: quantlink-fren-narrator
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn --bind 0.0.0.0:$PORT --workers 4 wsgi:app
    healthCheckPath: /api/health
    envVars:
      - key: FLASK_ENV
        value: production
      - key: PYTHONPATH
        value: /opt/render/project/src
      - key: SDL_AUDIODRIVER
        value: dummy
```

Simply connect your repository and Render will use this configuration automatically.

### Render Limitations

- **CPU/Memory:** Free tier has limited resources
- **Sleep mode:** Free tier apps sleep after 15 minutes of inactivity
- **Build time:** Limited build minutes per month on free tier

## Testing Deployments

Use the provided test script to verify your deployment:

```bash
# Local Docker testing
python3 test_deployment.py http://localhost:8000

# Render testing (replace with your URL)
python3 test_deployment.py https://your-app.onrender.com
```

The test script verifies:
- Health endpoint functionality
- Crypto price API
- Audio system compatibility
- Text narration endpoint
- Crypto narration endpoint
- Web interface accessibility

## Troubleshooting

### Audio System Issues

**Problem:** `ALSA: Couldn't open audio device` errors in logs

**Solution:** Ensure `SDL_AUDIODRIVER=dummy` environment variable is set. This tells pygame to use a dummy audio driver instead of trying to access real audio hardware.

**Docker:** Already configured in Dockerfile
**Render:** Set in render.yaml or manually in dashboard

### Container Startup Issues

**Problem:** Container exits with status 1

**Solutions:**
1. Check that all dependencies are properly installed
2. Verify config.ini exists and is valid
3. Ensure port 8000 is not already in use
4. Check Docker logs: `docker logs <container-id>`

### API Endpoint Failures

**Problem:** 502/503 errors when accessing API

**Solutions:**
1. Verify health endpoint: `/api/health`
2. Check application logs for errors
3. Ensure gunicorn workers are starting properly
4. Verify all environment variables are set

### Network/CORS Issues

**Problem:** Frontend cannot connect to API

**Solutions:**
1. Check that Flask-CORS is properly configured
2. Verify API base URL in frontend matches deployment
3. Ensure ports are correctly mapped in Docker

## Monitoring and Maintenance

### Health Checks
- Docker includes health check configuration
- Health endpoint: `/api/health`
- Returns JSON with service status

### Logs
```bash
# Docker logs
docker logs <container-id>

# Render logs
# Available in Render dashboard under "Logs" tab
```

### Updates
1. Update code in repository
2. Rebuild Docker image or trigger Render redeploy
3. Run test script to verify functionality

## Environment Variables

| Variable | Purpose | Required | Default |
|----------|---------|----------|---------|
| `FLASK_ENV` | Flask environment | No | `development` |
| `SDL_AUDIODRIVER` | Audio driver for headless | Yes* | `dummy` |
| `PYTHONPATH` | Python module path | No | Auto-detected |

*Required for cloud deployments without audio hardware

## Support

For deployment issues:
1. Check the troubleshooting section above
2. Review application logs
3. Run the test script to identify specific failures
4. Ensure all prerequisites are met 