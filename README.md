# QuantLink FREN Narrator

A production-ready cryptocurrency price narration platform with a modern React frontend and Flask API backend. Get real-time crypto prices with an intuitive dashboard and audio narration support.

## Features

- 🎨 **Modern React Frontend** with TypeScript and Tailwind CSS
- 🚀 **Fast cryptocurrency price fetching** from CoinGecko API
- 🎵 **Text-to-speech narration** for prices and custom text
- 📊 **Multiple cryptocurrency support** with price change data
- 🌐 **RESTful API** with comprehensive endpoints
- 🐳 **Docker-ready** for easy deployment
- ☁️ **Render deployment** for quick demos
- 📈 **Health monitoring** and logging
- 🔒 **Production security** with rate limiting and CORS

## Quick Start

### Option 1: Local Development

```bash
# Clone the repository
git clone https://github.com/yourusername/quantlink-fren-narrator.git
cd quantlink-fren-narrator

# Start development environment (builds frontend + starts backend)
./dev-start.sh

# Access the application
# Frontend: http://localhost:5000
# API: http://localhost:5000/api/
```

### Option 2: Development Mode (Frontend + Backend Separately)

```bash
# Terminal 1: Start backend API
python web_api.py --debug

# Terminal 2: Start frontend development server
cd frontend
npm install
npm run dev
# Frontend: http://localhost:5173 (with API proxy)
```

### Option 3: Render (Quick Demo)

**Perfect for sharing demos internally**

