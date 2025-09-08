# EquityScope - AI-Powered Financial Analysis Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18.0+-61dafb.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)

EquityScope is a comprehensive financial analysis platform that combines AI-powered insights with traditional valuation models to provide sophisticated equity research capabilities. Built with React frontend and FastAPI backend, it offers real-time market data integration, DCF valuation models, technical analysis, and intelligent caching for optimal performance.

## 🚀 Key Features

### 📊 **Comprehensive Analysis**
- **DCF Valuation Models**: Sector-specific models including Banking Excess Returns, EV/Revenue, and Traditional DCF
- **Technical Analysis**: Professional indicators (RSI, MACD, Bollinger Bands, Moving Averages)
- **AI-Powered Insights**: Claude-powered analysis for investment thesis, risk assessment, and market commentary
- **News Sentiment Analysis**: Real-time sentiment tracking from multiple sources

### 🤖 **AI Integration**
- **Smart Timeout Handling**: Optimized AI response times (<20 seconds)
- **Intelligent Caching**: 6-hour caching for AI insights to improve performance
- **Currency Accuracy**: Automatic ₹/$ detection based on stock exchange
- **Fallback Mechanisms**: Graceful degradation when AI services are unavailable

### 🔌 **Data Sources**
- **Primary**: Kite Connect API (real-time Indian market data)
- **Fallback**: yfinance (global market data)
- **Enhanced**: Multi-source news aggregation and sentiment analysis

### ⚡ **Performance Optimized**
- **Fast API Responses**: Optimized endpoints with intelligent caching
- **Real-time Updates**: Live market data integration
- **Responsive UI**: Modern React interface with smooth animations

## 🛠 Installation & Setup

### Prerequisites
- Python 3.9 or higher
- Node.js 16 or higher
- npm or yarn package manager

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/EquityScope.git
   cd EquityScope
   ```

2. **Run the automated setup script**
   ```bash
   chmod +x start_development.sh
   ./start_development.sh
   ```

   This script will:
   - Create Python virtual environment
   - Install backend dependencies
   - Install frontend dependencies
   - Start both servers automatically

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Manual Setup

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python start_server.py
```

#### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## 🔧 Configuration

### API Keys (Optional but Recommended)
For enhanced AI features, configure API keys in the application settings:

1. **Claude API Key**: For AI-powered analysis and insights
2. **Kite Connect API**: For real-time Indian market data
   - API Key and Secret from Zerodha Kite Connect
   - Requires HTTPS URLs for OAuth (use ngrok for local development)

### Environment Variables
Create a `.env` file in the backend directory:
```env
# AI Services
ANTHROPIC_API_KEY=your_claude_api_key_here

# Kite Connect (Optional)
KITE_API_KEY=your_kite_api_key
KITE_API_SECRET=your_kite_api_secret
KITE_ACCESS_TOKEN=your_access_token_after_auth
```

## 🐳 Docker Deployment

For production deployment using Docker:

```bash
docker-compose up -d
```

This will start:
- Backend API server
- Frontend React application  
- Redis for caching
- Nginx reverse proxy

## 📖 Usage Guide

### Basic Analysis
1. Enter a stock ticker (e.g., RELIANCE.NS, TCS.NS)
2. Select analysis mode (Simple or AI-Enhanced)
3. Review comprehensive analysis including:
   - Company overview and financials
   - DCF valuation with multiple models
   - Technical analysis with AI commentary
   - News sentiment and market insights

### Advanced Features
- **Peer Comparison**: Compare multiple stocks side-by-side
- **Sensitivity Analysis**: Test different assumption scenarios
- **Historical Performance**: Track valuation accuracy over time
- **Export Reports**: Generate PDF reports for analysis

## 🏗 Architecture

### Backend (FastAPI)
- **API Layer**: RESTful endpoints with automatic documentation
- **Services Layer**: Business logic and data processing
- **AI Integration**: Claude API for intelligent analysis
- **Data Sources**: Kite Connect, yfinance integration
- **Caching**: Redis-based intelligent caching system

### Frontend (React)
- **Modern UI**: Tailwind CSS with responsive design
- **State Management**: React hooks and context
- **Charts**: Interactive financial charts and visualizations
- **Real-time Updates**: WebSocket connections for live data

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📝 API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation.

### Key Endpoints
- `GET /api/company/{ticker}` - Company analysis
- `GET /api/v2/technical-analysis/{ticker}` - Technical analysis with AI
- `POST /api/dcf/insights/{ticker}` - DCF AI insights
- `GET /api/v3/summary/{ticker}/simple` - Simple mode analysis

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔧 Troubleshooting

### Common Issues

**Port conflicts:**
```bash
# Kill processes on ports 3000 and 8000
lsof -ti:3000 | xargs kill -9
lsof -ti:8000 | xargs kill -9
```

**Python dependencies:**
```bash
cd backend
pip install --upgrade pip
pip install -r requirements.txt
```

**Node dependencies:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Health Check
Use the included health check script:
```bash
./health_check.sh
```

## 📞 Support

For issues, questions, or contributions:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review the troubleshooting section above

## 🙏 Acknowledgments

- **FastAPI**: Modern, fast web framework for building APIs
- **React**: A JavaScript library for building user interfaces  
- **Claude AI**: Advanced AI capabilities for financial analysis
- **Kite Connect**: Real-time market data for Indian stocks
- **Tailwind CSS**: Utility-first CSS framework

---

**Built with ❤️ for the financial analysis community**
