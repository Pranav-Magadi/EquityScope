import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Calculator, RefreshCw, AlertCircle, Brain, TrendingUp, BookOpen, Settings, ChevronDown, ChevronUp } from 'lucide-react';
// import { DCFModeSelector } from './DCFModeSelector'; // Removed - mode already selected at dashboard level
import { MultiStageValuationOutput } from './MultiStageValuationOutput';
import { DCFEducationalPanel } from './DCFEducationalPanel';
import { ModelSpecificDCFAssumptions } from './ModelSpecificDCFAssumptions';
import { DCFModelType, DCFModelAssumptions, DCFModelDefaults, MultiStageSimpleDCFAssumptions, MultiStageAgenticDCFAssumptions } from '../../types/dcfModels';
import { ApiService } from '../../services/api';
import type { 
  DCFMode, 
  MultiStageDCFResponse,
  CompanyAnalysis
} from '../../types';
import type { SummaryResponse } from '../../types/summary';

interface MultiStageDCFCardProps {
  ticker: string;
  companyAnalysis: CompanyAnalysis | SummaryResponse;
}

export const MultiStageDCFCard: React.FC<MultiStageDCFCardProps> = ({ 
  ticker, 
  companyAnalysis
}) => {
  // Type guard to check if we have V3 Summary data
  const isV3Summary = (data: any): data is SummaryResponse => {
    return data && 'analysis_mode' in data && 'fair_value_band' in data;
  };
  
  // Extract props based on format
  const userExperienceLevel: 'beginner' | 'intermediate' | 'advanced' = 'intermediate'; // Default
  const currentPrice = isV3Summary(companyAnalysis) 
    ? companyAnalysis.fair_value_band.current_price
    : (companyAnalysis as CompanyAnalysis).stock_price?.current_price || 0;
  
  // Get analysis mode from V3 summary or default to simple
  const selectedMode: DCFMode = isV3Summary(companyAnalysis) 
    ? (companyAnalysis.analysis_mode as DCFMode) 
    : 'simple';
  const [dcfResponse, setDcfResponse] = useState<MultiStageDCFResponse | undefined>(undefined);
  const [isLoadingDCF, setIsLoadingDCF] = useState(false);
  const [error, setError] = useState<string | undefined>(undefined);
  const [hasCalculated, setHasCalculated] = useState(false);
  const [isEducationalPanelVisible, setIsEducationalPanelVisible] = useState(false);

  // Interactive DCF Assumptions State
  const [showAssumptions, setShowAssumptions] = useState(false);
  
  // Determine DCF model type based on analysis mode
  const dcfModelType: DCFModelType = selectedMode === 'simple' 
    ? DCFModelType.MULTI_STAGE_SIMPLE 
    : DCFModelType.MULTI_STAGE_AGENTIC;
  
  // Model-specific assumptions state
  const [assumptions, setAssumptions] = useState<DCFModelAssumptions>(
    selectedMode === 'simple' 
      ? {
          model_type: DCFModelType.MULTI_STAGE_SIMPLE,
          sector: isV3Summary(companyAnalysis) ? companyAnalysis.sector : 'General',
          projection_years: 10,
          stage_1_2_growth: 8.0,
          stage_3_5_growth: 6.0,
          stage_6_8_growth: 4.0,
          stage_9_10_growth: 3.0,
          ebitda_margin: 20.0,
          tax_rate: 25.0,
          wacc: 12.0,
          terminal_growth_rate: 3.0,
          capex_percentage: 4.0,
          working_capital_percentage: 2.0,
          historical_confidence: 0.8,
          gdp_blend_methodology: 'balanced' as const,
          validation_period_years: 5
        } as MultiStageSimpleDCFAssumptions
      : {
          model_type: DCFModelType.MULTI_STAGE_AGENTIC,
          sector: isV3Summary(companyAnalysis) ? companyAnalysis.sector : 'General',
          projection_years: 10,
          management_guidance_years_1_2: 10.0,
          capacity_expansion_years_3_5: 7.0,
          market_dynamics_years_6_8: 4.5,
          gdp_convergence_years_9_10: 3.0,
          news_sentiment_adjustment: 0.0,
          management_credibility_score: 0.8,
          competitive_moat_strength: 0.7,
          risk_adjusted_wacc: 12.5,
          scenario_weighted_terminal: 3.2,
          ebitda_margin: 20.0,
          tax_rate: 25.0,
          capex_percentage: 4.0,
          working_capital_percentage: 2.0,
          ai_confidence_score: 0.75,
          forward_looking_weight: 0.7
        } as MultiStageAgenticDCFAssumptions
  );
  
  const [defaults, setDefaults] = useState<DCFModelDefaults>({
    ...assumptions,
    current_price: currentPrice,
    rationale: {},
    data_sources: {},
    confidence_scores: {}
  } as DCFModelDefaults);

  // Mode is already determined from V3 summary data

  // Calculate multi-stage DCF
  const calculateMultiStageDCF = useCallback(async (mode: DCFMode) => {
    try {
      setIsLoadingDCF(true);
      setError(undefined);
      
      console.log(`Starting 10-year multi-stage DCF calculation for ${ticker} in ${mode} mode`);
      
      const response = await ApiService.calculateMultiStageDCF(ticker, mode, 10);
      console.log('Multi-stage DCF calculation successful:', response);
      
      // If currentPrice prop is provided, use it to override the response current price
      if (currentPrice && response.valuation) {
        const originalPrice = response.valuation.current_stock_price;
        response.valuation.current_stock_price = currentPrice;
        
        // Recalculate upside/downside with the consistent price
        response.valuation.upside_downside = currentPrice > 0 
          ? ((response.valuation.intrinsic_value_per_share - currentPrice) / currentPrice) * 100 
          : 0;
          
        console.log(`Updated price from ${originalPrice} to ${currentPrice}, new upside/downside: ${response.valuation.upside_downside.toFixed(1)}%`);
      }
      
      setDcfResponse(response);
      setHasCalculated(true);
      
    } catch (err: any) {
      console.error('Error calculating multi-stage DCF:', err);
      
      let errorMessage = 'Failed to calculate multi-stage DCF';
      
      if (err.response) {
        console.error('API Error Response:', err.response.data);
        if (err.response.status === 404) {
          errorMessage = `No financial data available for ${ticker}. Please check the ticker symbol.`;
        } else if (err.response.status === 422) {
          errorMessage = 'Invalid parameters for DCF calculation. Please try again.';
        } else if (err.response.data?.detail) {
          errorMessage = `API Error: ${err.response.data.detail}`;
        }
      } else if (err.code === 'NETWORK_ERROR' || err.message?.includes('Network Error')) {
        errorMessage = 'Network error: Please check if the backend server is running on http://localhost:8000';
      } else if (err.message) {
        errorMessage = `Error: ${err.message}`;
      }
      
      setError(errorMessage);
      
    } finally {
      setIsLoadingDCF(false);
    }
  }, [ticker, currentPrice]);

  // Load DCF defaults from API
  const loadDCFDefaults = useCallback(async () => {
    try {
      const sector = isV3Summary(companyAnalysis) ? companyAnalysis.sector : 'General';
      const apiDefaults = await ApiService.getDCFDefaults(ticker, sector);
      
      // Create model-specific defaults based on API response
      const modelDefaults: DCFModelDefaults = selectedMode === 'simple' 
        ? {
            model_type: DCFModelType.MULTI_STAGE_SIMPLE,
            sector,
            projection_years: 10,
            stage_1_2_growth: apiDefaults.revenue_growth_rate || 8.0,
            stage_3_5_growth: (apiDefaults.revenue_growth_rate || 8.0) * 0.75,
            stage_6_8_growth: (apiDefaults.revenue_growth_rate || 8.0) * 0.5,
            stage_9_10_growth: apiDefaults.terminal_growth_rate || 3.0,
            ebitda_margin: apiDefaults.ebitda_margin || 20.0,
            tax_rate: apiDefaults.tax_rate || 25.0,
            wacc: apiDefaults.wacc || 12.0,
            terminal_growth_rate: apiDefaults.terminal_growth_rate || 3.0,
            capex_percentage: apiDefaults.capex_percentage || 4.0,
            working_capital_percentage: apiDefaults.working_capital_percentage || 2.0,
            historical_confidence: 0.8,
            gdp_blend_methodology: 'balanced' as const,
            validation_period_years: 5,
            current_price: currentPrice,
            rationale: apiDefaults.rationale || {},
            data_sources: {
              'Historical Data': '5-year revenue and margin analysis',
              'Sector Intelligence': 'Damodaran sector data',
              'Risk-Free Rate': '10-Year Indian G-Sec yield'
            },
            confidence_scores: {
              'stage_1_2_growth': 0.9,
              'ebitda_margin': 0.8,
              'wacc': 0.7
            }
          } as DCFModelDefaults
        : {
            model_type: DCFModelType.MULTI_STAGE_AGENTIC,
            sector,
            projection_years: 10,
            management_guidance_years_1_2: apiDefaults.revenue_growth_rate || 10.0,
            capacity_expansion_years_3_5: (apiDefaults.revenue_growth_rate || 10.0) * 0.7,
            market_dynamics_years_6_8: (apiDefaults.revenue_growth_rate || 10.0) * 0.45,
            gdp_convergence_years_9_10: apiDefaults.terminal_growth_rate || 3.0,
            news_sentiment_adjustment: 0.0,
            management_credibility_score: 0.8,
            competitive_moat_strength: 0.7,
            risk_adjusted_wacc: (apiDefaults.wacc || 12.0) + 0.5,
            scenario_weighted_terminal: (apiDefaults.terminal_growth_rate || 3.0) + 0.2,
            ebitda_margin: apiDefaults.ebitda_margin || 20.0,
            tax_rate: apiDefaults.tax_rate || 25.0,
            capex_percentage: apiDefaults.capex_percentage || 4.0,
            working_capital_percentage: apiDefaults.working_capital_percentage || 2.0,
            ai_confidence_score: 0.75,
            forward_looking_weight: 0.7,
            current_price: currentPrice,
            rationale: apiDefaults.rationale || {},
            data_sources: {
              'AI Analysis': 'Management guidance extraction',
              'News Sentiment': '6-month sentiment analysis',
              'Market Intelligence': 'Competitive positioning data'
            },
            confidence_scores: {
              'management_guidance_years_1_2': 0.85,
              'news_sentiment_adjustment': 0.6,
              'risk_adjusted_wacc': 0.7
            }
          } as DCFModelDefaults;
      
      setDefaults(modelDefaults);
      
      // Extract just the assumptions part for setAssumptions
      const { current_price, rationale, data_sources, confidence_scores, ...assumptionsOnly } = modelDefaults;
      setAssumptions(assumptionsOnly as DCFModelAssumptions);
    } catch (error) {
      console.error('Error loading DCF defaults:', error);
    }
  }, [ticker, currentPrice, companyAnalysis, selectedMode]);

  // Handle assumption updates
  const handleUpdateAssumption = useCallback((key: string, value: number) => {
    setAssumptions(prev => ({
      ...prev,
      [key]: value
    }));
  }, []);

  // Reset to defaults
  const handleResetToDefaults = useCallback(() => {
    const { current_price, rationale, data_sources, confidence_scores, ...assumptionsOnly } = defaults;
    setAssumptions(assumptionsOnly as DCFModelAssumptions);
  }, [defaults]);

  // Load defaults on component mount
  useEffect(() => {
    loadDCFDefaults();
  }, [loadDCFDefaults]);

  // Auto-calculate DCF on component mount with selected mode
  useEffect(() => {
    if (selectedMode) {
      calculateMultiStageDCF(selectedMode);
    }
  }, [selectedMode, calculateMultiStageDCF]);

  // Mode is fixed from V3 summary - no need for mode change handler

  const handleRefresh = () => {
    calculateMultiStageDCF(selectedMode);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="bg-slate-900/50 backdrop-blur-sm rounded-xl border border-slate-700/50 overflow-hidden"
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-slate-800/80 to-slate-900/80 p-6 border-b border-slate-700/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-primary-500/20 rounded-lg">
              <Calculator className="h-6 w-6 text-primary-400" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-slate-100">
                10-Year Multi-Stage DCF Analysis
              </h2>
              <p className="text-sm text-slate-400">
                Advanced valuation with GDP blending over 10 years
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            {hasCalculated && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="flex items-center space-x-2 text-sm text-green-400"
              >
                <TrendingUp className="h-4 w-4" />
                <span>Analysis Complete</span>
              </motion.div>
            )}
            
            <button
              onClick={() => setShowAssumptions(!showAssumptions)}
              className={`p-2 transition-colors ${
                showAssumptions 
                  ? 'text-primary-400 bg-primary-500/20' 
                  : 'text-slate-400 hover:text-primary-400'
              }`}
              title="Configure DCF assumptions"
            >
              <Settings className="h-5 w-5" />
            </button>
            
            <button
              onClick={() => setIsEducationalPanelVisible(!isEducationalPanelVisible)}
              className={`p-2 transition-colors ${
                isEducationalPanelVisible 
                  ? 'text-primary-400 bg-primary-500/20' 
                  : 'text-slate-400 hover:text-primary-400'
              }`}
              title="Open learning center"
            >
              <BookOpen className="h-5 w-5" />
            </button>
            
            <button
              onClick={handleRefresh}
              disabled={isLoadingDCF}
              className="p-2 text-slate-400 hover:text-primary-400 transition-colors disabled:opacity-50"
              title="Refresh analysis"
            >
              <RefreshCw className={`h-5 w-5 ${isLoadingDCF ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        {/* Error State */}
        {error && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="mb-6 p-4 bg-red-900/20 border border-red-500/30 rounded-lg"
          >
            <div className="flex items-start space-x-3">
              <AlertCircle className="h-5 w-5 text-red-400 mt-0.5 flex-shrink-0" />
              <div>
                <h4 className="text-sm font-medium text-red-300 mb-1">
                  Analysis Error
                </h4>
                <p className="text-sm text-red-200">{error}</p>
                <button
                  onClick={() => {
                    setError(undefined);
                    handleRefresh();
                  }}
                  className="mt-2 text-xs text-red-300 hover:text-red-200 underline"
                >
                  Try again
                </button>
              </div>
            </div>
          </motion.div>
        )}

        {/* Selected Mode Indicator */}
        <div className="mb-6">
          <div className={`inline-flex items-center space-x-3 px-4 py-2 rounded-lg border ${
            selectedMode === 'simple' 
              ? 'bg-blue-900/20 text-blue-300 border-blue-500/30' 
              : 'bg-purple-900/20 text-purple-300 border-purple-500/30'
          }`}>
            <div className={`w-2 h-2 rounded-full ${
              selectedMode === 'simple' ? 'bg-blue-400' : 'bg-purple-400'
            }`}></div>
            <span className="font-medium text-sm">
              {selectedMode === 'simple' ? 'Rule-Based Analysis Mode' : 'AI Analyst Insights Mode'}
            </span>
          </div>
        </div>

        {/* Interactive DCF Assumptions Panel */}
        {showAssumptions && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mb-6"
          >
            <div className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <Settings className="h-5 w-5 text-primary-400" />
                  <h3 className="text-lg font-semibold text-slate-100">Configure DCF Assumptions</h3>
                  <div className="px-2 py-1 rounded text-xs font-medium bg-primary-500/20 text-primary-400">
                    REAL-TIME
                  </div>
                </div>
                <button
                  onClick={() => setShowAssumptions(false)}
                  className="text-slate-400 hover:text-slate-300 transition-colors"
                >
                  <ChevronUp className="h-5 w-5" />
                </button>
              </div>
              
              <ModelSpecificDCFAssumptions
                modelType={dcfModelType}
                assumptions={assumptions}
                defaults={defaults}
                onUpdateAssumption={handleUpdateAssumption}
                onResetToDefaults={handleResetToDefaults}
                sector={isV3Summary(companyAnalysis) ? companyAnalysis.sector : 'General'}
                mode={selectedMode}
              />
            </div>
          </motion.div>
        )}

        {/* Valuation Results */}
        <div>
            {dcfResponse ? (
              <MultiStageValuationOutput
                dcfResponse={dcfResponse}
                userLevel={userExperienceLevel}
                isLoading={isLoadingDCF}
              />
            ) : (
              <div className="space-y-6">
                {isLoadingDCF ? (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="bg-slate-800/50 rounded-lg p-8 text-center"
                  >
                    <div className="inline-flex items-center space-x-3">
                      <RefreshCw className="h-6 w-6 text-primary-400 animate-spin" />
                      <div className="text-left">
                        <div className="text-lg font-medium text-slate-200">
                          Calculating Multi-Stage DCF
                        </div>
                        <div className="text-sm text-slate-400">
                          {selectedMode === 'simple' 
                            ? 'Processing historical validation and GDP blending...' 
                            : 'Running AI-enhanced analysis with management guidance...'
                          }
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ) : (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="bg-slate-800/50 rounded-lg p-8 text-center"
                  >
                    <Brain className="h-12 w-12 text-slate-500 mx-auto mb-4" />
                    <div className="text-lg font-medium text-slate-300 mb-2">
                      Ready for 10-Year Analysis
                    </div>
                    <div className="text-sm text-slate-400 mb-4">
                      Select your preferred analysis mode to begin the advanced DCF calculation
                    </div>
                    <button
                      onClick={handleRefresh}
                      className="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg font-medium transition-colors"
                    >
                      Start Analysis
                    </button>
                  </motion.div>
                )}
              </div>
            )}
        </div>

        {/* Educational Panel */}
        <DCFEducationalPanel
          dcfResponse={dcfResponse}
          userLevel={userExperienceLevel}
          focusArea={dcfResponse ? 'interpretation' : 'basics'}
          isVisible={isEducationalPanelVisible}
          onClose={() => setIsEducationalPanelVisible(false)}
        />
      </div>
    </motion.div>
  );
};