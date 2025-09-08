import React, { useState, useCallback, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, TrendingUp, AlertCircle, Loader2, Zap, Activity, Wifi, Settings } from 'lucide-react';
import { CompanyHeader } from './QualitativeCards/CompanyHeader';
import { SWOTAnalysisCard } from './QualitativeCards/SWOTAnalysis';
import { NewsSentimentCard } from './QualitativeCards/NewsSentiment';
import { MarketLandscapeCard } from './QualitativeCards/MarketLandscape';
import { EmployeeVoiceCard } from './QualitativeCards/EmployeeVoice';
import { DCFCard } from './DCFValuation/DCFCard';
import ApiKeySettings from './Settings/ApiKeySettings';
import { EnhancedApiService, type DataSourceStatus } from '../services/enhancedApi';
import type { CompanyAnalysis, DashboardState } from '../types';
import type { SummaryResponse } from '../types/summary';

// Type guard to check if data is V3 Summary format
const isV3Summary = (data: any): data is SummaryResponse => {
  return data && 'analysis_mode' in data && 'fair_value_band' in data;
};

export const EnhancedDashboard: React.FC = () => {
  const [state, setState] = useState<DashboardState>({
    ticker: '',
    companyAnalysis: undefined,
    dcfResponse: undefined,
    dcfDefaults: undefined,
    loadingStates: {
      company: { isLoading: false },
      dcf: { isLoading: false }
    }
  });

  const [searchTicker, setSearchTicker] = useState('');
  const [dataSourceStatus, setDataSourceStatus] = useState<DataSourceStatus | null>(null);
  const [isOnline, setIsOnline] = useState(true);
  const [showSettings, setShowSettings] = useState(false);

  const updateLoadingState = useCallback((key: 'company' | 'dcf', loading: boolean, error?: string) => {
    setState(prev => ({
      ...prev,
      loadingStates: {
        ...prev.loadingStates,
        [key]: { isLoading: loading, error }
      }
    }));
  }, []);

  // Check data source status on mount
  useEffect(() => {
    const checkDataSources = async () => {
      try {
        const status = await EnhancedApiService.getDataSourceStatus();
        setDataSourceStatus(status);
      } catch (error) {
        console.error('Error checking data sources:', error);
        setIsOnline(false);
      }
    };

    checkDataSources();
  }, []);

  const fetchCompanyAnalysis = useCallback(async (ticker: string) => {
    try {
      updateLoadingState('company', true);
      
      // Try enhanced API first, then V3 API, then fallback to regular API
      let analysis: CompanyAnalysis | SummaryResponse;
      try {
        analysis = await EnhancedApiService.getEnhancedCompanyAnalysis(ticker);
      } catch (enhancedError) {
        console.warn('Enhanced API failed, trying V3 API:', enhancedError);
        try {
          // Try V3 simple summary as fallback
          const { ApiService } = await import('../services/api');
          analysis = await ApiService.getV3SimpleSummary(ticker);
        } catch (v3Error) {
          console.warn('V3 API failed, falling back to regular API:', v3Error);
          // Final fallback to regular API
          const { ApiService } = await import('../services/api');
          analysis = await ApiService.getCompanyAnalysis(ticker);
        }
      }
      
      setState(prev => ({
        ...prev,
        ticker,
        companyAnalysis: analysis
      }));
    } catch (error) {
      console.error('Error fetching company analysis:', error);
      updateLoadingState('company', false, 'Failed to fetch company data. Please check the ticker symbol.');
    } finally {
      updateLoadingState('company', false);
    }
  }, [updateLoadingState]);

  const handleSearch = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchTicker.trim()) return;

    const formattedTicker = searchTicker.toUpperCase().trim();
    
    // Add .NS suffix for NSE stocks if not present
    const ticker = formattedTicker.includes('.') ? formattedTicker : `${formattedTicker}.NS`;
    
    await fetchCompanyAnalysis(ticker);
  }, [searchTicker, fetchCompanyAnalysis]);

  const handleExampleClick = useCallback((ticker: string) => {
    setSearchTicker(ticker);
    fetchCompanyAnalysis(ticker);
  }, [fetchCompanyAnalysis]);

  const handleApiKeySave = useCallback(async (config: any) => {
    try {
      // Store configuration and update API service
      console.log('API keys updated:', config);
      
      // In a production deployment, you would:
      // 1. Send keys to backend securely
      // 2. Update API service configuration
      // 3. Refresh data source status
      
      // For now, just refresh the data source status
      const status = await EnhancedApiService.getDataSourceStatus();
      setDataSourceStatus(status);
    } catch (error) {
      console.error('Failed to update API keys:', error);
    }
  }, []);

  const getDataSourceIndicator = () => {
    if (!dataSourceStatus) return null;

    const { kite_available, enhanced_mode } = dataSourceStatus;
    
    if (enhanced_mode && kite_available) {
      return (
        <div className="flex items-center space-x-2 text-green-400">
          <Zap className="h-4 w-4" />
          <span className="text-xs font-medium">Real-time Mode</span>
        </div>
      );
    } else if (!isOnline) {
      return (
        <div className="flex items-center space-x-2 text-red-400">
          <Wifi className="h-4 w-4" />
          <span className="text-xs font-medium">Offline</span>
        </div>
      );
    } else {
      return (
        <div className="flex items-center space-x-2 text-yellow-400">
          <Activity className="h-4 w-4" />
          <span className="text-xs font-medium">Standard Mode</span>
        </div>
      );
    }
  };

  const isLoading = state.loadingStates.company.isLoading;
  const hasError = state.loadingStates.company.error;
  const hasData = state.companyAnalysis && !isLoading && !hasError;

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Header */}
      <header className="bg-slate-800 border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-primary-600 rounded-lg">
                <TrendingUp className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-slate-100">Qualitative Edge</h1>
                <p className="text-xs text-slate-400">Enhanced with Kite Connect Real-time Data</p>
              </div>
            </div>
            
            {/* Data Source Status */}
            <div className="flex items-center space-x-4">
              {getDataSourceIndicator()}
              <div className="text-xs text-slate-400">
                v2.0 {dataSourceStatus?.enhanced_mode ? '(Enhanced)' : '(Standard)'}
              </div>
              <button
                onClick={() => setShowSettings(true)}
                className="p-2 hover:bg-slate-700 rounded-lg transition-colors group"
                title="API Settings"
              >
                <Settings className="h-5 w-5 text-slate-400 group-hover:text-white transition-colors" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="text-center mb-6">
            <h2 className="text-3xl font-bold text-slate-100 mb-2">
              Real-time Company Analysis
            </h2>
            <p className="text-slate-400 max-w-2xl mx-auto">
              Enter an NSE ticker symbol to get {dataSourceStatus?.enhanced_mode ? 'real-time' : 'comprehensive'} analysis 
              with AI-powered insights and interactive DCF valuation
            </p>
            
            {/* Enhanced Features Badge */}
            {dataSourceStatus?.enhanced_mode && (
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className="inline-flex items-center space-x-2 bg-green-900/20 border border-green-500/30 rounded-full px-4 py-2 mt-2"
              >
                <Zap className="h-4 w-4 text-green-400" />
                <span className="text-sm text-green-300 font-medium">
                  Live market data • Intraday charts • Market depth
                </span>
              </motion.div>
            )}
          </div>

          <form onSubmit={handleSearch} className="max-w-md mx-auto">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-slate-400" />
              <input
                type="text"
                value={searchTicker}
                onChange={(e) => setSearchTicker(e.target.value)}
                placeholder="Enter NSE ticker (e.g., RELIANCE, TCS, INFY)"
                className="w-full pl-10 pr-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 placeholder-slate-400 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={isLoading || !searchTicker.trim()}
                className="absolute right-2 top-1/2 transform -translate-y-1/2 btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  'Analyze'
                )}
              </button>
            </div>
          </form>

          {/* Example Tickers */}
          <div className="text-center mt-4">
            <p className="text-sm text-slate-400 mb-2">Try these examples:</p>
            <div className="flex flex-wrap justify-center gap-2">
              {['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ITC.NS'].map((ticker) => (
                <button
                  key={ticker}
                  onClick={() => handleExampleClick(ticker)}
                  disabled={isLoading}
                  className="px-3 py-1 bg-slate-700 hover:bg-slate-600 text-slate-300 text-xs rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {ticker.replace('.NS', '')}
                </button>
              ))}
            </div>
          </div>
        </motion.div>

        {/* API Status Alert */}
        {!isOnline && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="mb-8"
          >
            <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <AlertCircle className="h-5 w-5 text-red-400" />
                <div className="text-red-300">
                  API connection unavailable. Some features may not work properly.
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* Error State */}
        <AnimatePresence>
          {hasError && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-8"
            >
              <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-4">
                <div className="flex items-center space-x-2">
                  <AlertCircle className="h-5 w-5 text-red-400" />
                  <div className="text-red-300">{hasError}</div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Loading State */}
        <AnimatePresence>
          {isLoading && !hasData && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="text-center py-12"
            >
              <Loader2 className="h-8 w-8 text-primary-400 animate-spin mx-auto mb-4" />
              <div className="text-slate-300 mb-2">
                Analyzing {searchTicker}... 
                {dataSourceStatus?.enhanced_mode && (
                  <span className="text-green-400 ml-2">(Real-time mode)</span>
                )}
              </div>
              <div className="text-sm text-slate-400">
                {dataSourceStatus?.enhanced_mode 
                  ? 'Fetching live market data and generating insights'
                  : 'Fetching financial data and generating insights'
                }
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Analysis Results */}
        <AnimatePresence>
          {hasData && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-8"
            >
              {/* Company Header */}
              <CompanyHeader
                ticker={state.ticker!}
                companyAnalysis={state.companyAnalysis!}
              />

              {/* Section 1: Qualitative Analysis */}
              <div>
                <motion.h2
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="text-2xl font-bold text-slate-100 mb-6"
                >
                  Qualitative Analysis
                </motion.h2>
                
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <SWOTAnalysisCard 
                    ticker={state.ticker!}
                    companyAnalysis={state.companyAnalysis!}
                  />
                  <NewsSentimentCard 
                    ticker={state.ticker!}
                    companyAnalysis={state.companyAnalysis!}
                  />
                  <MarketLandscapeCard 
                    ticker={state.ticker!}
                    companyAnalysis={state.companyAnalysis!}
                  />
                  <EmployeeVoiceCard 
                    ticker={state.ticker!}
                    companyAnalysis={state.companyAnalysis!}
                  />
                </div>
              </div>

              {/* Section 2: Enhanced DCF Valuation */}
              <div>
                <motion.h2
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 }}
                  className="text-2xl font-bold text-slate-100 mb-6 flex items-center space-x-2"
                >
                  <span>Interactive DCF Valuation</span>
                  {dataSourceStatus?.enhanced_mode && (
                    <div className="flex items-center space-x-1 text-green-400">
                      <Zap className="h-5 w-5" />
                      <span className="text-sm font-normal">Enhanced</span>
                    </div>
                  )}
                </motion.h2>
                
                <DCFCard 
                  ticker={state.ticker!} 
                  currentPrice={isV3Summary(state.companyAnalysis!) ? 
                    state.companyAnalysis!.fair_value_band.current_price : 
                    state.companyAnalysis?.stock_price?.current_price
                  }
                />
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Welcome State */}
        {!hasData && !isLoading && !hasError && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-16"
          >
            <div className="mb-8">
              <div className="w-24 h-24 bg-primary-900/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <TrendingUp className="h-12 w-12 text-primary-400" />
              </div>
              <h3 className="text-xl font-semibold text-slate-200 mb-2">
                Ready to Analyze
              </h3>
              <p className="text-slate-400 max-w-md mx-auto">
                Enter a ticker symbol above to get started with comprehensive company analysis and DCF valuation
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-4xl mx-auto">
              {[
                {
                  title: dataSourceStatus?.enhanced_mode ? 'Real-time Data' : 'AI-Powered SWOT',
                  description: dataSourceStatus?.enhanced_mode 
                    ? 'Live market quotes, intraday charts, and market depth analysis'
                    : 'Strategic analysis of strengths, weaknesses, opportunities, and threats'
                },
                {
                  title: 'News Sentiment',
                  description: 'Real-time sentiment analysis of recent news and market updates'
                },
                {
                  title: 'Enhanced DCF',
                  description: dataSourceStatus?.enhanced_mode
                    ? 'Real-time valuation model with live price updates and enhanced accuracy'
                    : 'Real-time valuation model with adjustable assumptions and sensitivity analysis'
                },
                {
                  title: 'Market Intelligence',
                  description: dataSourceStatus?.enhanced_mode
                    ? 'Live market status, portfolio tracking, and peer comparisons'
                    : 'Competitive positioning and industry trend analysis'
                }
              ].map((feature, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 + index * 0.1 }}
                  className={`border rounded-lg p-4 ${
                    dataSourceStatus?.enhanced_mode
                      ? 'bg-green-900/10 border-green-500/30'
                      : 'bg-slate-800 border-slate-700'
                  }`}
                >
                  <h4 className="font-medium text-slate-200 mb-2 flex items-center space-x-2">
                    <span>{feature.title}</span>
                    {dataSourceStatus?.enhanced_mode && index === 0 && (
                      <Zap className="h-3 w-3 text-green-400" />
                    )}
                  </h4>
                  <p className="text-sm text-slate-400">{feature.description}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </main>

      {/* API Key Settings Modal */}
      <ApiKeySettings
        isOpen={showSettings}
        onClose={() => setShowSettings(false)}
        onSave={handleApiKeySave}
      />
    </div>
  );
};