1. Push your code to GitHub
2. Connect your repo to [Render](https://render.com)
3. Deploy automatically using the included `render.yaml`
4. Your app will be live at `https://your-app.onrender.com`

### Option 4: Docker (Production)

```bash
# Build and run with Docker
docker build -t quantlink-narrator .
docker run -p 8000:8000 quantlink-narrator

# Or use the quick test script
./quick-deploy.sh
```

## Frontend Features

The React frontend provides:

- 📊 **Real-time price dashboard** with live crypto feeds
- 🎛️ **Interactive controls** for price fetching and narration
- 📈 **Price history visualization** with candlestick charts
- 🔊 **Audio narration controls** with customizable options
- 📱 **Responsive design** for desktop and mobile
- 🎨 **Modern UI/UX** with smooth animations

### Frontend Technology Stack

- **React 19** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **Custom components** for crypto visualization
- **API integration** with the Flask backend

## API Endpoints

### Health Check
```bash
GET /api/health
# Returns: {"status": "healthy", "version": "1.0.0"}
```

### Cryptocurrency Prices
```bash
# Single price
GET /api/crypto/price?crypto=bitcoin&currency=usd

# Multiple prices
GET /api/crypto/prices?cryptos=bitcoin,ethereum&currency=usd

# Price with 24h change
GET /api/crypto/price?crypto=bitcoin&with_24h_change=true
```

### Text-to-Speech Narration
```bash
# Narrate custom text
POST /api/narrator/text
{
  "text": "Hello world",
  "lang": "en",
  "slow": false,
  "return_audio": false
}

# Narrate crypto price
POST /api/narrator/crypto
{
  "crypto": "bitcoin",
  "currency": "usd",
  "with_24h_change": true,
  "return_audio": false
}

# Get audio file by ID
GET /api/narrator/audio/<file_id>
```

## Deployment Options

### 🎯 Render (Internal Demos)
- **Setup time:** 5 minutes
- **Cost:** Free tier available
- **Perfect for:** Quick demos, prototypes, team sharing

1. Connect your GitHub repo to [Render](https://render.com)
2. Render auto-detects the `render.yaml` configuration
3. Deploy with one click ✅
4. Features: Auto-deploy, SSL, monitoring

### 🐳 Docker (Production)
- **Setup time:** 15 minutes  
- **Cost:** Variable (depends on hosting)
- **Perfect for:** Production environments, full control

#### Local Testing
```bash
# Test Docker setup
./quick-deploy.sh
```

#### Production Deployment
```bash
# Docker Compose (recommended)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

#### Cloud Container Services
```bash
# Google Cloud Run
gcloud builds submit --tag gcr.io/PROJECT_ID/quantlink-narrator
gcloud run deploy --image gcr.io/PROJECT_ID/quantlink-narrator

# AWS/Azure - deploy to your preferred container service
```

## Configuration

### Environment Variables
Copy `env.example` to `.env` and customize:

```bash
# Production settings
FLASK_ENV=production
DEFAULT_CRYPTO_ID=bitcoin
DEFAULT_VS_CURRENCY=usd

# Docker settings
HOST=0.0.0.0
PORT=8000
WORKERS=4
```

### Security Features
- ✅ Rate limiting (10 requests/second)
- ✅ CORS protection
- ✅ Security headers
- ✅ Input validation
- ✅ Error handling

## Testing & Monitoring

### Automated Testing
```bash
# Test any deployment
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

### Health Checks & Logs
```bash
# Render: Built-in dashboard
# Docker: docker-compose logs -f
# Cloud: Provider log viewers
```

## Cost Comparison

| Platform | Setup Time | Monthly Cost | Best For |
|----------|------------|--------------|----------|
| Render | 5 minutes | $0 (free tier) | Demos, prototypes |
| Docker + VPS | 15 minutes | $5-20 | Production |
| Cloud Run | 10 minutes | Pay-per-use | Variable traffic |

## Development

### Project Structure
```
quantlink-fren-narrator/
├── frontend/               # React frontend application
│   ├── src/               # React source code
│   │   ├── components/    # React components
│   │   ├── App.tsx        # Main App component
│   │   └── main.tsx       # Entry point
│   ├── public/            # Public assets
│   ├── package.json       # Frontend dependencies
│   ├── vite.config.ts     # Vite configuration
│   └── dist/              # Built frontend (auto-generated)
├── src/                   # Backend core modules
│   ├── narrator.py        # Text-to-speech functionality
│   ├── price_fetcher.py   # Cryptocurrency price fetching
│   └── app_config.py      # Configuration management
├── static/                # Built frontend files (served by Flask)
├── web_api.py            # Main Flask application
├── wsgi.py               # WSGI entry point
├── dev-start.sh          # Development startup script
├── Dockerfile            # Multi-stage container build
├── docker-compose.yml    # Docker Compose setup
├── render.yaml           # Render deployment config
├── quick-deploy.sh       # Docker test script
└── requirements.txt      # Python dependencies
```

### Testing
```bash
# Run deployment tests
python test_deployment.py http://localhost:8000

# Test Docker locally
./quick-deploy.sh

# Manual API testing
curl http://localhost:8000/api/crypto/price?crypto=bitcoin
```

## Troubleshooting

### Render Issues
- Check build logs in Render dashboard
- Verify `render.yaml` configuration
- Ensure environment variables are set

### Docker Issues
- Check container logs: `docker logs <container_id>`
- Ensure all dependencies in requirements.txt
- Verify port mapping is correct

### API Issues
- Test health endpoint first: `/api/health`
- Check network connectivity to CoinGecko API
- Verify gTTS can connect for audio generation

## Which Should I Choose?

**Use Render when:**
- 🎯 Quick internal demos
- 🎯 Prototyping and testing
- 🎯 Want zero-config deployment
- 🎯 Sharing with team members

**Use Docker when:**
- 🎯 Production environments
- 🎯 Need full control over environment
- 🎯 Scaling requirements
- 🎯 Want consistent dev/prod environments

## Quick Deploy Steps

### For Internal Demo (Render):
1. `git push` to GitHub
2. Connect repo to Render
3. Deploy automatically ✅

### For Production (Docker):
1. `./quick-deploy.sh` (test locally)
2. Deploy to your cloud provider
3. Set up monitoring ✅

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Ready to deploy?** 
- **Quick demo:** Use Render 
- **Production:** Use Docker
Get your API running in minutes! 🚀
