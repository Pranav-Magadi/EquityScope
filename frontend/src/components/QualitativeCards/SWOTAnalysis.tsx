import React from 'react';
import { motion } from 'framer-motion';
import { Shield, AlertTriangle, Target, Zap } from 'lucide-react';
import type { SWOTAnalysis, CompanyAnalysis } from '../../types';
import type { SummaryResponse } from '../../types/summary';

interface SWOTAnalysisProps {
  ticker: string;
  companyAnalysis: CompanyAnalysis | SummaryResponse;
}

export const SWOTAnalysisCard: React.FC<SWOTAnalysisProps> = ({ ticker, companyAnalysis }) => {
  // Type guard to check if we have V3 Summary data
  const isV3Summary = (data: any): data is SummaryResponse => {
    return data && 'analysis_mode' in data && 'fair_value_band' in data;
  };
  
  // Extract SWOT data based on format
  const swot: SWOTAnalysis = isV3Summary(companyAnalysis) ? {
    // For V3 Summary, we need to derive SWOT from other fields
    // This is a simplified approach - ideally the backend should provide structured SWOT
    strengths: [
      `Fair value range: ₹${companyAnalysis.fair_value_band.min_value.toFixed(0)}-₹${companyAnalysis.fair_value_band.max_value.toFixed(0)}`,
      companyAnalysis.business_fundamentals,
      ...companyAnalysis.key_factors.filter(f => f.toLowerCase().includes('strong') || f.toLowerCase().includes('good'))
    ].filter(Boolean).slice(0, 4),
    weaknesses: [
      ...companyAnalysis.data_health_warnings,
      ...companyAnalysis.key_factors.filter(f => f.toLowerCase().includes('weak') || f.toLowerCase().includes('concern') || f.toLowerCase().includes('risk'))
    ].filter(Boolean).slice(0, 4),
    opportunities: [
      companyAnalysis.market_signals,
      ...companyAnalysis.key_factors.filter(f => f.toLowerCase().includes('growth') || f.toLowerCase().includes('expansion') || f.toLowerCase().includes('opportunity'))
    ].filter(Boolean).slice(0, 4),
    threats: [
      ...companyAnalysis.key_factors.filter(f => f.toLowerCase().includes('threat') || f.toLowerCase().includes('challenge') || f.toLowerCase().includes('pressure'))
    ].filter(Boolean).slice(0, 4)
  } : (companyAnalysis as CompanyAnalysis).swot;
  const swotItems = [
    {
      title: 'Strengths',
      items: swot.strengths,
      icon: Shield,
      color: 'green',
      bgColor: 'bg-green-900/20',
      iconColor: 'text-green-400',
      borderColor: 'border-green-500/30'
    },
    {
      title: 'Weaknesses',
      items: swot.weaknesses,
      icon: AlertTriangle,
      color: 'red',
      bgColor: 'bg-red-900/20',
      iconColor: 'text-red-400',
      borderColor: 'border-red-500/30'
    },
    {
      title: 'Opportunities',
      items: swot.opportunities,
      icon: Target,
      color: 'blue',
      bgColor: 'bg-blue-900/20',
      iconColor: 'text-blue-400',
      borderColor: 'border-blue-500/30'
    },
    {
      title: 'Threats',
      items: swot.threats,
      icon: Zap,
      color: 'orange',
      bgColor: 'bg-orange-900/20',
      iconColor: 'text-orange-400',
      borderColor: 'border-orange-500/30'
    }
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.1 }}
      className="card"
    >
      <div className="card-header">
        <h2 className="text-xl font-semibold text-slate-100">Strategic SWOT Analysis</h2>
        <p className="text-sm text-slate-400 mt-1">
          {isV3Summary(companyAnalysis) 
            ? `${companyAnalysis.analysis_mode === 'simple' ? 'Rule-based' : 'AI-powered'} strategic assessment`
            : 'AI-powered strategic assessment of competitive positioning'
          }
        </p>
      </div>
      <div className="card-body">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {swotItems.map((category, index) => (
            <motion.div
              key={category.title}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3, delay: 0.1 + index * 0.05 }}
              className={`${category.bgColor} ${category.borderColor} border rounded-lg p-4`}
            >
              <div className="flex items-center space-x-2 mb-3">
                <category.icon className={`h-5 w-5 ${category.iconColor}`} />
                <h3 className="font-medium text-slate-100">{category.title}</h3>
              </div>
              <ul className="space-y-2">
                {category.items.map((item, itemIndex) => (
                  <motion.li
                    key={itemIndex}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3, delay: 0.2 + itemIndex * 0.05 }}
                    className="text-sm text-slate-300 flex items-start space-x-2"
                  >
                    <span className="w-1 h-1 bg-slate-400 rounded-full mt-2 flex-shrink-0" />
                    <span>{item}</span>
                  </motion.li>
                ))}
              </ul>
            </motion.div>
          ))}
        </div>
      </div>
    </motion.div>
  );
};