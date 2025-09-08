import React from 'react';
import { motion } from 'framer-motion';
import { TrendingDown, Info, BarChart3 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { InfoTooltip } from '../common/InfoTooltip';
import { EducationalTooltip } from '../common/EducationalTooltip';
import type { GrowthStage, DCFMode } from '../../types';

interface GrowthWaterfallChartProps {
  growthStages: GrowthStage[];
  growthWaterfall: Record<string, number>;
  mode: DCFMode;
  userLevel?: 'beginner' | 'intermediate' | 'advanced';
  educationContent?: {
    mode_explanation: string;
    growth_methodology: string;
  };
}

interface WaterfallDataPoint {
  stage: string;
  growthRate: number;
  method: string;
  confidence: 'high' | 'medium' | 'low';
  gdpWeight: number;
  rationale: string;
}

const confidenceColors = {
  high: '#10b981',    // green-500
  medium: '#f59e0b',  // amber-500
  low: '#ef4444'      // red-500
};

const getStageColor = (confidence: 'high' | 'medium' | 'low', index: number) => {
  const baseColor = confidenceColors[confidence];
  const opacity = 1 - (index * 0.1); // Gradually fade for later stages
  return baseColor + Math.round(opacity * 255).toString(16).padStart(2, '0');
};

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload as WaterfallDataPoint;
    return (
      <div className="bg-slate-900 border border-slate-700 rounded-lg p-3 shadow-lg">
        <p className="text-slate-100 font-medium mb-1">{label}</p>
        <p className="text-primary-400 font-bold text-lg mb-2">
          {data.growthRate.toFixed(1)}%
        </p>
        <div className="space-y-1 text-sm">
          <p className="text-slate-300">
            <span className="text-slate-400">Method:</span> {data.method}
          </p>
          <p className="text-slate-300">
            <span className="text-slate-400">GDP Weight:</span> {(data.gdpWeight * 100).toFixed(0)}%
          </p>
          <p className={`font-medium ${
            data.confidence === 'high' ? 'text-green-400' :
            data.confidence === 'medium' ? 'text-yellow-400' : 'text-red-400'
          }`}>
            {data.confidence.toUpperCase()} Confidence
          </p>
        </div>
        <p className="text-xs text-slate-400 mt-2 max-w-64">
          {data.rationale}
        </p>
      </div>
    );
  }
  return null;
};

export const GrowthWaterfallChart: React.FC<GrowthWaterfallChartProps> = ({
  growthStages,
  growthWaterfall,
  mode,
  userLevel = 'intermediate',
  educationContent
}) => {
  // Prepare data for the waterfall chart
  const waterfallData: WaterfallDataPoint[] = growthStages.map((stage, index) => ({
    stage: `Years ${stage.years}`,
    growthRate: stage.growth_rate,
    method: stage.method.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
    confidence: stage.confidence,
    gdpWeight: stage.gdp_weight,
    rationale: stage.rationale
  }));

  // Add terminal value
  if (growthWaterfall.terminal) {
    waterfallData.push({
      stage: 'Terminal',
      growthRate: growthWaterfall.terminal,
      method: 'Long-term GDP Growth',
      confidence: 'high' as const,
      gdpWeight: 1.0,
      rationale: 'Long-term sustainable growth rate aligned with GDP growth'
    });
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="bg-slate-800/50 rounded-lg p-6"
    >
      {/* Header */}
      <div className="flex items-center space-x-3 mb-6">
        <BarChart3 className="h-6 w-6 text-primary-400" />
        <h3 className="text-lg font-semibold text-slate-100">
          10-Year Growth Stage Waterfall
        </h3>
        <EducationalTooltip
          userLevel={userLevel}
          type="concept"
          title="Growth Waterfall Chart"
          content={{
            beginner: "This chart shows how growth rates slow down over time. Companies can't grow fast forever - competition increases and markets mature. Each bar shows expected growth for different time periods.",
            intermediate: "The waterfall visualizes multi-stage growth decline over 10 years. Early stages use historical data, later stages blend with GDP growth (3%) as competitive advantages fade and the company reaches maturity.",
            advanced: "Multi-stage growth modeling with GDP blending coefficients. Stage 1-2: 80% historical/20% GDP. Stage 3-5: 50%/50%. Stage 6-8: 25%/75%. Stage 9-10: 0%/100%. This captures competitive dynamics and mean reversion."
          }}
        />
      </div>

      {/* Mode Badge */}
      <div className="flex items-center space-x-2 mb-4">
        <div className={`px-3 py-1 rounded-full text-xs font-medium ${
          mode === 'simple' 
            ? 'bg-green-500/20 text-green-400 border border-green-500/30'
            : 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
        }`}>
          {mode.toUpperCase()} MODE
        </div>
        <span className="text-sm text-slate-400">
          {mode === 'simple' ? 'Conservative Historical Analysis' : 'AI-Enhanced Projections'}
        </span>
      </div>

      {/* Waterfall Chart */}
      <div className="h-80 mb-6">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={waterfallData}
            margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis 
              dataKey="stage" 
              stroke="#9ca3af"
              fontSize={12}
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis 
              stroke="#9ca3af"
              fontSize={12}
              tickFormatter={(value) => `${value}%`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar 
              dataKey="growthRate" 
              radius={[4, 4, 0, 0]}
            >
              {waterfallData.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={getStageColor(entry.confidence, index)}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Growth Stages Summary */}
      <div className="space-y-3">
        <h4 className="text-md font-medium text-slate-300 flex items-center space-x-2">
          <TrendingDown className="h-4 w-4 text-slate-400" />
          <span>Growth Stage Breakdown</span>
        </h4>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          {waterfallData.map((stage, index) => (
            <motion.div
              key={stage.stage}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              className="bg-slate-700/30 rounded-lg p-3 border border-slate-600/50"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-slate-200">{stage.stage}</span>
                <div 
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: getStageColor(stage.confidence, index) }}
                />
              </div>
              
              <div className="space-y-1">
                <div className="text-lg font-bold text-primary-400">
                  {stage.growthRate.toFixed(1)}%
                </div>
                <div className="text-xs text-slate-400">
                  GDP Weight: {(stage.gdpWeight * 100).toFixed(0)}%
                </div>
                <div className={`text-xs font-medium ${
                  stage.confidence === 'high' ? 'text-green-400' :
                  stage.confidence === 'medium' ? 'text-yellow-400' : 'text-red-400'
                }`}>
                  {stage.confidence.toUpperCase()}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Educational Content */}
      {educationContent && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mt-6 pt-4 border-t border-slate-700"
        >
          <div className="space-y-3">
            <div>
              <h5 className="text-sm font-medium text-slate-300 mb-1">Mode Explanation</h5>
              <p className="text-xs text-slate-400">{educationContent.mode_explanation}</p>
            </div>
            <div>
              <h5 className="text-sm font-medium text-slate-300 mb-1">Growth Methodology</h5>
              <p className="text-xs text-slate-400">{educationContent.growth_methodology}</p>
            </div>
          </div>
        </motion.div>
      )}

      {/* Legend */}
      <div className="mt-4 pt-4 border-t border-slate-700">
        <div className="flex items-center space-x-6 text-xs">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-green-500" />
            <span className="text-slate-400">High Confidence</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-yellow-500" />
            <span className="text-slate-400">Medium Confidence</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-red-500" />
            <span className="text-slate-400">Low Confidence</span>
          </div>
          <div className="flex items-center space-x-2">
            <Info className="h-3 w-3 text-slate-500" />
            <span className="text-slate-500">Color fades as maturity increases</span>
          </div>
        </div>
      </div>
    </motion.div>
  );
};