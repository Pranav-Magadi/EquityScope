import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Calculator, BarChart3 } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { InfoTooltip } from '../common/InfoTooltip';
import type { DCFValuation } from '../../types';
import { DCFUtils } from '../../utils/dcf';

interface ValuationOutputProps {
  valuation: DCFValuation;
  isLoading?: boolean;
}

export const ValuationOutput: React.FC<ValuationOutputProps> = ({
  valuation,
  isLoading = false
}) => {
  const isPositive = valuation.upside_downside > 0;
  const chartData = DCFUtils.convertToChartData(valuation.projections);

  const formatTooltip = (value: number, name: string) => {
    return [DCFUtils.formatCurrency(value), name.replace('_', ' ').toUpperCase()];
  };

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

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      {/* Intrinsic Value */}
      <motion.div
        initial={{ scale: 0.95 }}
        animate={{ scale: 1 }}
        transition={{ duration: 0.3 }}
        className="bg-gradient-to-r from-primary-900/20 to-blue-900/20 border border-primary-500/30 rounded-lg p-6"
      >
        <div className="flex items-center space-x-3 mb-2">
          <Calculator className="h-6 w-6 text-primary-400" />
          <h3 className="text-lg font-semibold text-slate-100">Intrinsic Value Per Share</h3>
          <InfoTooltip content="The calculated fair value of one share based on projected future cash flows discounted to present value. Compare this to the current market price to assess if the stock is undervalued or overvalued." />
        </div>
        
        <div className="flex items-end justify-between">
          <div>
            <div className="text-3xl font-bold text-primary-400 mb-1">
              ₹{valuation.intrinsic_value_per_share.toFixed(2)}
            </div>
            <div className="text-sm text-slate-400">
              Current Price: ₹{valuation.current_stock_price.toFixed(2)}
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
              <InfoTooltip content={`The percentage difference between intrinsic value and current price. ${isPositive ? 'Positive values suggest the stock may be undervalued' : 'Negative values suggest the stock may be overvalued'}.`} />
            </div>
          </div>
        </div>
      </motion.div>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.1 }}
          className="bg-slate-700/30 rounded-lg p-4"
        >
          <div className="flex items-center space-x-2 mb-1">
            <span className="text-sm text-slate-400">Enterprise Value</span>
            <InfoTooltip content="The total value of the business, calculated as the sum of all discounted future cash flows. This represents what the entire company is worth." />
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
            <InfoTooltip content="The estimated value of cash flows beyond the 5-year projection period, assuming steady long-term growth. This typically represents 60-80% of total enterprise value." />
          </div>
          <div className="text-xl font-bold text-slate-100">
            {DCFUtils.formatCurrency(valuation.terminal_value)}
          </div>
        </motion.div>
      </div>

      {/* Projected Free Cash Flow Chart */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
        className="bg-slate-800/50 rounded-lg p-4"
      >
        <div className="flex items-center space-x-2 mb-4">
          <BarChart3 className="h-5 w-5 text-slate-400" />
          <h4 className="text-md font-medium text-slate-300">5-Year Cash Flow Projection</h4>
          <InfoTooltip content="Projected annual free cash flows based on your assumptions. Free cash flow is the cash available to shareholders after necessary capital expenditures." />
        </div>
        
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
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
          </ResponsiveContainer>
        </div>
      </motion.div>

      {/* Present Value Chart */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        className="bg-slate-800/50 rounded-lg p-4"
      >
        <div className="flex items-center space-x-2 mb-4">
          <h4 className="text-md font-medium text-slate-300">Present Value of Cash Flows</h4>
          <InfoTooltip content="The current worth of projected future cash flows, discounted using your WACC assumption. This shows how much future cash flows are worth in today's money." />
        </div>
        
        <div className="h-48">
          <ResponsiveContainer width="100%" height="100%">
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
          </ResponsiveContainer>
        </div>
      </motion.div>

      {/* Detailed Projections Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.5 }}
        className="bg-slate-800/50 rounded-lg p-4"
      >
        <div className="flex items-center space-x-2 mb-4">
          <h4 className="text-md font-medium text-slate-300">Detailed Cash Flow Projections</h4>
          <InfoTooltip content="Year-by-year breakdown showing revenue growth, EBITDA calculation, free cash flow generation, and present value calculations." />
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="text-left py-2 text-slate-400 font-medium">Year</th>
                <th className="text-right py-2 text-slate-400 font-medium">Revenue</th>
                <th className="text-right py-2 text-slate-400 font-medium">EBITDA</th>
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
                  transition={{ duration: 0.3, delay: 0.6 + index * 0.05 }}
                  className="border-b border-slate-800"
                >
                  <td className="py-2 font-mono text-slate-300">{projection.year}</td>
                  <td className="py-2 text-right text-slate-300 font-mono">
                    {DCFUtils.formatCurrency(projection.revenue)}
                  </td>
                  <td className="py-2 text-right text-slate-300 font-mono">
                    {DCFUtils.formatCurrency(projection.ebitda)}
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
      </motion.div>
    </motion.div>
  );
};