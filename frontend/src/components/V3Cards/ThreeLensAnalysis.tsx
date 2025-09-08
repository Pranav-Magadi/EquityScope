import React from 'react';
import { motion } from 'framer-motion';
import { Calculator, TrendingUp, Building, BarChart3, Activity, Users } from 'lucide-react';
import type { SummaryResponse } from '../../types/summary';

interface ThreeLensAnalysisProps {
  summaryData: SummaryResponse;
}

export const ThreeLensAnalysis: React.FC<ThreeLensAnalysisProps> = ({ summaryData }) => {
  const { valuation_insights, market_signals, business_fundamentals } = summaryData;

  const cards = [
    {
      title: "Valuation Insights",
      content: valuation_insights,
      icon: Calculator,
      color: "blue",
      bgColor: "bg-blue-900/20",
      borderColor: "border-blue-500/30",
      iconColor: "text-blue-400"
    },
    {
      title: "Market Signals", 
      content: market_signals,
      icon: TrendingUp,
      color: "green",
      bgColor: "bg-green-900/20",
      borderColor: "border-green-500/30",
      iconColor: "text-green-400"
    },
    {
      title: "Business Fundamentals",
      content: business_fundamentals,
      icon: Building,
      color: "purple",
      bgColor: "bg-purple-900/20", 
      borderColor: "border-purple-500/30",
      iconColor: "text-purple-400"
    }
  ];

  return (
    <div className="space-y-6">
      {cards.map((card, index) => (
        <motion.div
          key={card.title}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
          className={`${card.bgColor} border ${card.borderColor} rounded-xl p-6`}
        >
          {/* Card Header */}
          <div className="flex items-center space-x-3 mb-4">
            <div className={`p-2 bg-slate-800 rounded-lg`}>
              <card.icon className={`h-5 w-5 ${card.iconColor}`} />
            </div>
            <h3 className="text-lg font-semibold text-slate-100">{card.title}</h3>
          </div>

          {/* Content */}
          <div className="text-slate-300 text-sm leading-relaxed">
            {card.content}
          </div>

          {/* Visual Indicator */}
          <div className="mt-4 pt-4 border-t border-slate-700">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>Analysis Lens</span>
              <div className="flex items-center space-x-1">
                {card.title === "Valuation Insights" && <BarChart3 className="h-3 w-3" />}
                {card.title === "Market Signals" && <Activity className="h-3 w-3" />}
                {card.title === "Business Fundamentals" && <Users className="h-3 w-3" />}
                <span className="capitalize">{card.color}</span>
              </div>
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  );
};