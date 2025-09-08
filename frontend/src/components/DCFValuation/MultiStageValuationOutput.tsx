import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Calculator, BarChart3, Layers, Eye, EyeOff, Brain } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, ComposedChart } from 'recharts';
import { InfoTooltip } from '../common/InfoTooltip';
import { GrowthWaterfallChart } from './GrowthWaterfallChart';
import { DCFInterpretationPanel } from './DCFInterpretationPanel';
import type { MultiStageDCFResponse } from '../../types';
import { DCFUtils } from '../../utils/dcf';

interface MultiStageValuationOutputProps {
  dcfResponse: MultiStageDCFResponse;
  userLevel?: 'beginner' | 'intermediate' | 'advanced';
  isLoading?: boolean;
}

interface ProjectionChartData {
  year: number;
  revenue: number;
  free_cash_flow: number;
  present_value: number;
  growth_rate: number;
  growth_stage: string;
}

export const MultiStageValuationOutput: React.FC<MultiStageValuationOutputProps> = ({
  dcfResponse,
  userLevel = 'intermediate',
  isLoading = false
}) => {
  const [showDetailedTable, setShowDetailedTable] = useState(false);
  const [activeChart, setActiveChart] = useState<'fcf' | 'pv' | 'growth'>('fcf');

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-slate-700 rounded mb-4"></div>
          <div className="space-y-3">
            <div className="h-4 bg-slate-700 rounded w-3/4"></div>
            <div className="h-4 bg-slate-700 rounded w-1/2"></div>
            <div className="h-4 bg-slate-700 rounded w-5/6"></div>
          </div>
        </div>
      </div>
    );
  }

  const { valuation, mode, growth_stages_summary, education_content } = dcfResponse;
  const isPositive = valuation.upside_downside > 0;

  // Prepare chart data for 10-year projections
  const chartData: ProjectionChartData[] = valuation.projections.map(projection => ({
    year: projection.year,
    revenue: projection.revenue,
    free_cash_flow: projection.free_cash_flow,
    present_value: projection.present_value,
    growth_rate: projection.revenue_growth_rate,
    growth_stage: projection.growth_stage
  }));

  const formatTooltip = (value: number, name: string) => {
    if (name.includes('rate')) {
      return [`${value.toFixed(1)}%`, name.replace('_', ' ').toUpperCase()];
    }
    return [DCFUtils.formatCurrency(value), name.replace('_', ' ').toUpperCase()];
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      {/* Intrinsic Value - Enhanced */}
      <motion.div
        initial={{ scale: 0.95 }}
        animate={{ scale: 1 }}
        transition={{ duration: 0.3 }}
        className="bg-gradient-to-r from-primary-900/20 to-blue-900/20 border border-primary-500/30 rounded-lg p-6"
      >
        <div className="flex items-center space-x-3 mb-2">
          <Calculator className="h-6 w-6 text-primary-400" />
          <h3 className="text-lg font-semibold text-slate-100">10-Year DCF Intrinsic Value</h3>
          <div className={`px-2 py-1 rounded text-xs font-medium ${
            mode === 'simple' 
              ? 'bg-green-500/20 text-green-400'
              : 'bg-blue-500/20 text-blue-400'
          }`}>
            {mode.toUpperCase()} MODE
          </div>
          <InfoTooltip content="The calculated fair value based on 10-year multi-stage cash flow projections with GDP blending. This extends beyond traditional 5-year models to capture long-term value creation." />
        </div>
        
        <div className="flex items-end justify-between">
          <div>
            <div className="text-3xl font-bold text-primary-400 mb-1">
              ₹{valuation.intrinsic_value_per_share.toFixed(2)}
            </div>
            <div className="text-sm text-slate-400">
              Current Price: ₹{valuation.current_stock_price.toFixed(2)}
            </div>
            <div className="text-xs text-slate-500 mt-1">
              {valuation.multi_stage_assumptions.projection_years}-year projection horizon
            </div>
          </div>
          
          <div className="text-right">
            <div className={`flex items-center space-x-2 ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
              {isPositive ? <TrendingUp className="h-5 w-5" /> : <TrendingDown className="h-5 w-5" />}
              <span className="text-xl font-bold">
                {valuation.upside_downside > 0 ? '+' : ''}{valuation.upside_downside.toFixed(1)}%
              </span>
            </div>
            <div className="flex items-center space-x-1">
              <span className="text-xs text-slate-400">
                {isPositive ? 'Upside Potential' : 'Downside Risk'}
              </span>
              <InfoTooltip content={`The percentage difference between intrinsic value and current price using multi-stage DCF. ${isPositive ? 'Positive values suggest the stock may be undervalued' : 'Negative values suggest the stock may be overvalued'}.`} />
            </div>
          </div>
        </div>

        {/* Growth Stages Summary */}
        <div className="mt-4 pt-4 border-t border-slate-700/50">
          <div className="grid grid-cols-4 gap-4 text-center">
            {Object.entries(valuation.growth_waterfall).slice(0, 4).map(([stage, rate]) => (
              <div key={stage} className="space-y-1">
                <div className="text-sm text-slate-400">{stage}</div>
                <div className="text-lg font-bold text-primary-400">{rate.toFixed(1)}%</div>
              </div>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Enhanced Key Metrics */}
      <div className="grid grid-cols-3 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.1 }}
          className="bg-slate-700/30 rounded-lg p-4"
        >
          <div className="flex items-center space-x-2 mb-1">
            <span className="text-sm text-slate-400">Enterprise Value</span>
            <InfoTooltip content="The total value of the business from 10-year discounted cash flows, including the enhanced terminal value calculation." />
          </div>
          <div className="text-xl font-bold text-slate-100">
            {DCFUtils.formatCurrency(valuation.enterprise_value)}
          </div>
        </motion.div>
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.2 }}
          className="bg-slate-700/30 rounded-lg p-4"
        >
          <div className="flex items-center space-x-2 mb-1">
            <span className="text-sm text-slate-400">Terminal Value</span>
            <InfoTooltip content="The estimated value of cash flows beyond the 10-year projection period, using GDP-converged growth rates for enhanced accuracy." />
          </div>
          <div className="text-xl font-bold text-slate-100">
            {DCFUtils.formatCurrency(valuation.terminal_value)}
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.3 }}
          className="bg-slate-700/30 rounded-lg p-4"
        >
          <div className="flex items-center space-x-2 mb-1">
            <span className="text-sm text-slate-400">Avg Growth Rate</span>
            <InfoTooltip content="Weighted average growth rate across all 10-year stages, showing the blended historical and GDP convergence approach." />
          </div>
          <div className="text-xl font-bold text-slate-100">
            {(Object.values(valuation.growth_waterfall).reduce((a, b) => a + b, 0) / Object.values(valuation.growth_waterfall).length).toFixed(1)}%
          </div>
        </motion.div>
      </div>

      {/* Growth Waterfall Chart */}
      <GrowthWaterfallChart
        growthStages={valuation.multi_stage_assumptions.growth_stages}
        growthWaterfall={valuation.growth_waterfall}
        mode={mode}
        userLevel={userLevel}
        educationContent={education_content}
      />

      {/* Chart Selection */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
        className="bg-slate-800/50 rounded-lg p-4"
      >
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <BarChart3 className="h-5 w-5 text-slate-400" />
            <h4 className="text-md font-medium text-slate-300">10-Year Projection Analysis</h4>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setActiveChart('fcf')}
              className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                activeChart === 'fcf' 
                  ? 'bg-primary-500 text-white' 
                  : 'bg-slate-700 text-slate-400 hover:text-slate-300'
              }`}
            >
              Cash Flow
            </button>
            <button
              onClick={() => setActiveChart('pv')}
              className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                activeChart === 'pv' 
                  ? 'bg-primary-500 text-white' 
                  : 'bg-slate-700 text-slate-400 hover:text-slate-300'
              }`}
            >
              Present Value
            </button>
            <button
              onClick={() => setActiveChart('growth')}
              className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                activeChart === 'growth' 
                  ? 'bg-primary-500 text-white' 
                  : 'bg-slate-700 text-slate-400 hover:text-slate-300'
              }`}
            >
              Growth Rates
            </button>
          </div>
        </div>
        
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            {activeChart === 'fcf' ? (
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis 
                  dataKey="year" 
                  stroke="#9ca3af"
                  fontSize={12}
                />
                <YAxis 
                  stroke="#9ca3af"
                  fontSize={12}
                  tickFormatter={(value) => DCFUtils.formatLargeNumber(value)}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1f2937',
                    border: '1px solid #374151',
                    borderRadius: '8px',
                    color: '#f3f4f6'
                  }}
                  formatter={formatTooltip}
                />
                <Bar 
                  dataKey="free_cash_flow" 
                  fill="#0ea5e9" 
                  name="Free Cash Flow"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            ) : activeChart === 'pv' ? (
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis 
                  dataKey="year" 
                  stroke="#9ca3af"
                  fontSize={12}
                />
                <YAxis 
                  stroke="#9ca3af"
                  fontSize={12}
                  tickFormatter={(value) => DCFUtils.formatLargeNumber(value)}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1f2937',
                    border: '1px solid #374151',
                    borderRadius: '8px',
                    color: '#f3f4f6'
                  }}
                  formatter={formatTooltip}
                />
                <Line 
                  type="monotone" 
                  dataKey="present_value" 
                  stroke="#10b981" 
                  strokeWidth={3}
                  name="Present Value"
                  dot={{ fill: '#10b981', strokeWidth: 2, r: 4 }}
                />
              </LineChart>
            ) : (
              <ComposedChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis 
                  dataKey="year" 
                  stroke="#9ca3af"
                  fontSize={12}
                />
                <YAxis 
                  stroke="#9ca3af"
                  fontSize={12}
                  tickFormatter={(value) => `${value}%`}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1f2937',
                    border: '1px solid #374151',
                    borderRadius: '8px',
                    color: '#f3f4f6'
                  }}
                  formatter={formatTooltip}
                />
                <Line 
                  type="monotone" 
                  dataKey="growth_rate" 
                  stroke="#f59e0b" 
                  strokeWidth={3}
                  name="Growth Rate"
                  dot={{ fill: '#f59e0b', strokeWidth: 2, r: 4 }}
                />
              </ComposedChart>
            )}
          </ResponsiveContainer>
        </div>
      </motion.div>

      {/* Educational Content */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        className="bg-gradient-to-r from-blue-900/10 to-purple-900/10 border border-blue-500/20 rounded-lg p-4"
      >
        <div className="flex items-center space-x-2 mb-3">
          <Layers className="h-5 w-5 text-blue-400" />
          <h4 className="text-md font-medium text-slate-300">Understanding This Analysis</h4>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <h5 className="font-medium text-blue-300 mb-1">Key Benefits</h5>
            <p className="text-slate-400">{education_content.key_benefits}</p>
          </div>
          <div>
            <h5 className="font-medium text-blue-300 mb-1">Best For</h5>
            <p className="text-slate-400">{education_content.best_for}</p>
          </div>
        </div>
      </motion.div>

      {/* What This Means - Investment Interpretation */}
      <DCFInterpretationPanel 
        dcfResponse={dcfResponse}
        userLevel={userLevel}
      />

      {/* Assumptions Used - Data Source Transparency */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.5 }}
        className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-5"
      >
        <div className="flex items-center space-x-3 mb-4">
          <Calculator className="h-5 w-5 text-blue-400" />
          <h3 className="text-lg font-semibold text-slate-100">Assumptions Used</h3>
          <div className="px-2 py-1 rounded text-xs font-medium bg-blue-500/20 text-blue-400">
            DATA-DRIVEN
          </div>
        </div>
        
        <div className="space-y-4">
          {/* Historical Company Data */}
          <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4">
            <h4 className="text-sm font-semibold text-green-400 mb-2 flex items-center">
              <TrendingUp className="h-4 w-4 mr-2" />
              Historical Company Data (4 Years)
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
              <div className="text-slate-300">
                <span className="font-medium">Revenue Growth:</span> {valuation.multi_stage_assumptions?.growth_stages?.[0]?.growth_rate || valuation.assumptions.revenue_growth_rate.toFixed(1) + '%'}
                <div className="text-xs text-slate-400 mt-1">From actual financial statements</div>
              </div>
              <div className="text-slate-300">
                <span className="font-medium">EBITDA Margin:</span> {valuation.assumptions.ebitda_margin.toFixed(1)}%
                <div className="text-xs text-slate-400 mt-1">Average from historical performance</div>
              </div>
            </div>
          </div>

          {/* Damodaran Sector Intelligence */}
          <div className="bg-purple-500/10 border border-purple-500/20 rounded-lg p-4">
            <h4 className="text-sm font-semibold text-purple-400 mb-2 flex items-center">
              <Brain className="h-4 w-4 mr-2" />
              Damodaran Sector Intelligence (Expert Data)
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
              <div className="text-slate-300">
                <span className="font-medium">WACC:</span> {valuation.assumptions.wacc.toFixed(1)}%
                <div className="text-xs text-slate-400 mt-1">Sector beta + live risk-free rate</div>
              </div>
              <div className="text-slate-300">
                <span className="font-medium">Tax Rate:</span> {valuation.assumptions.tax_rate.toFixed(1)}%
                <div className="text-xs text-slate-400 mt-1">Sector-specific effective rate</div>
              </div>
              <div className="text-slate-300">
                <span className="font-medium">Terminal Growth:</span> {valuation.assumptions.terminal_growth_rate.toFixed(1)}%
                <div className="text-xs text-slate-400 mt-1">Long-term sector growth rate</div>
              </div>
            </div>
          </div>

          {/* Live Market Data */}
          <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
            <h4 className="text-sm font-semibold text-blue-400 mb-2 flex items-center">
              <BarChart3 className="h-4 w-4 mr-2" />
              Live Market Data
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
              <div className="text-slate-300">
                <span className="font-medium">Current Price:</span> ₹{valuation.current_stock_price.toFixed(2)}
                <div className="text-xs text-slate-400 mt-1">Real-time stock price</div>
              </div>
              <div className="text-slate-300">
                <span className="font-medium">Risk-Free Rate:</span> ~7.2%
                <div className="text-xs text-slate-400 mt-1">10-Year Indian G-Sec yield</div>
              </div>
            </div>
          </div>

          {/* Data Sources Footer */}
          <div className="text-xs text-slate-500 pt-2 border-t border-slate-700">
            <strong>Sources:</strong> Historical data from company financials • Sector intelligence from Aswath Damodaran (NYU Stern) datasets • Live market data from financial APIs
          </div>
        </div>
      </motion.div>

      {/* Detailed Projections Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.6 }}
        className="bg-slate-800/50 rounded-lg p-4"
      >
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <h4 className="text-md font-medium text-slate-300">Detailed 10-Year Projections</h4>
            <InfoTooltip content="Year-by-year breakdown showing revenue growth by stage, cash flow generation, and present value calculations with multi-stage growth methodology." />
          </div>
          <button
            onClick={() => setShowDetailedTable(!showDetailedTable)}
            className="flex items-center space-x-2 text-sm text-slate-400 hover:text-primary-400 transition-colors"
          >
            {showDetailedTable ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            <span>{showDetailedTable ? 'Hide' : 'Show'} Details</span>
          </button>
        </div>
        
        {showDetailedTable && (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left py-2 text-slate-400 font-medium">Year</th>
                  <th className="text-right py-2 text-slate-400 font-medium">Stage</th>
                  <th className="text-right py-2 text-slate-400 font-medium">Growth</th>
                  <th className="text-right py-2 text-slate-400 font-medium">Revenue</th>
                  <th className="text-right py-2 text-slate-400 font-medium">FCF</th>
                  <th className="text-right py-2 text-slate-400 font-medium">PV</th>
                </tr>
              </thead>
              <tbody>
                {valuation.projections.map((projection, index) => (
                  <motion.tr
                    key={projection.year}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3, delay: 0.6 + index * 0.03 }}
                    className="border-b border-slate-800"
                  >
                    <td className="py-2 font-mono text-slate-300">{projection.year}</td>
                    <td className="py-2 text-right text-slate-400 text-xs">{projection.growth_stage}</td>
                    <td className="py-2 text-right text-amber-400 font-mono">
                      {projection.revenue_growth_rate.toFixed(1)}%
                    </td>
                    <td className="py-2 text-right text-slate-300 font-mono">
                      {DCFUtils.formatCurrency(projection.revenue)}
                    </td>
                    <td className="py-2 text-right text-slate-300 font-mono">
                      {DCFUtils.formatCurrency(projection.free_cash_flow)}
                    </td>
                    <td className="py-2 text-right text-green-400 font-mono">
                      {DCFUtils.formatCurrency(projection.present_value)}
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </motion.div>
    </motion.div>
  );
};