import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, DollarSign, BarChart3, Users, Target, Info } from 'lucide-react';

interface WeightedScoreDisplayProps {
  totalScore: number;
  componentScores: {
    dcf_score: number;
    financial_score: number;
    technical_score: number;
    peer_score: number;
  };
  investmentLabel: string;
  confidence: number;
}

export const WeightedScoreDisplay: React.FC<WeightedScoreDisplayProps> = ({
  totalScore,
  componentScores,
  investmentLabel,
  confidence
}) => {
  const getScoreColor = (score: number) => {
    if (score >= 20) return 'text-green-400';
    if (score >= 10) return 'text-green-300';
    if (score >= -10) return 'text-yellow-400';
    if (score >= -20) return 'text-orange-400';
    return 'text-red-400';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 20) return 'bg-green-500/20';
    if (score >= 10) return 'bg-green-500/10';
    if (score >= -10) return 'bg-yellow-500/10';
    if (score >= -20) return 'bg-orange-500/10';
    return 'bg-red-500/20';
  };

  const getProgressWidth = (score: number) => {
    // Convert score from -100 to +100 scale to 0-100% for progress bar
    return Math.max(0, Math.min(100, (score + 100) / 2));
  };

  const components = [
    {
      name: 'DCF Valuation',
      icon: DollarSign,
      score: componentScores.dcf_score,
      weight: '35%',
      description: 'Sector-specific discounted cash flow analysis'
    },
    {
      name: 'Financial Health',
      icon: BarChart3,
      score: componentScores.financial_score,
      weight: '25%',
      description: 'Profitability and efficiency metrics'
    },
    {
      name: 'Technical Signals',
      icon: TrendingUp,
      score: componentScores.technical_score,
      weight: '20%',
      description: 'Price momentum and market indicators'
    },
    {
      name: 'Peer Comparison',
      icon: Users,
      score: componentScores.peer_score,
      weight: '20%',
      description: 'Relative valuation vs sector peers'
    }
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-slate-800 border border-slate-700 rounded-lg p-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg">
            <Target className="h-5 w-5 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-slate-100">
              Weighted Score Analysis
            </h3>
            <p className="text-sm text-slate-400">
              v3 Multi-component scoring framework
            </p>
          </div>
        </div>
        
        <div className="text-right">
          <div className={`text-3xl font-bold ${getScoreColor(totalScore)}`}>
            {totalScore > 0 ? '+' : ''}{totalScore.toFixed(1)}
          </div>
          <div className="text-sm text-slate-400">Total Score</div>
        </div>
      </div>

      {/* Overall Score Bar */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-slate-300">Overall Assessment</span>
          <div className="flex items-center space-x-2">
            <span className={`text-sm font-medium ${getScoreColor(totalScore)}`}>
              {investmentLabel}
            </span>
            <span className="text-xs text-slate-500">
              ({confidence >= 0.7 ? 'High' : confidence >= 0.5 ? 'Medium' : 'Low'} Confidence)
            </span>
          </div>
        </div>
        
        <div className="relative h-3 bg-slate-700 rounded-full overflow-hidden">
          {/* Background gradient */}
          <div className="absolute inset-0 bg-gradient-to-r from-red-500/30 via-yellow-500/30 to-green-500/30"></div>
          
          {/* Score indicator */}
          <motion.div
            className="absolute top-0 h-full bg-white/30 backdrop-blur-sm border-r-2 border-white"
            style={{ left: `${getProgressWidth(totalScore)}%`, width: '2px' }}
            initial={{ left: '50%' }}
            animate={{ left: `${getProgressWidth(totalScore)}%` }}
            transition={{ duration: 1, ease: "easeOut" }}
          />
        </div>
        
        <div className="flex justify-between text-xs text-slate-500 mt-1">
          <span>Bearish (-100)</span>
          <span>Neutral (0)</span>
          <span>Bullish (+100)</span>
        </div>
      </div>

      {/* Component Breakdown */}
      <div className="space-y-4">
        <div className="flex items-center space-x-2 mb-3">
          <Info className="h-4 w-4 text-slate-400" />
          <span className="text-sm text-slate-400">Component Breakdown</span>
        </div>
        
        {components.map((component, index) => {
          const IconComponent = component.icon;
          
          return (
            <motion.div
              key={component.name}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="flex items-center space-x-4 p-3 bg-slate-900/50 rounded-lg"
            >
              {/* Icon */}
              <div className={`p-2 rounded-lg ${getScoreBgColor(component.score)}`}>
                <IconComponent className={`h-4 w-4 ${getScoreColor(component.score)}`} />
              </div>
              
              {/* Component Info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-slate-200">
                    {component.name}
                  </span>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-slate-500 font-mono">
                      {component.weight}
                    </span>
                    <span className={`text-sm font-semibold ${getScoreColor(component.score)}`}>
                      {component.score > 0 ? '+' : ''}{component.score.toFixed(1)}
                    </span>
                  </div>
                </div>
                <p className="text-xs text-slate-400 truncate">
                  {component.description}
                </p>
                
                {/* Mini progress bar */}
                <div className="mt-2 h-1 bg-slate-700 rounded-full overflow-hidden">
                  <motion.div
                    className={`h-full transition-all duration-500 ${
                      component.score >= 0 ? 'bg-green-500' : 'bg-red-500'
                    }`}
                    style={{ 
                      width: `${Math.abs(component.score)}%`,
                      maxWidth: '100%'
                    }}
                    initial={{ width: 0 }}
                    animate={{ width: `${Math.min(Math.abs(component.score), 100)}%` }}
                    transition={{ delay: index * 0.2, duration: 0.8 }}
                  />
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Methodology Note */}
      <div className="mt-6 p-3 bg-slate-900/30 rounded-lg border border-slate-700/50">
        <div className="flex items-start space-x-2">
          <Info className="h-4 w-4 text-blue-400 mt-0.5 flex-shrink-0" />
          <div className="text-xs text-slate-400 leading-relaxed">
            <span className="font-medium text-slate-300">Methodology:</span>
            {' '}Weighted scoring combines DCF valuation (35%), financial health (25%), 
            technical analysis (20%), and peer comparison (20%) to generate investment labels 
            from Strongly Bearish (-60+) to Strongly Bullish (+60+).
          </div>
        </div>
      </div>
    </motion.div>
  );
};