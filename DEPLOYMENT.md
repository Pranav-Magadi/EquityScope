# EquityScope Deployment Guide

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)
```bash
chmod +x start_development.sh
./start_development.sh
```

### Option 2: Docker Deployment
```bash
docker-compose up -d
```

### Option 3: Manual Setup
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python start_server.py

# Frontend (new terminal)
cd frontend
npm install
npm start
```

## 🔧 Configuration

### Required Environment Variables
Create `backend/.env`:
```env
# AI Services (Optional but recommended)
ANTHROPIC_API_KEY=your_claude_api_key

# Kite Connect (Optional - for real-time Indian market data)
KITE_API_KEY=your_kite_api_key
KITE_API_SECRET=your_kite_api_secret
```

### API Key Setup

**Important**: For v3.1.0+, API keys must be configured through the application's Settings panel, not environment variables.

#### In-App Configuration (Recommended):
1. Launch the application using any method above
2. Navigate to Settings (⚙️ icon) in the top navigation
3. Configure API keys:
   - **Claude API Key**: Get from https://console.anthropic.com/
   - **Kite Connect**: Register at https://kite.trade/
4. Click "Save Configuration"
5. Page will refresh automatically to apply settings

#### Environment Variables (Fallback):
If you prefer environment variables, create `backend/.env`:
```env
ANTHROPIC_API_KEY=your_claude_api_key
KITE_API_KEY=your_kite_api_key
KITE_API_SECRET=your_kite_api_secret
```

**Note**: In-app configuration takes precedence over environment variables.

## 🌐 Production Deployment

### Using Docker (Recommended)
```bash
# Build and start services
docker-compose -f docker-compose.yml up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Manual Production Setup
```bash
# Backend production server
cd backend
pip install gunicorn
gunicorn app.main:app --host 0.0.0.0 --port 8000

# Frontend production build
cd frontend
npm run build
# Serve with nginx or your preferred web server
```

## 🔍 Health Checks

### Automated Health Check
```bash
./health_check.sh
```

### Manual Verification
- Backend: http://localhost:8000/health
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

## 🐛 Troubleshooting

### Port Conflicts
```bash
# Kill existing processes
lsof -ti:3000 | xargs kill -9
lsof -ti:8000 | xargs kill -9
```

### Dependency Issues
```bash
# Backend
cd backend && pip install --upgrade pip && pip install -r requirements.txt

# Frontend
cd frontend && rm -rf node_modules package-lock.json && npm install
```

### Performance Optimization
- Enable Redis caching for production
- Configure CDN for static assets
- Use environment-specific API keys
- Monitor with included health endpoints
