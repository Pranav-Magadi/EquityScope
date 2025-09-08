import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  TrendingUp, 
  AlertCircle, 
  Loader2, 
  Zap, 
  Bot,
  Settings,
  Clock,
  CheckCircle,
  Square
} from 'lucide-react';

// Section 1: Qualitative Narrative Components
import { CompanyHeader } from './QualitativeCards/CompanyHeader';
import { DetailedSWOTAnalysisCard } from './QualitativeCards/DetailedSWOTAnalysis';
import { NewsSentimentCard } from './QualitativeCards/NewsSentiment';
import { CompetitiveAnalysisCard } from './QualitativeCards/CompetitiveAnalysis';

// Section 2: Quantitative Valuation Components  
import { DCFCard } from './DCFValuation/DCFCard';
import { TechnicalAnalysisCard } from './TechnicalAnalysis/TechnicalAnalysisCard';

// Section 3: AI Investment Committee
import { AIInvestmentCommittee } from './InvestmentCommittee/AIInvestmentCommittee';

// Settings
import ApiKeySettings from './Settings/ApiKeySettings';

// Common Components
import { StockAutocomplete } from './common/StockAutocomplete';

// Services and Types
import { ApiService } from '../services/api';
import type { 
  DashboardState, 
  CompanyAnalysis,
  InvestmentCommitteeData,
  SWOTAnalysis,
  CompetitiveAnalysis 
} from '../types';
import type { SummaryResponse } from '../types/summary';

// Type guard to check if data is V3 Summary format
const isV3Summary = (data: any): data is SummaryResponse => {
  return data && 'analysis_mode' in data && 'fair_value_band' in data;
};
import type { StockSymbol } from '../data/stockSymbols';

interface AgenticAnalysisState {
  isRunning: boolean;
  progress: number;
  currentStep: string;
  message: string;
  result?: {
    dashboard_sections: {
      section_1_qualitative_narrative: {
        header_card: any;
        swot_analysis: SWOTAnalysis;
        news_sentiment: any;
        competitive_analysis: CompetitiveAnalysis;
      };
      section_2_quantitative_valuation: {
        dcf_assumptions: any;
        sensitivity_analysis: any;
      };
      section_3_investment_committee: InvestmentCommitteeData;
    };
  };
  error?: string;
}

