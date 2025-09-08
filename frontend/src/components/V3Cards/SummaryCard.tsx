import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, BarChart3 } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import type { SummaryResponse } from '../../types/summary';

interface SummaryCardProps {
  summaryData: SummaryResponse;
  dcfInsights?: {
    fairValue?: number;
    currentPrice?: number;
    upside?: number;
    insights?: any;
  };
  financialMetrics?: {
    revenueCagr?: number;
    ebitdaCagr?: number;
    profitCagr?: number;
    eps?: number;
    pe?: number;
    roe?: number;
  };
  technicalInsights?: {
    summary?: string;
  };
  sentimentInsights?: {
    summary?: string;
  };
  priceData?: {
    [key: string]: Array<{
      date: string;
      price: number;
      timestamp: number;
    }>;
  };
}

export const SummaryCard: React.FC<SummaryCardProps> = ({ 
  summaryData,
  dcfInsights,
  financialMetrics,
  technicalInsights,
  sentimentInsights,
  priceData
}) => {
  // Debug props data
  console.log('🔍 SummaryCard Props Debug:', {
    hasCompanyData: !!summaryData,
    hasDcfInsights: !!dcfInsights,
    hasFinancialMetrics: !!financialMetrics,
    hasTechnicalInsights: !!technicalInsights,
    technicalInsightsData: technicalInsights,
    hasSentimentInsights: !!sentimentInsights,
    hasPriceData: !!priceData
  });
  const [selectedDuration, setSelectedDuration] = useState('1Y');
  
  // Duration options for price chart
  const durationOptions = [
    { label: 'Daily', value: '1D' },
    { label: '1M', value: '1M' },
    { label: '3M', value: '3M' },
    { label: '6M', value: '6M' },
    { label: '1Y', value: '1Y' },
    { label: '3Y', value: '3Y' },
    { label: '5Y', value: '5Y' }
  ];

  // Get price data for selected duration
  const getSelectedPriceData = () => {
    if (priceData && priceData[selectedDuration]) {
      return priceData[selectedDuration];
    }
    
    // Fallback mock data if real data not available
    const currentPrice = dcfInsights?.currentPrice || 1373;
    const dataPoints = selectedDuration === '1D' ? 24 : 
                     selectedDuration === '1M' ? 30 : 
                     selectedDuration === '3M' ? 90 : 
                     selectedDuration === '6M' ? 180 : 
                     selectedDuration === '1Y' ? 252 : 
                     selectedDuration === '3Y' ? 756 : 1260;
    
    const data = [];
    const now = new Date();
    
    for (let i = 0; i < dataPoints; i++) {
      const variation = (Math.random() - 0.5) * 50;
      const price = Math.max(currentPrice + variation, currentPrice * 0.8);
      
      // Calculate actual date based on duration
      let date = new Date(now);
      if (selectedDuration === '1D') {
        // For daily, show hourly intervals
        date.setHours(9 + Math.floor(i/4), (i%4)*15, 0, 0);
        data.push({
          date: date.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }),
          price: Math.round(price * 100) / 100,
          timestamp: date.getTime()
        });
      } else {
        // For other durations, show actual dates
        const daysBack = selectedDuration === '1M' ? 30 : 
                        selectedDuration === '3M' ? 90 : 
                        selectedDuration === '6M' ? 180 : 
                        selectedDuration === '1Y' ? 252 : 
                        selectedDuration === '3Y' ? 756 : 1260;
        
        // Start from daysBack ago and go forward to today
        date.setDate(date.getDate() - daysBack + Math.floor((i * daysBack) / (dataPoints - 1)));
        
        // Ensure the last data point is today
        if (i === dataPoints - 1) {
          date = new Date(now); // Set to today
        }
        data.push({
          date: date.toLocaleDateString('en-IN', { 
            month: 'short', 
            day: 'numeric',
            year: selectedDuration === '3Y' || selectedDuration === '5Y' ? 'numeric' : undefined
          }),
          price: Math.round(price * 100) / 100,
          timestamp: date.getTime()
        });
      }
    }
    return data;
  };

  const chartData = getSelectedPriceData();
  const {
    ticker,
    company_name,
    sector,
    analysis_mode,
    data_health_warnings
  } = summaryData;

  // Get current price from the latest data point
  const currentPrice = chartData.length > 0 ? chartData[chartData.length - 1].price : (dcfInsights?.currentPrice || 1373);


  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-slate-800 rounded-xl p-6 border border-slate-700"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-slate-100">{company_name}</h2>
          <div className="flex items-center space-x-3 mt-1">
            <span className="text-slate-400">{ticker}</span>
            <span className="text-slate-500">•</span>
            <span className="text-slate-400">{sector}</span>
            <span className="text-slate-500">•</span>
            <span className="text-xs text-slate-500 capitalize">{analysis_mode} mode</span>
          </div>
        </div>
        
        {/* Duration Selector */}
        <div className="flex items-center space-x-1">
          {durationOptions.map((option) => (
            <button
              key={option.value}
              onClick={() => setSelectedDuration(option.value)}
              className={`px-2 py-1 text-xs rounded-md transition-colors ${
                selectedDuration === option.value
                  ? 'bg-primary-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {/* Price Chart */}
      <div className="mb-6">
        <div className="bg-slate-900/30 rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <BarChart3 className="h-4 w-4 text-primary-400" />
              <span className="text-primary-400 font-medium text-sm">Price Chart</span>
            </div>
            <div className="text-sm text-slate-300">
              Current: <span className="font-semibold text-primary-300">₹{currentPrice.toFixed(2)}</span>
            </div>
          </div>
          
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis 
                  dataKey="date" 
                  stroke="#9CA3AF"
                  fontSize={10}
                  interval="preserveStartEnd"
                />
                <YAxis 
                  stroke="#9CA3AF"
                  fontSize={10}
                  domain={['dataMin - 50', 'dataMax + 50']}
                  tickFormatter={(value) => `₹${value.toFixed(0)}`}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1F2937',
                    border: '1px solid #374151',
                    borderRadius: '8px',
                    color: '#F3F4F6'
                  }}
                  formatter={(value: any) => [`₹${value.toFixed(2)}`, 'Price']}
                  labelFormatter={(label) => `Date: ${label}`}
                />
                <Line
                  type="monotone"
                  dataKey="price"
                  stroke="#3B82F6"
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 4, fill: '#3B82F6' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>



      {/* Data Health Warnings - Only show in agentic mode */}
      {analysis_mode === 'agentic' && data_health_warnings && data_health_warnings.length > 0 && (
        <div className="bg-yellow-900/20 border border-yellow-500/30 rounded-lg p-4 mt-4">
          <div className="flex items-start space-x-2">
            <AlertTriangle className="h-4 w-4 text-yellow-400 mt-0.5 flex-shrink-0" />
            <div>
              <div className="text-yellow-300 font-medium text-sm mb-1">Data Quality Alerts</div>
              <div className="space-y-1">
                {data_health_warnings.map((warning, index) => (
                  <div key={index} className="text-yellow-200 text-xs">{warning}</div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </motion.div>
  );
};