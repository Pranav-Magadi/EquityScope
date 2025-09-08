import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Calculator, RefreshCw, AlertCircle } from 'lucide-react';
import { SimpleAssumptionsPanel } from './SimpleAssumptionsPanel';
import { ValuationOutput } from './ValuationOutput';
import { SensitivityAnalysisComponent } from './SensitivityAnalysis';
import PriceHeatBar from './PriceHeatBar';
import { ApiService } from '../../services/api';
import type { DCFAssumptions, DCFDefaults, DCFResponse } from '../../types';
import { DCFUtils } from '../../utils/dcf';

interface DCFCardProps {
  ticker: string;
  currentPrice?: number; // Optional prop to ensure price consistency
}

export const DCFCard: React.FC<DCFCardProps> = ({ ticker, currentPrice }) => {
  const [assumptions, setAssumptions] = useState<DCFAssumptions>({
    revenue_growth_rate: 8.0,
    ebitda_margin: 15.0,
    tax_rate: 25.0,
    wacc: 12.0,
    terminal_growth_rate: 4.0,
    projection_years: 5
  });

  const [defaults, setDefaults] = useState<DCFDefaults | null>(null);
  const [dcfResponse, setDcfResponse] = useState<DCFResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasCalculated, setHasCalculated] = useState(false);

  // Debounced calculation
  const [calculationTimeout, setCalculationTimeout] = useState<NodeJS.Timeout | null>(null);

  const fetchDefaults = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      console.log(`Fetching DCF defaults for ${ticker}`);
      
      const defaultsData = await ApiService.getDCFDefaults(ticker);
      console.log('DCF defaults fetched successfully:', defaultsData);
      
      setDefaults(defaultsData);
      
      // Update assumptions with defaults
      setAssumptions({
        revenue_growth_rate: defaultsData.revenue_growth_rate,
        ebitda_margin: defaultsData.ebitda_margin,
        tax_rate: defaultsData.tax_rate,
        wacc: defaultsData.wacc,
        terminal_growth_rate: defaultsData.terminal_growth_rate,
        projection_years: 5
      });
    } catch (err: any) {
      console.error('Error fetching defaults:', err);
      
      let errorMessage = 'Failed to fetch default assumptions';
      
      if (err.response) {
        console.error('API Error Response:', err.response.data);
        if (err.response.status === 404) {
          errorMessage = `No financial data available for ${ticker}. Please check the ticker symbol.`;
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
      setIsLoading(false);
    }
  }, [ticker]);

  const calculateDCF = useCallback(async (assumptionsToUse: DCFAssumptions) => {
    try {
      setIsLoading(true);
      setError(null);
      
      console.log(`Starting DCF calculation for ${ticker} with assumptions:`, assumptionsToUse);
      
      const response = await ApiService.calculateDCF(ticker, assumptionsToUse);
      console.log('DCF calculation successful:', response);
      
      // If currentPrice prop is provided, use it to override the response current price
      if (currentPrice && response.valuation) {
        const originalPrice = response.valuation.current_stock_price;
        response.valuation.current_stock_price = currentPrice;
        
        // Recalculate upside/downside with the consistent price
        response.valuation.upside_downside = currentPrice > 0 
          ? ((response.valuation.intrinsic_value_per_share - currentPrice) / currentPrice) * 100 
          : 0;
          
        console.log(`Updated current price from ${originalPrice} to ${currentPrice} for consistency`);
      }
      
      setDcfResponse(response);
      setHasCalculated(true);
    } catch (err: any) {
      console.error('Error calculating DCF:', err);
      
      let errorMessage = 'Failed to calculate DCF valuation';
      
      if (err.response) {
        // API returned an error response
        console.error('API Error Response:', err.response.data);
        if (err.response.status === 404) {
          errorMessage = `Financial data not found for ${ticker}. Please check the ticker symbol.`;
        } else if (err.response.status === 400) {
          errorMessage = `Invalid data for DCF calculation: ${err.response.data?.detail || 'Please check your inputs'}`;
        } else if (err.response.data?.detail) {
          errorMessage = `API Error: ${err.response.data.detail}`;
        }
      } else if (err.code === 'NETWORK_ERROR' || err.message?.includes('Network Error')) {
        errorMessage = 'Network error: Please check if the backend server is running on http://localhost:8000';
      } else if (err.message) {
        errorMessage = `Calculation error: ${err.message}`;
      }
      
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [ticker]);

  // Debounced calculation effect
  useEffect(() => {
    if (!hasCalculated || !defaults) return;

    // Clear existing timeout
    if (calculationTimeout) {
      clearTimeout(calculationTimeout);
    }

    // Validate assumptions before calculating
    const validation = DCFUtils.validateAssumptions(assumptions);
    if (!validation.isValid) {
      setError(`Invalid assumptions: ${validation.errors.join(', ')}`);
      return;
    }

    // Set new timeout for debounced calculation
    const timeout = setTimeout(() => {
      calculateDCF(assumptions);
    }, 500); // 500ms delay

    setCalculationTimeout(timeout);

    return () => {
      if (timeout) clearTimeout(timeout);
    };
  }, [assumptions, calculateDCF, hasCalculated, defaults, calculationTimeout]);

  // Reset state and fetch new data when ticker changes
  useEffect(() => {
    // Reset all state when ticker changes
    setDefaults(null);
    setDcfResponse(null);
    setError(null);
    setHasCalculated(false);
    setAssumptions({
      revenue_growth_rate: 8.0,
      ebitda_margin: 15.0,
      tax_rate: 25.0,
      wacc: 12.0,
      terminal_growth_rate: 4.0,
      projection_years: 5
    });
    
    // Clear any pending calculation timeouts
    if (calculationTimeout) {
      clearTimeout(calculationTimeout);
      setCalculationTimeout(null);
    }
    
    // Fetch new defaults for the new ticker
    fetchDefaults();
  }, [ticker, fetchDefaults]);

  // Initial calculation after defaults are loaded
  useEffect(() => {
    if (defaults && !hasCalculated) {
      calculateDCF(assumptions);
    }
  }, [defaults, assumptions, calculateDCF, hasCalculated]);

  const handleUpdateAssumption = useCallback((key: keyof DCFAssumptions, value: number) => {
    setAssumptions(prev => ({
      ...prev,
      [key]: value
    }));
  }, []);

  const handleResetToDefaults = useCallback(() => {
    if (defaults) {
      setAssumptions({
        revenue_growth_rate: defaults.revenue_growth_rate,
        ebitda_margin: defaults.ebitda_margin,
        tax_rate: defaults.tax_rate,
        wacc: defaults.wacc,
        terminal_growth_rate: defaults.terminal_growth_rate,
        projection_years: 5
      });
    }
  }, [defaults]);

  const handleRecalculate = useCallback(() => {
    calculateDCF(assumptions);
  }, [calculateDCF, assumptions]);

  if (!defaults) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.5 }}
        className="card"
      >
        <div className="card-body">
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <RefreshCw className="h-8 w-8 text-primary-400 animate-spin mx-auto mb-4" />
              <div className="text-slate-300">Loading DCF model...</div>
            </div>
          </div>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.5 }}
      className="card"
    >
      <div className="card-header">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Calculator className="h-5 w-5 text-primary-400" />
            <h2 className="text-xl font-semibold text-slate-100">Interactive DCF Valuation</h2>
          </div>
          <div className="flex items-center space-x-2">
            {isLoading && (
              <RefreshCw className="h-4 w-4 text-primary-400 animate-spin" />
            )}
            <button
              onClick={handleRecalculate}
              disabled={isLoading}
              className="btn-secondary text-sm"
            >
              Recalculate
            </button>
          </div>
        </div>
        <p className="text-sm text-slate-400 mt-1">
          Real-time discounted cash flow analysis with interactive assumptions
        </p>
      </div>

      <div className="card-body">
        {error && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="bg-red-900/20 border border-red-500/30 rounded-lg p-4 mb-6"
          >
            <div className="flex items-center space-x-2">
              <AlertCircle className="h-5 w-5 text-red-400" />
              <div className="text-sm text-red-300">{error}</div>
            </div>
          </motion.div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column: Assumptions */}
          <div className="space-y-6">
            <SimpleAssumptionsPanel
              assumptions={assumptions}
              defaults={defaults}
              onUpdateAssumption={handleUpdateAssumption}
              onResetToDefaults={handleResetToDefaults}
            />
          </div>

          {/* Right Column: Valuation Output */}
          <div className="space-y-6">
            {dcfResponse ? (
              <ValuationOutput
                valuation={dcfResponse.valuation}
                isLoading={isLoading}
              />
            ) : (
              <div className="flex items-center justify-center h-64">
                <div className="text-center">
                  <Calculator className="h-8 w-8 text-slate-400 mx-auto mb-4" />
                  <div className="text-slate-400">Calculating valuation...</div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Price Heat Bar - Full Width */}
        {dcfResponse && (
          <div className="mt-8">
            <PriceHeatBar
              currentPrice={currentPrice || dcfResponse.valuation.current_stock_price}
              intrinsicValue={dcfResponse.valuation.intrinsic_value_per_share}
              companyName={ticker.replace('.NS', '')}
            />
          </div>
        )}

        {/* Sensitivity Analysis - Full Width */}
        {dcfResponse && (
          <div className="mt-8 pt-6 border-t border-slate-700">
            <SensitivityAnalysisComponent
              sensitivity={dcfResponse.sensitivity}
              baseValuation={dcfResponse.valuation}
            />
          </div>
        )}
      </div>
    </motion.div>
  );
};