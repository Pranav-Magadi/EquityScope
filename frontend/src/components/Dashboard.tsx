import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { TrendingUp, AlertCircle, Loader2, Settings } from 'lucide-react';
import { SummaryCard } from './V3Cards/SummaryCard';
// import { ThreeLensAnalysis } from './V3Cards/ThreeLensAnalysis'; // Removed - not used in this dashboard
import { NewsSentimentCard } from './QualitativeCards/NewsSentiment';
import { DCFModelsCard } from './DCFValuation/DCFModelsCard';
import { TechnicalAnalysisCard } from './TechnicalAnalysis/TechnicalAnalysisCard';
import { FinancialAnalysisCard } from './FinancialAnalysis/FinancialAnalysisCard';
import { ModeSelectionCards } from './ModeSelection/ModeSelectionCards';
import { ApiService } from '../services/api';
import ApiKeySettings from './Settings/ApiKeySettings';
import type { DashboardState } from '../types';
import type { AnalysisMode, SummaryResponse } from '../types/summary';

export const Dashboard: React.FC = () => {
  // State Management
  const [selectedMode, setSelectedMode] = useState<AnalysisMode>('simple');
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
  const [showSettings, setShowSettings] = useState(false);
  
  // Dynamic Insights State - collected from different components
  const [dynamicInsights, setDynamicInsights] = useState({
    dcfInsights: null as any,
    financialMetrics: null as any,
    technicalInsights: null as any,
    sentimentInsights: null as any,
    priceData: null as any
  });

  const updateLoadingState = useCallback((key: 'company' | 'dcf', loading: boolean, error?: string) => {
    setState(prev => ({
      ...prev,
      loadingStates: {
        ...prev.loadingStates,
        [key]: { isLoading: loading, error }
      }
    }));
  }, []);

  // Callbacks to update dynamic insights from different components
  const updateDCFInsights = useCallback((data: any) => {
    console.log('📊 Dashboard received DCF insights update:', data);
    setDynamicInsights(prev => ({ ...prev, dcfInsights: data }));
  }, []);

  const updateFinancialMetrics = useCallback((data: any) => {
    setDynamicInsights(prev => ({ ...prev, financialMetrics: data }));
  }, []);

  const updateTechnicalInsights = useCallback((data: any) => {
    console.log('📊 Dashboard received technical insights update:', data);
    setDynamicInsights(prev => ({ ...prev, technicalInsights: data }));
  }, []);

  const updateSentimentInsights = useCallback((data: any) => {
    setDynamicInsights(prev => ({ ...prev, sentimentInsights: data }));
  }, []);

  const updatePriceData = useCallback((data: any) => {
    setDynamicInsights(prev => ({ ...prev, priceData: data }));
  }, []);

  const fetchCompanyAnalysis = useCallback(async (ticker: string) => {
    try {
      updateLoadingState('company', true);
      
      let analysis: SummaryResponse;
      if (selectedMode === 'simple') {
        analysis = await ApiService.getV3SimpleSummary(ticker);
      } else if (selectedMode === 'agentic') {
        analysis = await ApiService.getV3AgenticSummary(ticker);
      } else {
        analysis = await ApiService.getV3Summary(ticker, selectedMode || 'simple');
      }
      
      setState(prev => ({ 
        ...prev, 
        ticker, 
        companyAnalysis: analysis 
      }));
    } catch (error) {
      console.error('Error fetching V3 analysis:', error);
      updateLoadingState('company', false, 'Failed to fetch analysis. Please try again.');
    } finally {
      updateLoadingState('company', false);
    }
  }, [updateLoadingState, selectedMode]);

  const handleModeSelect = useCallback((mode: AnalysisMode) => {
    setSelectedMode(mode);
  }, []);

  const handleAnalyze = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchTicker.trim()) return;

    const formattedTicker = searchTicker.toUpperCase().trim();
    const finalTicker = formattedTicker.includes('.') ? formattedTicker : `${formattedTicker}.NS`;
    
    await fetchCompanyAnalysis(finalTicker);
  }, [searchTicker, fetchCompanyAnalysis]);

  // Type guard removed - using direct casting since we know it's V3 format

  const handleSettingsSave = useCallback(async (config: any) => {
    try {
      // Save API keys to backend
      const response = await ApiService.updateApiKeys(config);
      console.log('✅ API keys updated successfully:', response);
      
      // Force refresh of the page to re-trigger all AI components with new API keys
      window.location.reload();
      
    } catch (error) {
      console.error('❌ Failed to update API keys:', error);
      // Keep modal open on error so user can retry
    }
  }, []);

  const isLoading = state.loadingStates.company.isLoading;
  const hasError = state.loadingStates.company.error;
  const hasData = state.companyAnalysis && !isLoading && !hasError;

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Simplified Header */}
      <header className="bg-slate-800 border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg">
                <TrendingUp className="h-6 w-6 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-slate-100">EquityScope</h1>
            </div>
            
            {/* Settings Button */}
            <button
              onClick={() => setShowSettings(true)}
              className="flex items-center space-x-2 px-3 py-2 text-slate-300 hover:text-white hover:bg-slate-700 rounded-lg transition-colors"
              title="Configure API Keys"
            >
              <Settings className="h-4 w-4" />
              <span className="text-sm hidden sm:inline">Settings</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Mode Selection Cards */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-slate-100 text-center mb-2">
            Choose Analysis Mode
          </h2>
          <p className="text-slate-400 text-center mb-8">
            Select your preferred analysis approach
          </p>
          
          <ModeSelectionCards
            selectedMode={selectedMode}
            onModeSelect={handleModeSelect}
          />
        </div>

        {/* Search Section */}
        <div className="mb-8">
          <h3 className="text-xl font-semibold text-slate-200 text-center mb-4">
            Enter Stock Ticker
          </h3>
          
          <form onSubmit={handleAnalyze} className="max-w-md mx-auto">
            <div className="relative">
              <input
                type="text"
                value={searchTicker}
                onChange={(e) => setSearchTicker(e.target.value)}
                placeholder="Enter NSE ticker (e.g., RELIANCE, TCS, INFY)"
                className="w-full pl-4 pr-20 py-3 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 placeholder-slate-400 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={isLoading || !searchTicker.trim()}
                className="absolute right-2 top-1/2 transform -translate-y-1/2 px-4 py-1.5 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  'Analyse'
                )}
              </button>
            </div>
          </form>

          {/* Example Tickers */}
          <div className="text-center mt-4">
            <p className="text-sm text-slate-400 mb-2">Try these examples:</p>
            <div className="flex flex-wrap justify-center gap-2">
              {['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ITC'].map((ticker) => (
                <button
                  key={ticker}
                  onClick={() => {
                    setSearchTicker(ticker);
                    setTimeout(() => {
                      const event = { preventDefault: () => {} } as React.FormEvent;
                      handleAnalyze(event);
                    }, 100);
                  }}
                  disabled={isLoading}
                  className="px-3 py-1 bg-slate-700 hover:bg-slate-600 text-slate-300 text-sm rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {ticker}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Selected Mode Indicator */}
        <div className="text-center mb-8">
          <div className={`inline-flex items-center space-x-3 px-6 py-3 rounded-full border ${
            selectedMode === 'simple' 
              ? 'bg-blue-900/30 text-blue-300 border-blue-500/30' 
              : 'bg-purple-900/30 text-purple-300 border-purple-500/30'
          }`}>
            <div className={`w-3 h-3 rounded-full ${
              selectedMode === 'simple' ? 'bg-blue-400' : 'bg-purple-400'
            }`}></div>
            <span className="font-medium">
              {selectedMode === 'simple' ? 'Rule-Based Analysis (~15s)' : 'AI Analyst Insights (Comprehensive)'}
            </span>
          </div>
        </div>

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
          {isLoading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="text-center py-12"
            >
              <Loader2 className="h-8 w-8 text-primary-400 animate-spin mx-auto mb-4" />
              <div className="text-slate-300 mb-2">
                {selectedMode === 'simple' 
                  ? 'Running Rule-Based Analysis...' 
                  : 'AI Analyst Working...'
                }
              </div>
              <div className="text-sm text-slate-400">
                {selectedMode === 'simple' 
                  ? 'Calculating sector-specific DCF and weighted scoring (~15 seconds)' 
                  : 'Generating comprehensive investment thesis with market context'
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
              {/* 1. V3 Summary Box */}
              <SummaryCard 
                summaryData={state.companyAnalysis as SummaryResponse}
                dcfInsights={dynamicInsights.dcfInsights}
                financialMetrics={dynamicInsights.financialMetrics}
                technicalInsights={dynamicInsights.technicalInsights}
                sentimentInsights={dynamicInsights.sentimentInsights}
                priceData={dynamicInsights.priceData}
              />

              {/* 2. DCF Valuation Box */}
              <div>
                <motion.h2
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="text-2xl font-bold text-slate-100 mb-6"
                >
                  DCF Valuation Analysis
                </motion.h2>
                <DCFModelsCard 
                  ticker={state.ticker || ''}
                  summaryData={state.companyAnalysis as SummaryResponse}
                  onOpenSettings={() => setShowSettings(true)}
                  onDCFInsightsUpdate={updateDCFInsights}
                />
              </div>

              {/* 3. Technical Analysis - Full Charts & Indicators */}
              <TechnicalAnalysisCard 
                ticker={state.ticker || ''}
                useAgenticMode={selectedMode === 'agentic'}
                onTechnicalInsightsUpdate={updateTechnicalInsights}
                onPriceDataUpdate={updatePriceData}
              />


              {/* 5. Financial Analysis - 3-Tab Interface */}
              <FinancialAnalysisCard 
                ticker={state.ticker || ''} 
                useAgenticMode={selectedMode === 'agentic'}
                onFinancialMetricsUpdate={updateFinancialMetrics}
              />

              {/* 6. News Sentiment - Only show in Agentic mode */}
              {selectedMode === 'agentic' && (
                <div>
                  <motion.h2
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="text-2xl font-bold text-slate-100 mb-6"
                  >
                    News Sentiment Analysis
                  </motion.h2>
                  <NewsSentimentCard 
                    ticker={state.ticker || ''}
                    companyAnalysis={state.companyAnalysis!}
                    onSentimentInsightsUpdate={updateSentimentInsights}
                  />
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </main>
      
      {/* Settings Modal */}
      <ApiKeySettings
        isOpen={showSettings}
        onClose={() => setShowSettings(false)}
        onSave={handleSettingsSave}
      />
    </div>
  );
};