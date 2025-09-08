import React from 'react';
import { motion } from 'framer-motion';
import { 
  Shield, 
  TrendingUp, 
  TrendingDown, 
  Minus, 
  Building2, 
  Cpu, 
  Settings, 
  Award,
  ExternalLink,
  Target
} from 'lucide-react';

import { CompetitiveAnalysis, CompetitivePeer } from '../../types';

interface CompetitiveAnalysisProps {
  data: CompetitiveAnalysis;
  companyName: string;
  ticker: string;
}

export const CompetitiveAnalysisCard: React.FC<CompetitiveAnalysisProps> = ({
  data,
  companyName,
  ticker
}) => {
  const getScoreIcon = (score: 'stronger' | 'similar' | 'weaker') => {
    switch (score) {
      case 'stronger':
        return <TrendingUp className="h-4 w-4 text-green-400" />;
      case 'weaker':
        return <TrendingDown className="h-4 w-4 text-red-400" />;
      default:
        return <Minus className="h-4 w-4 text-yellow-400" />;
    }
  };

  const getScoreColor = (score: 'stronger' | 'similar' | 'weaker') => {
    switch (score) {
      case 'stronger':
        return 'text-green-400 bg-green-900/20 border-green-500/30';
      case 'weaker':
        return 'text-red-400 bg-red-900/20 border-red-500/30';
      default:
        return 'text-yellow-400 bg-yellow-900/20 border-yellow-500/30';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'financial':
        return <TrendingUp className="h-5 w-5 text-blue-400" />;
      case 'technological':
        return <Cpu className="h-5 w-5 text-purple-400" />;
      case 'operational':
        return <Settings className="h-5 w-5 text-orange-400" />;
      case 'governance':
        return <Shield className="h-5 w-5 text-emerald-400" />;
      default:
        return <Building2 className="h-5 w-5 text-slate-400" />;
    }
  };

  const handleSourceClick = (url: string) => {
    if (url && url !== '#') {
      window.open(url, '_blank', 'noopener,noreferrer');
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.3 }}
      className="bg-slate-800/50 rounded-lg border border-slate-700/50 overflow-hidden"
    >
      <div className="p-6">
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-2 bg-indigo-600 rounded-lg">
            <Target className="h-6 w-6 text-white" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-slate-100">Competitive Analysis</h3>
            <p className="text-sm text-slate-400">{companyName} vs Industry Peers</p>
          </div>
        </div>

        {/* Competitive Positioning */}
        <div className="mb-6 p-4 bg-slate-900/50 rounded-lg">
          <h4 className="text-lg font-semibold text-slate-100 mb-2">Market Positioning</h4>
          <p className="text-slate-300 text-sm leading-relaxed">
            {data.competitive_positioning}
          </p>
        </div>

        {/* Peer Comparison */}
        <div className="space-y-6">
          {data.peers.map((peer: CompetitivePeer, index: number) => (
            <motion.div
              key={peer.ticker}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.1 * index }}
              className="border border-slate-600/30 rounded-lg p-4 bg-slate-900/30"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <Building2 className="h-5 w-5 text-slate-400" />
                  <div>
                    <h5 className="font-semibold text-slate-100">{peer.name}</h5>
                    <span className="text-xs text-slate-400 font-mono">{peer.ticker}</span>
                  </div>
                </div>
              </div>

              {/* Comparison Categories */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(peer.comparison).map(([category, data]: [string, any]) => (
                  <div key={category} className="space-y-2">
                    <div className="flex items-center space-x-2">
                      {getCategoryIcon(category)}
                      <span className="text-sm font-medium text-slate-200 capitalize">
                        {category === 'technological' ? 'Technology' : category}
                      </span>
                      {getScoreIcon(data.score)}
                    </div>
                    
                    <div className={`p-3 rounded-lg border text-xs ${getScoreColor(data.score)}`}>
                      <p className="leading-relaxed">{data.details}</p>
                      
                      {data.sources && data.sources.length > 0 && (
                        <div className="mt-2 pt-2 border-t border-current/20">
                          <div className="flex flex-wrap gap-1">
                            {data.sources.map((source: string, sourceIndex: number) => (
                              <button
                                key={sourceIndex}
                                onClick={() => handleSourceClick(source)}
                                className="inline-flex items-center space-x-1 px-2 py-1 bg-current/10 hover:bg-current/20 rounded text-xs transition-colors"
                              >
                                <ExternalLink className="h-3 w-3" />
                                <span>Source {sourceIndex + 1}</span>
                              </button>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          ))}
        </div>

        {/* Competitive Advantages & Threats */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Competitive Advantages */}
          <div className="bg-green-900/10 border border-green-500/20 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-3">
              <Award className="h-5 w-5 text-green-400" />
              <h4 className="font-semibold text-green-300">Key Advantages</h4>
            </div>
            <ul className="space-y-2">
              {data.key_competitive_advantages.map((advantage: string, index: number) => (
                <li key={index} className="flex items-start space-x-2 text-sm text-green-200">
                  <div className="w-1.5 h-1.5 bg-green-400 rounded-full mt-2 flex-shrink-0"></div>
                  <span>{advantage}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Competitive Threats */}
          <div className="bg-red-900/10 border border-red-500/20 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-3">
              <Shield className="h-5 w-5 text-red-400" />
              <h4 className="font-semibold text-red-300">Competitive Threats</h4>
            </div>
            <ul className="space-y-2">
              {data.competitive_threats.map((threat: string, index: number) => (
                <li key={index} className="flex items-start space-x-2 text-sm text-red-200">
                  <div className="w-1.5 h-1.5 bg-red-400 rounded-full mt-2 flex-shrink-0"></div>
                  <span>{threat}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default CompetitiveAnalysisCard;