export const AgenticDashboard: React.FC = () => {
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

  const [agenticState, setAgenticState] = useState<AgenticAnalysisState>({
    isRunning: false,
    progress: 0,
    currentStep: 'idle',
    message: 'Ready to start AI agentic analysis'
  });

  const [searchTicker, setSearchTicker] = useState('');
  const [showSettings, setShowSettings] = useState(false);
  const [useAgenticMode, setUseAgenticMode] = useState(true);

  const updateLoadingState = useCallback((key: 'company' | 'dcf', loading: boolean, error?: string) => {
    setState(prev => ({
      ...prev,
      loadingStates: {
        ...prev.loadingStates,
        [key]: { isLoading: loading, error }
      }
    }));
  }, []);

  // Agentic Analysis Flow
  const runAgenticAnalysis = useCallback(async (ticker: string) => {
    try {
      setAgenticState({
        isRunning: true,
        progress: 0,
        currentStep: 'starting',
        message: 'Connecting to AI backend...'
      });

      // First check if backend is available
      try {
        const healthResponse = await fetch('/api/agentic/health');
        if (!healthResponse.ok) {
          throw new Error('Backend server not available');
        }
        const healthData = await healthResponse.json();
        if (!healthData.claude_available) {
          throw new Error('Claude AI service not configured. Please add your Claude API key in Settings.');
        }
      } catch (error) {
        throw new Error('Backend server not running. Please start the backend server with: cd backend && uvicorn app.main:app --reload');
      }

      setAgenticState(prev => ({
        ...prev,
        progress: 5,
        message: 'Starting agentic workflow...'
      }));

      // Start the analysis
      const response = await fetch(`/api/agentic/analyze/${ticker}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ max_news_articles: 10 })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || 'Failed to start agentic analysis');
      }

      await response.json();

      // Poll for progress updates
      const pollProgress = async () => {
        try {
          const statusResponse = await fetch(`/api/agentic/status/${ticker}`);
          const statusData = await statusResponse.json();

          setAgenticState(prev => ({
            ...prev,
            progress: statusData.progress,
            currentStep: statusData.current_step,
            message: statusData.message
          }));

          if (statusData.status === 'completed') {
            // Get the final result
            const resultResponse = await fetch(`/api/agentic/result/${ticker}`);
            const resultData = await resultResponse.json();

            setAgenticState(prev => ({
              ...prev,
              isRunning: false,
              progress: 100,
              currentStep: 'complete',
              message: 'Analysis complete!',
              result: resultData
            }));

            // Update state with results
            setState(prev => ({
              ...prev,
              ticker,
              companyAnalysis: resultData.dashboard_sections.section_1_qualitative_narrative
            }));

          } else if (statusData.status === 'failed') {
            setAgenticState(prev => ({
              ...prev,
              isRunning: false,
              error: statusData.error || 'Analysis failed',
              currentStep: 'error',
              message: 'Analysis failed'
            }));
          } else {
            // Continue polling
            setTimeout(pollProgress, 2000);
          }
        } catch (error) {
          console.error('Error polling status:', error);
          setAgenticState(prev => ({
            ...prev,
            isRunning: false,
            error: 'Failed to check analysis status',
            currentStep: 'error',
            message: 'Connection error'
          }));
        }
      };

      // Start polling after a brief delay
      setTimeout(pollProgress, 1000);

    } catch (error) {
      console.error('Error starting agentic analysis:', error);
      
      // Check if it's a backend connectivity issue
      const errorMessage = error instanceof Error ? error.message : 'Failed to start analysis';
      const isBackendIssue = errorMessage.includes('Backend server') || errorMessage.includes('Claude AI service');
      
      if (isBackendIssue) {
        // Offer demo mode
        setAgenticState(prev => ({
          ...prev,
          isRunning: false,
          error: `${errorMessage}\n\nTip: You can try the demo mode by disabling "AI Agentic Mode" above, or start the backend server.`,
          currentStep: 'error',
          message: 'Backend connection failed'
        }));
      } else {
        setAgenticState(prev => ({
          ...prev,
          isRunning: false,
          error: errorMessage,
          currentStep: 'error',
          message: 'Analysis failed'
        }));
      }
    }
  }, []);

  // Fallback to standard analysis (basic data only)
  const runStandardAnalysis = useCallback(async (ticker: string) => {
    try {
      updateLoadingState('company', true);
      const basicData = await ApiService.getBasicCompanyData(ticker);
      
      setState(prev => ({
        ...prev,
        ticker,
        companyAnalysis: basicData
      }));
    } catch (error) {
      console.error('Error fetching basic company data:', error);
      updateLoadingState('company', false, 'Failed to fetch company data. Please check the ticker symbol.');
    } finally {
      updateLoadingState('company', false);
    }
  }, [updateLoadingState]);

  // Cancel agentic analysis
  const cancelAgenticAnalysis = useCallback(async () => {
    if (!state.ticker || !agenticState.isRunning) return;
    
    try {
      const response = await fetch(`/api/agentic/cancel/${state.ticker}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        setAgenticState(prev => ({
          ...prev,
          isRunning: false,
          progress: 0,
          currentStep: 'cancelled',
          message: 'Analysis cancelled by user'
        }));
      }
    } catch (error) {
      console.error('Error cancelling analysis:', error);
    }
  }, [state.ticker, agenticState.isRunning]);

  const handleSearch = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchTicker.trim()) return;

    const ticker = searchTicker.trim().toUpperCase();
    
    if (useAgenticMode) {
      await runAgenticAnalysis(ticker);
    } else {
      await runStandardAnalysis(ticker);
    }
  }, [searchTicker, useAgenticMode, runAgenticAnalysis, runStandardAnalysis]);

  const handleStockSelect = useCallback(async (stock: StockSymbol) => {
    if (useAgenticMode) {
      await runAgenticAnalysis(stock.ticker);
    } else {
      await runStandardAnalysis(stock.ticker);
    }
  }, [useAgenticMode, runAgenticAnalysis, runStandardAnalysis]);

  const handleExampleClick = useCallback((ticker: string) => {
    setSearchTicker(ticker);
    if (useAgenticMode) {
      runAgenticAnalysis(ticker);
    } else {
      runStandardAnalysis(ticker);
    }
  }, [useAgenticMode, runAgenticAnalysis, runStandardAnalysis]);

  const handleApiKeySave = useCallback(async (config: any) => {
    console.log('API keys updated:', config);
    // Here you would typically send the keys to the backend
  }, []);

  // Computed states
  const isLoading = state.loadingStates.company.isLoading || agenticState.isRunning;
  const hasError = state.loadingStates.company.error || agenticState.error;
  const hasData = state.companyAnalysis || agenticState.result;
  const hasAgenticResult = agenticState.result?.dashboard_sections;

  return (
    <div className="min-h-screen bg-slate-900">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header with Settings */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-4xl font-bold text-slate-100 mb-2">
                Qualitative Edge
              </h1>
              <p className="text-slate-400">
                AI-Powered Financial Analysis with Agentic Workflow
              </p>
            </div>
            <button
              onClick={() => setShowSettings(true)}
              className="p-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg transition-colors"
            >
              <Settings className="h-5 w-5 text-slate-400" />
            </button>
          </div>

          {/* Analysis Type Selector */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
            {/* Simple Analysis Option */}
            <motion.div
              whileHover={{ scale: 1.02 }}
              className={`relative p-6 border-2 rounded-xl cursor-pointer transition-all ${
                !useAgenticMode 
                  ? 'border-blue-500 bg-blue-900/20 shadow-lg shadow-blue-500/10' 
                  : 'border-slate-600 bg-slate-800/50 hover:border-slate-500'
              }`}
              onClick={() => setUseAgenticMode(false)}
            >
              <div className="flex items-start space-x-4">
                <div className={`p-3 rounded-lg ${!useAgenticMode ? 'bg-blue-600' : 'bg-slate-700'}`}>
                  <TrendingUp className="h-6 w-6 text-white" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className={`text-lg font-semibold ${!useAgenticMode ? 'text-blue-300' : 'text-slate-300'}`}>
                      Simple Analysis
                    </h3>
                    <span className="px-2 py-1 bg-green-600 text-white text-xs rounded-full">
                      Always Available
                    </span>
                  </div>
                  <p className="text-sm text-slate-400 mb-3">
                    Fast, reliable analysis using financial data and basic insights. Perfect for quick research and fundamental analysis.
                  </p>
                  <div className="space-y-2 text-xs text-slate-500">
                    <div className="flex items-center space-x-2">
                      <div className="w-1 h-1 bg-green-400 rounded-full"></div>
                      <span>Company fundamentals & DCF valuation</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-1 h-1 bg-green-400 rounded-full"></div>
                      <span>Basic SWOT analysis</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-1 h-1 bg-green-400 rounded-full"></div>
                      <span>No API keys required</span>
                    </div>
                  </div>
                  <div className="mt-4 p-3 bg-slate-900/50 rounded-lg">
                    <p className="text-xs text-slate-400">
                      <strong>Disclaimer:</strong> Uses historical financial data and general market insights. Not personalized investment advice.
                    </p>
                  </div>
                </div>
              </div>
              {!useAgenticMode && (
                <div className="absolute top-4 right-4">
                  <div className="w-4 h-4 bg-blue-500 rounded-full flex items-center justify-center">
                    <div className="w-2 h-2 bg-white rounded-full"></div>
                  </div>
                </div>
              )}
            </motion.div>

            {/* AI Agentic Analysis Option */}
            <motion.div
              whileHover={{ scale: 1.02 }}
              className={`relative p-6 border-2 rounded-xl cursor-pointer transition-all ${
                useAgenticMode 
                  ? 'border-purple-500 bg-purple-900/20 shadow-lg shadow-purple-500/10' 
                  : 'border-slate-600 bg-slate-800/50 hover:border-slate-500'
              }`}
              onClick={() => setUseAgenticMode(true)}
            >
              <div className="flex items-start space-x-4">
                <div className={`p-3 rounded-lg ${useAgenticMode ? 'bg-purple-600' : 'bg-slate-700'}`}>
                  <Bot className="h-6 w-6 text-white" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className={`text-lg font-semibold ${useAgenticMode ? 'text-purple-300' : 'text-slate-300'}`}>
                      AI Agentic Analysis
                    </h3>
                    <span className="px-2 py-1 bg-yellow-600 text-white text-xs rounded-full">
                      Requires API Key
                    </span>
                  </div>
                  <p className="text-sm text-slate-400 mb-3">
                    Advanced AI-powered analysis with 4-agent workflow, source attribution, and investment committee validation.
                  </p>
                  <div className="space-y-2 text-xs text-slate-500">
                    <div className="flex items-center space-x-2">
                      <div className="w-1 h-1 bg-purple-400 rounded-full"></div>
                      <span>4-Agent workflow: Generator → Checker → Bull → Bear</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-1 h-1 bg-purple-400 rounded-full"></div>
                      <span>Real-time news scraping with source links</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-1 h-1 bg-purple-400 rounded-full"></div>
                      <span>Investment committee validation</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-1 h-1 bg-purple-400 rounded-full"></div>
                      <span>Bull/Bear commentary with scenarios</span>
                    </div>
                  </div>
                  <div className="mt-4 p-3 bg-slate-900/50 rounded-lg">
                    <p className="text-xs text-slate-400">
                      <strong>Disclaimer:</strong> AI-generated insights for research purposes. Requires Claude API key. Not financial advice.
                    </p>
                  </div>
                </div>
              </div>
              {useAgenticMode && (
                <div className="absolute top-4 right-4">
                  <div className="w-4 h-4 bg-purple-500 rounded-full flex items-center justify-center">
                    <div className="w-2 h-2 bg-white rounded-full"></div>
                  </div>
                </div>
              )}
            </motion.div>
          </div>

          {/* Search Interface */}
          <div className="text-center">
            <h2 className="text-2xl font-bold text-slate-100 mb-2">
              {useAgenticMode ? 'AI-Powered Multi-Agent Analysis' : 'Standard Company Analysis'}
            </h2>
            <p className="text-slate-400 max-w-2xl mx-auto mb-6">
              {useAgenticMode 
                ? 'Advanced analysis using 4 AI agents with source attribution and investment committee validation'
                : 'Enter an NSE ticker symbol to get AI-powered qualitative analysis combined with interactive DCF valuation'
              }
            </p>

            <form onSubmit={handleSearch} className="max-w-lg mx-auto">
              <div className="flex space-x-2">
                <div className="flex-1">
                  <StockAutocomplete
                    value={searchTicker}
                    onChange={setSearchTicker}
                    onSelect={handleStockSelect}
                    placeholder="Enter stock name or ticker (e.g., SBI, RELIANCE, TCS)"
                    disabled={isLoading}
                  />
                </div>
                <button
                  type="submit"
                  disabled={isLoading || !searchTicker.trim()}
                  className="btn-primary whitespace-nowrap disabled:opacity-50 disabled:cursor-not-allowed min-w-[120px]"
                >
                  {isLoading ? (
                    <div className="flex items-center space-x-2">
                      <Loader2 className="h-4 w-4 animate-spin" />
                      <span>Analyzing...</span>
                    </div>
                  ) : useAgenticMode ? (
                    <div className="flex items-center space-x-2">
                      <Zap className="h-4 w-4" />
                      <span>AI Analyze</span>
                    </div>
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
                {['RELIANCE.NS', 'TCS.NS', 'SBIN.NS', 'HDFCBANK.NS', 'ITC.NS', 'INFY.NS'].map((ticker) => (
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
          </div>
        </motion.div>

        {/* Agentic Progress Indicator */}
        <AnimatePresence>
          {agenticState.isRunning && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="mb-8"
            >
              <div className="bg-gradient-to-r from-purple-900/20 to-blue-900/20 border border-purple-700/30 rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-purple-600 rounded-lg">
                      <Bot className="h-5 w-5 text-white" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-white">AI Agentic Analysis Running</h3>
                      <p className="text-sm text-purple-200">{agenticState.message}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <button
                      onClick={cancelAgenticAnalysis}
                      className="btn-secondary text-sm flex items-center space-x-2 px-3 py-2 bg-red-600 hover:bg-red-700 text-white"
                    >
                      <Square className="h-4 w-4" />
                      <span>Stop</span>
                    </button>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-purple-300">{agenticState.progress}%</div>
                      <div className="text-xs text-purple-400">{agenticState.currentStep}</div>
                    </div>
                  </div>
                </div>
                
                {/* Progress Bar */}
                <div className="w-full bg-slate-700 rounded-full h-2">
                  <motion.div
                    className="bg-gradient-to-r from-purple-400 to-blue-400 h-2 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${agenticState.progress}%` }}
                    transition={{ duration: 0.5 }}
                  />
                </div>

                {/* Progress Steps */}
                <div className="flex justify-between mt-4 text-xs text-purple-200">
                  <div className={`flex items-center space-x-1 ${agenticState.progress >= 25 ? 'text-purple-300' : 'text-slate-500'}`}>
                    {agenticState.progress >= 50 ? <CheckCircle className="h-3 w-3" /> : <Clock className="h-3 w-3" />}
                    <span>Data Ingestion</span>
                  </div>
                  <div className={`flex items-center space-x-1 ${agenticState.progress >= 50 ? 'text-purple-300' : 'text-slate-500'}`}>
                    {agenticState.progress >= 70 ? <CheckCircle className="h-3 w-3" /> : <Clock className="h-3 w-3" />}
                    <span>Generator Agent</span>
                  </div>
                  <div className={`flex items-center space-x-1 ${agenticState.progress >= 75 ? 'text-purple-300' : 'text-slate-500'}`}>
                    {agenticState.progress >= 85 ? <CheckCircle className="h-3 w-3" /> : <Clock className="h-3 w-3" />}
                    <span>Checker Agent</span>
                  </div>
                  <div className={`flex items-center space-x-1 ${agenticState.progress >= 90 ? 'text-purple-300' : 'text-slate-500'}`}>
                    {agenticState.progress === 100 ? <CheckCircle className="h-3 w-3" /> : <Clock className="h-3 w-3" />}
                    <span>Commentators</span>
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
              <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-6">
                <div className="flex items-start space-x-3">
                  <AlertCircle className="h-5 w-5 text-red-400 mt-0.5 flex-shrink-0" />
                  <div className="flex-1">
                    <h3 className="text-red-300 font-medium mb-2">Analysis Failed</h3>
                    <div className="text-red-200 text-sm whitespace-pre-line leading-relaxed">
                      {hasError}
                    </div>
                    {hasError.includes('Backend server') && (
                      <div className="mt-4 p-3 bg-blue-900/20 border border-blue-500/30 rounded-lg">
                        <h4 className="text-blue-300 font-medium text-sm mb-2">Quick Start Instructions:</h4>
                        <div className="text-blue-200 text-xs space-y-1">
                          <div>1. Open a terminal and navigate to the backend directory</div>
                          <div>2. Run: <code className="bg-slate-800 px-2 py-1 rounded text-blue-100">python start_server.py</code></div>
                          <div>3. Wait for "Server started" message</div>
                          <div>4. Try the analysis again</div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Standard Loading State */}
        <AnimatePresence>
          {isLoading && !hasData && !agenticState.isRunning && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="text-center py-12"
            >
              <Loader2 className="h-8 w-8 text-primary-400 animate-spin mx-auto mb-4" />
              <div className="text-slate-300 mb-2">Analyzing {searchTicker}...</div>
              <div className="text-sm text-slate-400">Fetching financial data and generating insights</div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* 3-Section Dashboard Layout */}
        <AnimatePresence>
          {hasAgenticResult && agenticState.result && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-12"
            >
              {/* Company Header */}
              {agenticState.result.dashboard_sections.section_1_qualitative_narrative.header_card && (
                <CompanyHeader
                  ticker={state.ticker || ''}
                  companyAnalysis={agenticState.result as any}
                />
              )}

              {/* Section 1: Qualitative Narrative */}
              <section>
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="mb-8"
                >
                  <div className="flex items-center space-x-3 mb-6">
                    <div className="w-8 h-8 bg-green-600 rounded-lg flex items-center justify-center text-white font-bold">1</div>
                    <div>
                      <h2 className="text-3xl font-bold text-slate-100">Qualitative Narrative</h2>
                      <p className="text-slate-400">SWOT Analysis, News Sentiment & Competitive Analysis with Source Attribution</p>
                    </div>
                  </div>
                </motion.div>
                
                <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
                  {agenticState.result.dashboard_sections.section_1_qualitative_narrative.swot_analysis && (
                    <DetailedSWOTAnalysisCard 
                      swot={agenticState.result.dashboard_sections.section_1_qualitative_narrative.swot_analysis}
                      companyName={state.ticker || 'Company'}
                      ticker={state.ticker || ''}
                    />
                  )}
                  {agenticState.result.dashboard_sections.section_1_qualitative_narrative.news_sentiment && (
                    <NewsSentimentCard 
                      ticker={state.ticker || ''}
                      companyAnalysis={agenticState.result as any}
                    />
                  )}
                </div>
                
                {/* Competitive Analysis - Full Width */}
                {agenticState.result.dashboard_sections.section_1_qualitative_narrative.competitive_analysis && (
                  <div className="mt-8">
                    <CompetitiveAnalysisCard 
                      data={agenticState.result.dashboard_sections.section_1_qualitative_narrative.competitive_analysis}
                      companyName={state.ticker || 'Company'}
                      ticker={state.ticker || ''}
                    />
                  </div>
                )}
              </section>

              {/* Section 2: Interactive Quantitative Valuation */}
              <section>
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.2 }}
                  className="mb-8"
                >
                  <div className="flex items-center space-x-3 mb-6">
                    <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold">2</div>
                    <div>
                      <h2 className="text-3xl font-bold text-slate-100">Interactive Quantitative Valuation</h2>
                      <p className="text-slate-400">Technical Analysis & DCF Model with Real-time Sensitivity Analysis</p>
                    </div>
                  </div>
                </motion.div>
                
                {/* Technical Analysis Summary Card */}
                {state.ticker && (
                  <div className="mb-8">
                    <TechnicalAnalysisCard 
                      ticker={state.ticker} 
                      useAgenticMode={useAgenticMode}
                    />
                  </div>
                )}
                
                {/* DCF Valuation Card */}
                {state.ticker && (
                  <DCFCard 
                    ticker={state.ticker} 
                    currentPrice={agenticState.result?.dashboard_sections?.section_1_qualitative_narrative?.header_card?.current_price}
                  />
                )}
              </section>

              {/* Section 3: AI Investment Committee */}
              <section>
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.4 }}
                  className="mb-8"
                >
                  <div className="flex items-center space-x-3 mb-6">
                    <div className="w-8 h-8 bg-purple-600 rounded-lg flex items-center justify-center text-white font-bold">3</div>
                    <div>
                      <h2 className="text-3xl font-bold text-slate-100">AI Investment Committee</h2>
                      <p className="text-slate-400">Multi-Agent Validation & Bull-Bear Commentary</p>
                    </div>
                  </div>
                </motion.div>
                
                {agenticState.result.dashboard_sections.section_3_investment_committee && (
                  <AIInvestmentCommittee
                    data={agenticState.result.dashboard_sections.section_3_investment_committee}
                    companyName={state.ticker || 'Company'}
                    ticker={state.ticker || ''}
                  />
                )}
              </section>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Fallback to Standard Analysis Results */}
        <AnimatePresence>
          {hasData && !hasAgenticResult && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-8"
            >
              <CompanyHeader
                ticker={state.ticker || ''}
                companyAnalysis={state.companyAnalysis!}
              />

              <div>
                <motion.h2
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.1 }}
                  className="text-2xl font-bold text-slate-100 mb-6"
                >
                  Technical Analysis Summary
                </motion.h2>
                
                <TechnicalAnalysisCard 
                  ticker={state.ticker!} 
                  useAgenticMode={useAgenticMode}
                />
              </div>

              <div>
                <motion.h2
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 }}
                  className="text-2xl font-bold text-slate-100 mb-6"
                >
                  Interactive DCF Valuation
                </motion.h2>
                
                <DCFCard 
                  ticker={state.ticker!} 
                  currentPrice={isV3Summary(state.companyAnalysis!) ? 
                    state.companyAnalysis!.fair_value_band.current_price : 
                    state.companyAnalysis?.stock_price?.current_price
                  }
                />
              </div>

              <div>
                <motion.h2
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="text-2xl font-bold text-slate-100 mb-6"
                >
                  AI-Powered Analysis Available
                </motion.h2>
                
                <div className="grid grid-cols-1 gap-6">
                  {/* SWOT and Sentiment Analysis Notice */}
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-6"
                  >
                    <div className="flex items-center space-x-3 mb-4">
                      <Bot className="h-6 w-6 text-purple-400" />
                      <h3 className="text-xl font-semibold text-slate-100">Upgrade to AI Agentic Mode</h3>
                    </div>
                    <p className="text-slate-300 mb-4">
                      SWOT Analysis, News Sentiment, and Investment Committee validation are exclusively available through our AI Agentic Analysis mode.
                    </p>
                    <div className="bg-slate-900/50 rounded-lg p-4 mb-4">
                      <h4 className="text-sm font-semibold text-purple-300 mb-2">Enable AI Agentic Mode to get:</h4>
                      <ul className="text-sm text-slate-400 space-y-1">
                        <li>• Comprehensive SWOT Analysis with source attribution</li>
                        <li>• Real-time News Sentiment Analysis</li>
                        <li>• Competitive Analysis vs Industry Peers</li>
                        <li>• AI Investment Committee validation</li>
                        <li>• Bull and Bear commentary with DCF scenarios</li>
                      </ul>
                    </div>
                    <div className="text-xs text-slate-500">
                      <strong>Note:</strong> Standard mode focuses on quantitative DCF valuation without AI-generated qualitative insights.
                    </div>
                  </motion.div>
                </div>
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
                {useAgenticMode ? (
                  <Bot className="h-12 w-12 text-primary-400" />
                ) : (
                  <TrendingUp className="h-12 w-12 text-primary-400" />
                )}
              </div>
            </div>
            <h3 className="text-xl font-semibold text-slate-100 mb-2">
              {useAgenticMode ? 'Ready for AI Agentic Analysis' : 'Ready for Analysis'}
            </h3>
            <p className="text-slate-400 max-w-md mx-auto">
              {useAgenticMode 
                ? 'Enter a ticker symbol to start the 4-agent AI workflow with comprehensive source attribution and investment committee validation.'
                : 'Enter a ticker symbol above to start your comprehensive company analysis with AI-powered insights and interactive DCF valuation.'
              }
            </p>
          </motion.div>
        )}
      </div>

      {/* API Key Settings Modal */}
      <ApiKeySettings
        isOpen={showSettings}
        onClose={() => setShowSettings(false)}
        onSave={handleApiKeySave}
      />
    </div>
  );
};

export default AgenticDashboard;