import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { 
  TrendingUp, 
  TrendingDown, 
  BarChart3, 
  Activity,
  ChevronDown,
  AlertCircle,
  Info,
  Loader2,
  Volume2,
  Zap,
  Settings
} from 'lucide-react';
import { 
  ComposedChart, 
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  ReferenceLine,
  BarChart
} from 'recharts';
import type { TechnicalAnalysisData } from '../../types';

interface TechnicalAnalysisCardProps {
  ticker: string;
  useAgenticMode: boolean;
  onTechnicalInsightsUpdate?: (insights: any) => void;
  onPriceDataUpdate?: (priceData: any) => void;
}

const PERIOD_OPTIONS = [
  { value: '3mo', label: '3 Months' },
  { value: '6mo', label: '6 Months' },
  { value: '1y', label: '1 Year' },
  { value: '3y', label: '3 Years' }
];

export const TechnicalAnalysisCard: React.FC<TechnicalAnalysisCardProps> = ({
  ticker,
  useAgenticMode,
  onTechnicalInsightsUpdate,
  onPriceDataUpdate
}) => {
  const [selectedPeriod, setSelectedPeriod] = useState('1y');
  const [technicalData, setTechnicalData] = useState<TechnicalAnalysisData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  
  // Indicator visibility toggles
  const [showIndicators, setShowIndicators] = useState({
    macd: true,
    stochastic: true,
    volume: true,
    bollinger: true,
    rsi: true
  });
  const [indicatorDropdownOpen, setIndicatorDropdownOpen] = useState(false);

  const fetchTechnicalAnalysis = useCallback(async (period: string) => {
    if (!ticker) return;
    
    setLoading(true);
    setError(null);
    
    try {
      // Include mode in API call - backend should only return ai_summary for Agent mode
      const modeParam = useAgenticMode ? 'agentic' : 'simple';
      const response = await fetch(`/api/valuation/${ticker}/technical-analysis?period=${period}&mode=${modeParam}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      
      // Debug logging to understand what data is being returned
      console.log('🔍 Technical Analysis Debug:', {
        mode: modeParam,
        useAgenticMode,
        hasAiSummary: !!data.ai_summary,
        aiSummaryLength: data.ai_summary?.length,
        aiSummaryPreview: data.ai_summary?.substring(0, 100) + '...'
      });
      
      setTechnicalData(data);
      
      // Emit technical insights to parent component - only in Agent mode
      if (onTechnicalInsightsUpdate && useAgenticMode && data.ai_summary) {
        console.log('🔄 Technical Insights Update Called:', {
          callbackExists: !!onTechnicalInsightsUpdate,
          agenticMode: useAgenticMode,
          hasAiSummary: !!data.ai_summary,
          summaryLength: data.ai_summary?.length
        });
        
        // Create short summary for Summary box (first 3-4 sentences)
        const shortSummary = data.ai_summary.split('.').slice(0, 3).join('.').trim() + 
                            (data.ai_summary.split('.').length > 3 ? '.' : '');
        
        onTechnicalInsightsUpdate({
          summary: shortSummary,
          fullSummary: data.ai_summary
        });
      }
      
      // Emit price data to parent component for chart
      if (onPriceDataUpdate && data.price_data) {
        onPriceDataUpdate({
          [selectedPeriod]: data.price_data
        });
      }
    } catch (err) {
      console.error('Error fetching technical analysis:', err);
      setError('Failed to load technical analysis data');
      setTechnicalData(null);
    } finally {
      setLoading(false);
    }
  }, [ticker]);

  useEffect(() => {
    fetchTechnicalAnalysis(selectedPeriod);
  }, [ticker, selectedPeriod, fetchTechnicalAnalysis]);

  // Transform data for Recharts
  const chartData = technicalData?.chart_data.map(point => ({
    date: new Date(point.timestamp * 1000).toLocaleDateString(),
    timestamp: point.timestamp,
    open: point.open,
    high: point.high,
    low: point.low,
    close: point.close,
    volume: point.volume,
    sma_50: point.sma_50,
    sma_200: point.sma_200,
    bb_upper: point.bb_upper,
    bb_lower: point.bb_lower,
    bb_middle: point.bb_middle,
    rsi: point.rsi,
    // New indicators
    macd_line: point.macd_line,
    macd_signal: point.macd_signal,
    macd_histogram: point.macd_histogram,
    stoch_k: point.stoch_k,
    stoch_d: point.stoch_d,
    volume_sma: point.volume_sma,
    obv: point.obv
  })) ?? [];

  // Helper function to format volume
  const formatVolume = (volume: number) => {
    if (volume >= 10000000) return `${(volume / 10000000).toFixed(1)}Cr`;
    if (volume >= 100000) return `${(volume / 100000).toFixed(1)}L`;
    if (volume >= 1000) return `${(volume / 1000).toFixed(1)}K`;
    return volume.toString();
  };

  // Helper function to format price dynamically based on price range
  const formatPrice = (price: number) => {
    if (price >= 10000) return `₹${(price / 1000).toFixed(1)}K`;  // ₹50K for expensive stocks
    if (price >= 1000) return `₹${price.toFixed(0)}`;             // ₹1,400 for normal stocks  
    if (price >= 100) return `₹${price.toFixed(1)}`;              // ₹150.5 for mid-range stocks
    if (price >= 10) return `₹${price.toFixed(2)}`;               // ₹15.25 for lower-priced stocks
    return `₹${price.toFixed(3)}`;                                // ₹2.150 for penny stocks
  };

  // Custom tooltip for price chart
  const PriceTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-slate-800 border border-slate-600 rounded-lg p-3 text-sm">
          <p className="text-slate-300 mb-2">{label}</p>
          <div className="space-y-1">
            <p className="text-green-400">Open: {formatPrice(data.open)}</p>
            <p className="text-blue-400">High: {formatPrice(data.high)}</p>
            <p className="text-red-400">Low: {formatPrice(data.low)}</p>
            <p className="text-slate-100">Close: {formatPrice(data.close)}</p>
            {data.volume && <p className="text-gray-400">Volume: {formatVolume(data.volume)}</p>}
            {data.sma_50 && <p className="text-blue-300">SMA 50: {formatPrice(data.sma_50)}</p>}
            {data.sma_200 && <p className="text-amber-300">SMA 200: {formatPrice(data.sma_200)}</p>}
          </div>
        </div>
      );
    }
    return null;
  };

  // Custom tooltip for RSI chart
  const RSITooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const rsi = payload[0].value;
      return (
        <div className="bg-slate-800 border border-slate-600 rounded-lg p-3 text-sm">
          <p className="text-slate-300 mb-2">{label}</p>
          <p className="text-cyan-400">RSI: {rsi?.toFixed(1)}</p>
        </div>
      );
    }
    return null;
  };

  // Custom tooltip for MACD chart
  const MACDTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-slate-800 border border-slate-600 rounded-lg p-3 text-sm">
          <p className="text-slate-300 mb-2">{label}</p>
          <div className="space-y-1">
            {data.macd_line && <p className="text-blue-400">MACD: {data.macd_line.toFixed(3)}</p>}
            {data.macd_signal && <p className="text-orange-400">Signal: {data.macd_signal.toFixed(3)}</p>}
            {data.macd_histogram && <p className="text-purple-400">Histogram: {data.macd_histogram.toFixed(3)}</p>}
          </div>
        </div>
      );
    }
    return null;
  };

  // Custom tooltip for Stochastic chart
  const StochasticTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-slate-800 border border-slate-600 rounded-lg p-3 text-sm">
          <p className="text-slate-300 mb-2">{label}</p>
          <div className="space-y-1">
            {data.stoch_k && <p className="text-green-400">%K: {data.stoch_k.toFixed(1)}</p>}
            {data.stoch_d && <p className="text-red-400">%D: {data.stoch_d.toFixed(1)}</p>}
          </div>
        </div>
      );
    }
    return null;
  };

  const getRSIStatus = (rsi: number) => {
    if (rsi >= 70) return { status: 'Overbought', color: 'text-red-400', icon: TrendingDown };
    if (rsi <= 30) return { status: 'Oversold', color: 'text-green-400', icon: TrendingUp };
    return { status: 'Neutral', color: 'text-slate-400', icon: Activity };
  };

  // MACD signal interpretation
  const getMACDStatus = (macd: number, signal: number) => {
    const diff = macd - signal;
    if (diff > 0.5) return { status: 'Bullish', color: 'text-green-400', icon: TrendingUp };
    if (diff < -0.5) return { status: 'Bearish', color: 'text-red-400', icon: TrendingDown };
    return { status: 'Neutral', color: 'text-slate-400', icon: Activity };
  };

  // Stochastic signal interpretation
  const getStochasticStatus = (k: number, d: number) => {
    if (k >= 80 && d >= 80) return { status: 'Overbought', color: 'text-red-400', icon: TrendingDown };
    if (k <= 20 && d <= 20) return { status: 'Oversold', color: 'text-green-400', icon: TrendingUp };
    if (k > d) return { status: 'Bullish Cross', color: 'text-green-400', icon: TrendingUp };
    if (k < d) return { status: 'Bearish Cross', color: 'text-red-400', icon: TrendingDown };
    return { status: 'Neutral', color: 'text-slate-400', icon: Activity };
  };

  // Volume trend interpretation
  const getVolumeStatus = (trend: string) => {
    if (trend === 'increasing') return { status: 'Accumulating', color: 'text-green-400', icon: Volume2 };
    if (trend === 'decreasing') return { status: 'Distributing', color: 'text-red-400', icon: Volume2 };
    return { status: 'Neutral', color: 'text-slate-400', icon: Volume2 };
  };

  const handlePeriodChange = (period: string) => {
    setSelectedPeriod(period);
    setDropdownOpen(false);
  };

  const toggleIndicator = (indicator: keyof typeof showIndicators) => {
    setShowIndicators(prev => ({
      ...prev,
      [indicator]: !prev[indicator]
    }));
  };

  if (loading) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-slate-800/50 rounded-lg border border-slate-700/50 p-6"
      >
        <div className="flex items-center justify-center h-64">
          <div className="flex flex-col items-center space-y-4">
            <Loader2 className="h-8 w-8 text-blue-400 animate-spin" />
            <p className="text-slate-400">Loading technical analysis...</p>
          </div>
        </div>
      </motion.div>
    );
  }

  if (error) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-slate-800/50 rounded-lg border border-slate-700/50 p-6"
      >
        <div className="flex items-center justify-center h-64">
          <div className="flex flex-col items-center space-y-4">
            <AlertCircle className="h-8 w-8 text-red-400" />
            <p className="text-red-300">{error}</p>
            <button
              onClick={() => fetchTechnicalAnalysis(selectedPeriod)}
              className="btn-primary"
            >
              Retry
            </button>
          </div>
        </div>
      </motion.div>
    );
  }

  if (!technicalData) return null;

  const rsiStatus = getRSIStatus(technicalData.indicator_values.rsi);
  const RSIIcon = rsiStatus.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="bg-slate-800/50 rounded-lg border border-slate-700/50 overflow-hidden"
    >
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-600 rounded-lg">
              <BarChart3 className="h-6 w-6 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-slate-100">Technical Analysis Summary</h3>
              <p className="text-sm text-slate-400">Advanced indicators and price charts</p>
            </div>
          </div>

          {/* Controls */}
          <div className="flex items-center space-x-3">
            {/* Indicator Toggle */}
            <div className="relative">
              <button
                onClick={() => setIndicatorDropdownOpen(!indicatorDropdownOpen)}
                className="flex items-center space-x-2 px-3 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg border border-slate-600 text-slate-200 transition-colors"
              >
                <Settings className="h-4 w-4" />
                <span className="hidden sm:inline">Indicators</span>
                <ChevronDown className={`h-4 w-4 transition-transform ${indicatorDropdownOpen ? 'rotate-180' : ''}`} />
              </button>

              {indicatorDropdownOpen && (
                <div className="absolute right-0 top-full mt-2 w-48 bg-slate-700 border border-slate-600 rounded-lg shadow-lg z-20">
                  {Object.entries(showIndicators).map(([key, value]) => (
                    <button
                      key={key}
                      onClick={() => toggleIndicator(key as keyof typeof showIndicators)}
                      className="w-full text-left px-4 py-2 text-sm hover:bg-slate-600 transition-colors flex items-center justify-between"
                    >
                      <span className="text-slate-200 capitalize">{key.toUpperCase()}</span>
                      <div className={`w-4 h-4 rounded border-2 ${value ? 'bg-blue-500 border-blue-500' : 'border-slate-400'}`}>
                        {value && <div className="w-full h-full flex items-center justify-center text-white text-xs">✓</div>}
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Period Selector */}
            <div className="relative">
              <button
                onClick={() => setDropdownOpen(!dropdownOpen)}
                className="flex items-center space-x-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg border border-slate-600 text-slate-200 transition-colors"
              >
                <span>{PERIOD_OPTIONS.find(p => p.value === selectedPeriod)?.label}</span>
                <ChevronDown className={`h-4 w-4 transition-transform ${dropdownOpen ? 'rotate-180' : ''}`} />
              </button>

              {dropdownOpen && (
                <div className="absolute right-0 top-full mt-2 w-40 bg-slate-700 border border-slate-600 rounded-lg shadow-lg z-10">
                  {PERIOD_OPTIONS.map((option) => (
                    <button
                      key={option.value}
                      onClick={() => handlePeriodChange(option.value)}
                      className={`w-full text-left px-4 py-2 text-sm hover:bg-slate-600 transition-colors ${
                        selectedPeriod === option.value ? 'text-blue-400 bg-slate-600' : 'text-slate-200'
                      }`}
                    >
                      {option.label}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Key Indicators Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-6">
          {/* RSI */}
          {showIndicators.rsi && (
            <div className="bg-slate-700/30 rounded-lg p-3">
              <div className="text-xs text-slate-400 mb-1">RSI (14)</div>
              <div className={`text-lg font-semibold ${rsiStatus.color} flex items-center space-x-2`}>
                <RSIIcon className="h-4 w-4" />
                <span>{technicalData.indicator_values.rsi.toFixed(1)}</span>
              </div>
              <div className="text-xs text-slate-500">{rsiStatus.status}</div>
            </div>
          )}

          {/* MACD */}
          {showIndicators.macd && technicalData.indicator_values.macd_current !== undefined && (
            <div className="bg-slate-700/30 rounded-lg p-3">
              <div className="text-xs text-slate-400 mb-1">MACD</div>
              <div className={`text-lg font-semibold ${getMACDStatus(technicalData.indicator_values.macd_current, technicalData.indicator_values.macd_signal_current).color} flex items-center space-x-2`}>
                <Zap className="h-4 w-4" />
                <span>{technicalData.indicator_values.macd_current.toFixed(3)}</span>
              </div>
              <div className="text-xs text-slate-500">{getMACDStatus(technicalData.indicator_values.macd_current, technicalData.indicator_values.macd_signal_current).status}</div>
            </div>
          )}

          {/* Stochastic */}
          {showIndicators.stochastic && technicalData.indicator_values.stoch_k_current !== undefined && (
            <div className="bg-slate-700/30 rounded-lg p-3">
              <div className="text-xs text-slate-400 mb-1">Stochastic</div>
              <div className={`text-lg font-semibold ${getStochasticStatus(technicalData.indicator_values.stoch_k_current, technicalData.indicator_values.stoch_d_current).color} flex items-center space-x-2`}>
                <Activity className="h-4 w-4" />
                <span>{technicalData.indicator_values.stoch_k_current.toFixed(1)}</span>
              </div>
              <div className="text-xs text-slate-500">{getStochasticStatus(technicalData.indicator_values.stoch_k_current, technicalData.indicator_values.stoch_d_current).status}</div>
            </div>
          )}

          {/* Volume */}
          {showIndicators.volume && technicalData.indicator_values.volume_trend && (
            <div className="bg-slate-700/30 rounded-lg p-3">
              <div className="text-xs text-slate-400 mb-1">Volume</div>
              <div className={`text-lg font-semibold ${getVolumeStatus(technicalData.indicator_values.volume_trend).color} flex items-center space-x-2`}>
                <Volume2 className="h-4 w-4" />
                <span>OBV</span>
              </div>
              <div className="text-xs text-slate-500">{getVolumeStatus(technicalData.indicator_values.volume_trend).status}</div>
            </div>
          )}

          {/* Support */}
          <div className="bg-slate-700/30 rounded-lg p-3">
            <div className="text-xs text-slate-400 mb-1">Support</div>
            <div className="text-lg font-semibold text-green-400">
              ₹{technicalData.indicator_values.support_level.toFixed(2)}
            </div>
            <div className="text-xs text-slate-500">Key level</div>
          </div>

          {/* Resistance */}
          <div className="bg-slate-700/30 rounded-lg p-3">
            <div className="text-xs text-slate-400 mb-1">Resistance</div>
            <div className="text-lg font-semibold text-red-400">
              ₹{technicalData.indicator_values.resistance_level.toFixed(2)}
            </div>
            <div className="text-xs text-slate-500">Key level</div>
          </div>
        </div>

        {/* AI Technical Summary (Only in Agentic Mode) - Full rich details */}
        {useAgenticMode && technicalData.ai_summary && (
          <div className="bg-blue-900/10 border border-blue-500/20 rounded-lg p-4 mb-6">
            <div className="flex items-center space-x-2 mb-3">
              <Activity className="h-5 w-5 text-blue-400" />
              <h4 className="font-semibold text-blue-300">AI Technical Summary</h4>
            </div>
            <div className="text-blue-200 text-sm leading-relaxed">
              <p className="whitespace-pre-line">{technicalData.ai_summary}</p>
            </div>
          </div>
        )}

        {/* Price Chart */}
        <div className="mb-6">
          <div className="flex items-center space-x-2 mb-3">
            <h4 className="text-lg font-semibold text-slate-100">Price & Volume Chart</h4>
            <div title="Price chart with technical indicators and volume">
              <Info className="h-4 w-4 text-slate-400" />
            </div>
          </div>
          <div className="bg-slate-900/50 rounded-lg p-4">
            <ResponsiveContainer width="100%" height={showIndicators.volume ? 500 : 400}>
              <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis 
                  dataKey="date" 
                  stroke="#64748b"
                  fontSize={12}
                  label={{ value: 'Date', position: 'insideBottom', offset: -5, style: { textAnchor: 'middle', fill: '#64748b' } }}
                />
                <YAxis 
                  yAxisId="price"
                  stroke="#64748b"
                  fontSize={12}
                  domain={['dataMin - 50', 'dataMax + 50']}
                  label={{ value: 'Price (₹)', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle', fill: '#64748b' } }}
                  tickFormatter={(value) => formatPrice(value)}
                />
                {showIndicators.volume && (
                  <YAxis 
                    yAxisId="volume"
                    orientation="right"
                    stroke="#64748b"
                    fontSize={12}
                    label={{ value: 'Volume', angle: 90, position: 'insideRight', style: { textAnchor: 'middle', fill: '#64748b' } }}
                    tickFormatter={(value) => {
                      if (value >= 10000000) return `${(value / 10000000).toFixed(1)}Cr`;
                      if (value >= 100000) return `${(value / 100000).toFixed(1)}L`;
                      if (value >= 1000) return `${(value / 1000).toFixed(1)}K`;
                      return value.toString();
                    }}
                  />
                )}
                <Tooltip content={<PriceTooltip />} />
                <Legend />
                
                {/* Volume Bars */}
                {showIndicators.volume && (
                  <Bar 
                    yAxisId="volume"
                    dataKey="volume" 
                    fill="#64748b" 
                    fillOpacity={0.3}
                    name="Volume"
                  />
                )}
                
                {/* Bollinger Bands */}
                {showIndicators.bollinger && (
                  <>
                    <Line 
                      yAxisId="price"
                      type="monotone" 
                      dataKey="bb_upper" 
                      stroke="#8b5cf6" 
                      strokeWidth={1}
                      strokeDasharray="5 5"
                      dot={false}
                      name="BB Upper"
                      connectNulls={false}
                    />
                    <Line 
                      yAxisId="price"
                      type="monotone" 
                      dataKey="bb_lower" 
                      stroke="#8b5cf6" 
                      strokeWidth={1}
                      strokeDasharray="5 5"
                      dot={false}
                      name="BB Lower"
                      connectNulls={false}
                    />
                    <Line 
                      yAxisId="price"
                      type="monotone" 
                      dataKey="bb_middle" 
                      stroke="#8b5cf6" 
                      strokeWidth={1}
                      strokeDasharray="2 2"
                      dot={false}
                      name="BB Middle"
                      connectNulls={false}
                    />
                  </>
                )}
                
                {/* Moving Averages */}
                <Line 
                  yAxisId="price"
                  type="monotone" 
                  dataKey="sma_50" 
                  stroke="#3b82f6" 
                  strokeWidth={2}
                  dot={false}
                  name="SMA 50"
                  connectNulls={false}
                />
                <Line 
                  yAxisId="price"
                  type="monotone" 
                  dataKey="sma_200" 
                  stroke="#f59e0b" 
                  strokeWidth={2}
                  dot={false}
                  name="SMA 200"
                  connectNulls={false}
                />
                
                {/* Close Price */}
                <Line 
                  yAxisId="price"
                  type="monotone" 
                  dataKey="close" 
                  stroke="#10b981" 
                  strokeWidth={2}
                  dot={false}
                  name="Close Price"
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* RSI Chart */}
        {showIndicators.rsi && (
          <div className="mb-6">
            <div className="flex items-center space-x-2 mb-3">
              <h4 className="text-lg font-semibold text-slate-100">RSI (Relative Strength Index)</h4>
              <div title="RSI with overbought (70) and oversold (30) levels">
                <Info className="h-4 w-4 text-slate-400" />
              </div>
            </div>
            <div className="bg-slate-900/50 rounded-lg p-4">
              <ResponsiveContainer width="100%" height={150}>
                <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis 
                    dataKey="date" 
                    stroke="#64748b"
                    fontSize={12}
                    label={{ value: 'Date', position: 'insideBottom', offset: -5, style: { textAnchor: 'middle', fill: '#64748b' } }}
                  />
                  <YAxis 
                    stroke="#64748b"
                    fontSize={12}
                    domain={[0, 100]}
                    label={{ value: 'RSI', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle', fill: '#64748b' } }}
                    tickFormatter={(value) => `${value}`}
                  />
                  <Tooltip content={<RSITooltip />} />
                  <Legend />
                  
                  {/* RSI Line */}
                  <Line 
                    type="monotone" 
                    dataKey="rsi" 
                    stroke="#06b6d4" 
                    strokeWidth={2}
                    dot={false}
                    name="RSI"
                    connectNulls={false}
                  />
                  
                  {/* Reference Lines */}
                  <ReferenceLine y={70} stroke="#ef4444" strokeDasharray="2 2" label="Overbought" />
                  <ReferenceLine y={30} stroke="#10b981" strokeDasharray="2 2" label="Oversold" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* MACD Chart */}
        {showIndicators.macd && (
          <div className="mb-6">
            <div className="flex items-center space-x-2 mb-3">
              <h4 className="text-lg font-semibold text-slate-100">MACD (Moving Average Convergence Divergence)</h4>
              <div title="MACD line, signal line, and histogram">
                <Info className="h-4 w-4 text-slate-400" />
              </div>
            </div>
            <div className="bg-slate-900/50 rounded-lg p-4">
              <ResponsiveContainer width="100%" height={200}>
                <ComposedChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis 
                    dataKey="date" 
                    stroke="#64748b"
                    fontSize={12}
                    label={{ value: 'Date', position: 'insideBottom', offset: -5, style: { textAnchor: 'middle', fill: '#64748b' } }}
                  />
                  <YAxis 
                    stroke="#64748b"
                    fontSize={12}
                    label={{ value: 'MACD', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle', fill: '#64748b' } }}
                    tickFormatter={(value) => value.toFixed(2)}
                  />
                  <Tooltip content={<MACDTooltip />} />
                  <Legend />
                  
                  {/* MACD Histogram */}
                  <Bar 
                    dataKey="macd_histogram" 
                    fill="#8b5cf6"
                    fillOpacity={0.6}
                    name="MACD Histogram"
                  />
                  
                  {/* MACD Line */}
                  <Line 
                    type="monotone" 
                    dataKey="macd_line" 
                    stroke="#3b82f6" 
                    strokeWidth={2}
                    dot={false}
                    name="MACD"
                    connectNulls={false}
                  />
                  
                  {/* Signal Line */}
                  <Line 
                    type="monotone" 
                    dataKey="macd_signal" 
                    stroke="#f59e0b" 
                    strokeWidth={2}
                    dot={false}
                    name="Signal"
                    connectNulls={false}
                  />
                  
                  {/* Zero Line */}
                  <ReferenceLine y={0} stroke="#64748b" strokeDasharray="2 2" />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* Stochastic Chart */}
        {showIndicators.stochastic && (
          <div className="mb-6">
            <div className="flex items-center space-x-2 mb-3">
              <h4 className="text-lg font-semibold text-slate-100">Stochastic Oscillator</h4>
              <div title="Stochastic %K and %D lines with overbought/oversold levels">
                <Info className="h-4 w-4 text-slate-400" />
              </div>
            </div>
            <div className="bg-slate-900/50 rounded-lg p-4">
              <ResponsiveContainer width="100%" height={150}>
                <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis 
                    dataKey="date" 
                    stroke="#64748b"
                    fontSize={12}
                    label={{ value: 'Date', position: 'insideBottom', offset: -5, style: { textAnchor: 'middle', fill: '#64748b' } }}
                  />
                  <YAxis 
                    stroke="#64748b"
                    fontSize={12}
                    domain={[0, 100]}
                    label={{ value: 'Stochastic', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle', fill: '#64748b' } }}
                    tickFormatter={(value) => `${value}%`}
                  />
                  <Tooltip content={<StochasticTooltip />} />
                  <Legend />
                  
                  {/* %K Line (Fast) */}
                  <Line 
                    type="monotone" 
                    dataKey="stoch_k" 
                    stroke="#10b981" 
                    strokeWidth={2}
                    dot={false}
                    name="%K"
                    connectNulls={false}
                  />
                  
                  {/* %D Line (Slow) */}
                  <Line 
                    type="monotone" 
                    dataKey="stoch_d" 
                    stroke="#ef4444" 
                    strokeWidth={2}
                    dot={false}
                    name="%D"
                    connectNulls={false}
                  />
                  
                  {/* Reference Lines */}
                  <ReferenceLine y={80} stroke="#ef4444" strokeDasharray="2 2" label="Overbought" />
                  <ReferenceLine y={20} stroke="#10b981" strokeDasharray="2 2" label="Oversold" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}


        {/* Technical Signals */}
        {technicalData.indicator_values.signals && technicalData.indicator_values.signals.length > 0 && (
          <div className="mt-4 bg-slate-700/30 rounded-lg p-4">
            <h4 className="font-semibold text-slate-100 mb-2">Technical Signals</h4>
            <div className="space-y-1">
              {technicalData.indicator_values.signals.map((signal: string, index: number) => (
                <div key={index} className="flex items-center space-x-2 text-sm text-slate-300">
                  <div className="w-1.5 h-1.5 bg-yellow-400 rounded-full"></div>
                  <span>{signal}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default TechnicalAnalysisCard;