import React from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, Info, AlertCircle, Clock } from 'lucide-react';

interface DataHealthWarningsProps {
  warnings: string[];
}

export const DataHealthWarnings: React.FC<DataHealthWarningsProps> = ({ warnings }) => {
  if (warnings.length === 0) return null;

  const getWarningType = (warning: string) => {
    const lowerWarning = warning.toLowerCase();
    
    if (lowerWarning.includes('cached') || lowerWarning.includes('outdated')) {
      return {
        icon: Clock,
        color: 'border-yellow-500/30 bg-yellow-900/10 text-yellow-300',
        iconColor: 'text-yellow-400'
      };
    } else if (lowerWarning.includes('unavailable') || lowerWarning.includes('missing')) {
      return {
        icon: Info,
        color: 'border-blue-500/30 bg-blue-900/10 text-blue-300',
        iconColor: 'text-blue-400'
      };
    } else if (lowerWarning.includes('fallback') || lowerWarning.includes('reduced')) {
      return {
        icon: AlertCircle,
        color: 'border-orange-500/30 bg-orange-900/10 text-orange-300',
        iconColor: 'text-orange-400'
      };
    } else {
      return {
        icon: AlertTriangle,
        color: 'border-red-500/30 bg-red-900/10 text-red-300',
        iconColor: 'text-red-400'
      };
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="bg-slate-800 border border-slate-700 rounded-lg p-4"
    >
      <div className="flex items-center space-x-2 mb-3">
        <AlertTriangle className="h-4 w-4 text-slate-400" />
        <h4 className="text-sm font-medium text-slate-300">Data Health Status</h4>
      </div>

      <div className="space-y-2">
        {warnings.map((warning, index) => {
          const warningType = getWarningType(warning);
          const Icon = warningType.icon;

          return (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.2, delay: index * 0.1 }}
              className={`flex items-start space-x-2 p-2 rounded border ${warningType.color}`}
            >
              <Icon className={`h-4 w-4 flex-shrink-0 mt-0.5 ${warningType.iconColor}`} />
              <div className="text-xs leading-relaxed">{warning}</div>
            </motion.div>
          );
        })}
      </div>

      <div className="mt-3 text-xs text-slate-500">
        These warnings indicate data limitations that may affect analysis accuracy.
      </div>
    </motion.div>
  );
};