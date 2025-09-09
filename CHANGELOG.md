# Changelog

All notable changes to EquityScope will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-09-09

### Fixed
- **yfinance Upgrade**: Updated from v0.2.28 to v0.2.65
  - Resolved Yahoo Finance API compatibility issues causing 400/404 errors
  - Fixed v3 summary endpoints that were failing due to rate limiting
  - Added new dependencies: curl-cffi, protobuf, peewee, platformdirs
  - Improved data reliability and error handling
- **WebSockets**: Updated from v12.0 to v15.0.1 for better compatibility
- **API Stability**: Enhanced error handling for external data source failures

### Changed
- Updated requirements.txt with latest yfinance dependencies
- Enhanced README.md with troubleshooting section for yfinance issues
- Improved data source reliability documentation

## [1.0.0] - 2025-09-08

### Added
- Initial release of EquityScope financial analysis platform
- AI-powered DCF valuation models with Claude integration
- Real-time market data integration via Kite Connect API
- Technical analysis with professional indicators (RSI, MACD, Bollinger Bands)
- News sentiment analysis with AI-powered insights
- Responsive React frontend with modern UI/UX
- FastAPI backend with comprehensive API documentation
- Docker deployment support
- Automated setup scripts for development
- Intelligent caching system for performance optimization
- Multi-mode analysis (Simple and AI-Enhanced)
- Currency-aware display (₹ for Indian stocks, $ for US stocks)

### Features
- **DCF Models**: Banking Excess Returns, EV/Revenue, Traditional DCF
- **AI Integration**: 20-second timeout optimization, fallback mechanisms
- **Data Sources**: Primary Kite Connect, fallback to yfinance
- **Performance**: 6-hour intelligent caching for AI insights
- **Security**: Environment-based API key management
- **Testing**: Comprehensive test suites for backend and frontend
- **Documentation**: Complete setup, deployment, and contribution guides

### Technical Stack
- **Backend**: FastAPI 0.104.1, Python 3.9+
- **Frontend**: React 18, TypeScript, Tailwind CSS
- **AI**: Claude (Anthropic) for financial analysis
- **Data**: Kite Connect API, yfinance
- **Deployment**: Docker, Docker Compose
- **Testing**: pytest, React Testing Library, Playwright

### Known Issues
- None at initial release

### Security
- API keys managed via environment variables
- Secure OAuth handling for Kite Connect
- No hardcoded secrets in codebase
