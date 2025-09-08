import React, { useState, useCallback, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { TrendingUp, AlertCircle, Loader2, Search, RefreshCw, ArrowRight, Sparkles } from 'lucide-react';
import { SummaryBox } from './SummaryEngine/SummaryBox';
import { StockAutocomplete } from './common/StockAutocomplete';
import { ModeSelectionCards } from './ModeSelection/ModeSelectionCards';
import { ModeSelectionHeader } from './ModeSelection/ModeSelectionHeader';
import { DCFModelsCard } from './DCFValuation/DCFModelsCard';
import { v3ApiService } from '../services/v3ApiService';
import type { SummaryResponse, AnalysisMode, AppState } from '../types/summary';
import type { StockSymbol } from '../data/stockSymbols';

// V3 Dashboard implementing the new Summary Engine architecture
export const V3Dashboard: React.FC = () => {
  // Simplified v3 state structure (as per Migration Strategy)
  const [state, setState] = useState<AppState>({
    currentTicker: '',
    summaryData: null,
    analysisMode: 'simple',
    isLoading: false,
    error: null
  });

  const [searchTicker, setSearchTicker] = useState('');
  const [showTickerInput, setShowTickerInput] = useState(false);

  const updateState = useCallback((updates: Partial<AppState>) => {
    setState(prev => ({ ...prev, ...updates }));
  }, []);

  const fetchSummary = useCallback(async (ticker: string, mode?: AnalysisMode) => {
    const analysisMode = mode || state.analysisMode;
    
    try {
      updateState({ isLoading: true, error: null });
      
      const summaryData = await v3ApiService.getSummary(ticker, analysisMode);
      
      updateState({
        currentTicker: ticker,
        summaryData,
        analysisMode,
        isLoading: false
      });
    } catch (error) {
      console.error('Error fetching summary:', error);
      updateState({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Analysis failed'
      });
    }
  }, [state.analysisMode, updateState]);

  const handleSearch = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchTicker.trim()) return;

    const formattedTicker = searchTicker.toUpperCase().trim();
    const ticker = formattedTicker.includes('.') ? formattedTicker : `${formattedTicker}.NS`;
    
    await fetchSummary(ticker);
  }, [searchTicker, fetchSummary]);

  const handleStockSelect = useCallback(async (stock: StockSymbol) => {
    await fetchSummary(stock.ticker);
  }, [fetchSummary]);

  const handleModeToggle = useCallback(async (mode: AnalysisMode) => {
    if (!state.currentTicker) return;
    
    updateState({ analysisMode: mode });
    await fetchSummary(state.currentTicker, mode);
  }, [state.currentTicker, fetchSummary, updateState]);

  const handleRefresh = useCallback(async () => {
    if (!state.currentTicker) return;
    await fetchSummary(state.currentTicker);
  }, [state.currentTicker, fetchSummary]);

  const handleDemoSelect = useCallback(async (ticker: string) => {
    setSearchTicker(ticker);
    setShowTickerInput(true);
    await fetchSummary(ticker);
  }, [fetchSummary]);

  const handleModeSelect = useCallback((mode: AnalysisMode) => {
    updateState({ analysisMode: mode });
    setShowTickerInput(true);
  }, [updateState]);

  // Load demo data on mount for development
  useEffect(() => {
    // Uncomment for development with mock data
    // const mockData = v3ApiService.getMockSummary('TCS.NS', 'simple');
    // updateState({
    //   currentTicker: 'TCS.NS',
    //   summaryData: mockData,
    //   analysisMode: 'simple'
    // });
  }, []);

  const hasData = state.summaryData && !state.isLoading && !state.error;
  const hasError = state.error;

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
                <h1 className="text-xl font-bold text-slate-100">EquityScope v3</h1>
                <p className="text-xs text-slate-400">Summary Engine - Executive Investment Insights</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3 text-xs text-slate-400">
              <span>v3.0 Summary Engine</span>
              <div className="w-2 h-2 bg-green-400 rounded-full"></div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Mode Selection Screen */}
        <AnimatePresence>
          {!showTickerInput && (
            <motion.div
              key="mode-selection"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              {/* Header */}
              <ModeSelectionHeader selectedMode={state.analysisMode} />
              
              {/* Mode Selection Cards */}
              <ModeSelectionCards
                selectedMode={state.analysisMode}
                onModeSelect={handleModeSelect}
                disabled={state.isLoading}
              />
              
              {/* Demo Access */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.8, duration: 0.6 }}
                className="mt-12"
              >
                <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-8 max-w-4xl mx-auto text-center">
                  <div className="flex items-center justify-center space-x-2 mb-4">
                    <Sparkles className="h-6 w-6 text-yellow-300" />
                    <h3 className="text-2xl font-bold text-white">
                      Try Live Analysis Now
                    </h3>
                    <Sparkles className="h-6 w-6 text-yellow-300" />
                  </div>
                  
                  <p className="text-blue-100 mb-6 text-lg">
                    Experience the power of v3 Summary Engine with real market data
                  </p>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {[
                      { ticker: 'TCS.NS', name: 'TCS', icon: '💻', desc: 'IT Services Leader' },
                      { ticker: 'RELIANCE.NS', name: 'Reliance', icon: '⚡', desc: 'Energy & Telecom' },
                      { ticker: 'HDFCBANK.NS', name: 'HDFC Bank', icon: '🏦', desc: 'Banking Giant' }
                    ].map((stock) => (
                      <motion.button
                        key={stock.ticker}
                        onClick={() => handleDemoSelect(stock.ticker)}
                        disabled={state.isLoading}
                        className="bg-white/10 hover:bg-white/20 backdrop-blur-sm border border-white/20 text-white p-4 rounded-lg transition-all duration-200 disabled:opacity-50"
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                      >
                        <div className="text-2xl mb-2">{stock.icon}</div>
                        <div className="font-semibold mb-1">{stock.name}</div>
                        <div className="text-sm text-blue-100 opacity-75">{stock.desc}</div>
                      </motion.button>
                    ))}
                  </div>
                  
                  <div className="mt-6 text-sm text-blue-100 opacity-75">
                    Select any demo to see the {state.analysisMode === 'simple' ? 'Rule-Based' : 'AI Analyst'} analysis in action
                  </div>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Ticker Input Screen */}
        <AnimatePresence>
          {showTickerInput && !hasData && !state.isLoading && !hasError && (
            <motion.div
              key="ticker-input"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              {/* Back Button and Selected Mode */}
              <div className="flex items-center justify-between mb-8">
                <button
                  onClick={() => setShowTickerInput(false)}
                  className="flex items-center space-x-2 text-slate-400 hover:text-slate-300 transition-colors"
                >
                  <ArrowRight className="h-4 w-4 rotate-180" />
                  <span>Back to Mode Selection</span>
                </button>
                
                <div className={`flex items-center space-x-3 px-4 py-2 rounded-lg ${
                  state.analysisMode === 'simple' 
                    ? 'bg-blue-900/30 text-blue-300 border border-blue-500/30'
                    : 'bg-purple-900/30 text-purple-300 border border-purple-500/30'
                }`}>
                  <div className={`w-2 h-2 rounded-full ${
                    state.analysisMode === 'simple' ? 'bg-blue-400' : 'bg-purple-400'
                  }`}></div>
                  <span className="font-medium">
                    {state.analysisMode === 'simple' ? 'Rule-Based Analysis' : 'AI Analyst Insights'}
                  </span>
                </div>
              </div>

              {/* Step Progress Indicator */}
              <div className="flex items-center justify-center space-x-4 mb-12">
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 bg-green-600 rounded-full flex items-center justify-center text-white text-sm font-bold">
                    ✓
                  </div>
                  <span className="text-green-400 font-medium">Mode Selected</span>
                </div>
                
                <div className="w-12 h-px bg-blue-500"></div>
                
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm font-bold">
                    2
                  </div>
                  <span className="text-slate-300 font-medium">Enter Stock Ticker</span>
                </div>
                
                <div className="w-12 h-px bg-slate-600"></div>
                
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 bg-slate-600 rounded-full flex items-center justify-center text-slate-400 text-sm font-bold">
                    3
                  </div>
                  <span className="text-slate-500 font-medium">Get Analysis</span>
                </div>
              </div>

              {/* Ticker Input */}
              <div className="max-w-2xl mx-auto text-center">
                <h2 className="text-3xl font-bold text-slate-100 mb-4">
                  Enter Stock Ticker
                </h2>
                <p className="text-slate-400 mb-8">
                  Get comprehensive investment analysis for any NSE-listed stock
                </p>

                <form onSubmit={handleSearch} className="mb-8">
                  <div className="flex space-x-3">
                    <div className="flex-1">
                      <StockAutocomplete
                        value={searchTicker}
                        onChange={setSearchTicker}
                        onSelect={handleStockSelect}
                        placeholder="Enter stock name or ticker (e.g., TCS, RELIANCE, HDFCBANK)"
                        disabled={state.isLoading}
                      />
                    </div>
                    <button
                      type="submit"
                      disabled={state.isLoading || !searchTicker.trim()}
                      className="btn-primary whitespace-nowrap disabled:opacity-50 disabled:cursor-not-allowed px-8 py-3 font-semibold"
                    >
                      {state.isLoading ? (
                        <div className="flex items-center space-x-2">
                          <Loader2 className="h-5 w-5 animate-spin" />
                          <span>Analyzing...</span>
                        </div>
                      ) : (
                        <div className="flex items-center space-x-2">
                          <Search className="h-5 w-5" />
                          <span>Analyze</span>
                        </div>
                      )}
                    </button>
                  </div>
                </form>

                {/* Quick Access Stocks */}
                <div>
                  <p className="text-sm text-slate-400 mb-4">Popular stocks to try:</p>
                  <div className="flex flex-wrap justify-center gap-3">
                    {[
                      { ticker: 'RELIANCE.NS', name: 'Reliance', sector: 'Energy' },
                      { ticker: 'TCS.NS', name: 'TCS', sector: 'IT' },
                      { ticker: 'HDFCBANK.NS', name: 'HDFC Bank', sector: 'Banking' },
                      { ticker: 'INFY.NS', name: 'Infosys', sector: 'IT' },
                      { ticker: 'ITC.NS', name: 'ITC', sector: 'FMCG' },
                      { ticker: 'SBIN.NS', name: 'SBI', sector: 'Banking' }
                    ].map((stock) => (
                      <button
                        key={stock.ticker}
                        onClick={() => handleDemoSelect(stock.ticker)}
                        disabled={state.isLoading}
                        className="group bg-slate-800 hover:bg-slate-700 border border-slate-600 hover:border-slate-500 text-slate-300 hover:text-slate-100 px-4 py-2 rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <div className="font-medium">{stock.name}</div>
                        <div className="text-xs text-slate-500 group-hover:text-slate-400">{stock.sector}</div>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

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
                  {state.currentTicker && (
                    <button
                      onClick={handleRefresh}
                      className="ml-auto flex items-center space-x-1 text-sm text-red-400 hover:text-red-300 transition-colors"
                    >
                      <RefreshCw className="h-4 w-4" />
                      <span>Retry</span>
                    </button>
                  )}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Loading State */}
        <AnimatePresence>
          {state.isLoading && !hasData && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="text-center py-12"
            >
              <Loader2 className="h-8 w-8 text-primary-400 animate-spin mx-auto mb-4" />
              <div className="text-slate-300 mb-2">
                Generating {state.analysisMode} analysis for {searchTicker}...
              </div>
              <div className="text-sm text-slate-400">
                {state.analysisMode === 'simple' ? 'Applying quantitative rules...' : 'AI analyst processing data...'}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Summary Box - Main Content */}
        <AnimatePresence>
          {hasData && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <div className="space-y-8">
                <SummaryBox
                  ticker={state.currentTicker}
                  summary={state.summaryData!}
                  onModeToggle={handleModeToggle}
                  isLoading={state.isLoading}
                  onRefresh={handleRefresh}
                  hideAnalysisModeToggle={true}
                />
                
                {/* Single Tabbed DCF Card */}
                <DCFModelsCard
                  ticker={state.currentTicker}
                  summaryData={state.summaryData!}
                />
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Welcome State */}
        {!hasData && !state.isLoading && !hasError && (
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
                Ready for Analysis
              </h3>
              <p className="text-slate-400 max-w-md mx-auto">
                Enter a ticker symbol above to get executive-level investment insights
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-4xl mx-auto">
              {[
                {
                  title: 'Fair Value Band',
                  description: 'DCF-based valuation range with current price analysis'
                },
                {
                  title: 'Investment Label',
                  description: 'Clear bullish/bearish assessment with confidence scoring'
                },
                {
                  title: 'Three Lens Analysis',
                  description: 'Valuation, market signals, and business fundamentals'
                },
                {
                  title: 'Dual Mode Analysis',
                  description: 'Rule-based (fast) or AI-powered (comprehensive) insights'
                }
              ].map((feature, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 + index * 0.1 }}
                  className="bg-slate-800 border border-slate-700 rounded-lg p-4"
                >
                  <h4 className="font-medium text-slate-200 mb-2">{feature.title}</h4>
                  <p className="text-sm text-slate-400">{feature.description}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </main>
    </div>
  );
};