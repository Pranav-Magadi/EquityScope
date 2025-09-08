import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Info, BookOpen, HelpCircle, Lightbulb } from 'lucide-react';
import type { ExperienceLevel } from './ProgressiveDisclosure';

interface EducationalTooltipProps {
  content: {
    beginner?: string;
    intermediate?: string;
    advanced?: string;
  };
  userLevel: ExperienceLevel;
  title?: string;
  type?: 'concept' | 'calculation' | 'interpretation' | 'warning';
  className?: string;
  placement?: 'top' | 'bottom' | 'left' | 'right';
}

const getTooltipIcon = (type: string) => {
  switch (type) {
    case 'concept': return BookOpen;
    case 'calculation': return HelpCircle;
    case 'interpretation': return Lightbulb;
    case 'warning': return Info;
    default: return Info;
  }
};

const getTooltipColor = (type: string) => {
  switch (type) {
    case 'concept': return 'border-blue-500/30 bg-blue-900/20';
    case 'calculation': return 'border-green-500/30 bg-green-900/20';
    case 'interpretation': return 'border-purple-500/30 bg-purple-900/20';
    case 'warning': return 'border-yellow-500/30 bg-yellow-900/20';
    default: return 'border-slate-500/30 bg-slate-900/20';
  }
};

const getPlacementClasses = (placement: string) => {
  switch (placement) {
    case 'top':
      return {
        tooltip: 'bottom-full left-1/2 transform -translate-x-1/2 mb-2',
        arrow: 'top-full left-1/2 transform -translate-x-1/2 border-t border-l'
      };
    case 'bottom':
      return {
        tooltip: 'top-full left-1/2 transform -translate-x-1/2 mt-2',
        arrow: 'bottom-full left-1/2 transform -translate-x-1/2 border-b border-r'
      };
    case 'left':
      return {
        tooltip: 'right-full top-1/2 transform -translate-y-1/2 mr-2',
        arrow: 'left-full top-1/2 transform -translate-y-1/2 border-l border-t'
      };
    case 'right':
      return {
        tooltip: 'left-full top-1/2 transform -translate-y-1/2 ml-2',
        arrow: 'right-full top-1/2 transform -translate-y-1/2 border-r border-b'
      };
    default:
      return {
        tooltip: 'bottom-full left-1/2 transform -translate-x-1/2 mb-2',
        arrow: 'top-full left-1/2 transform -translate-x-1/2 border-t border-l'
      };
  }
};

export const EducationalTooltip: React.FC<EducationalTooltipProps> = ({
  content,
  userLevel,
  title,
  type = 'concept',
  className = '',
  placement = 'top'
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  const Icon = getTooltipIcon(type);
  const colorClasses = getTooltipColor(type);
  const placementClasses = getPlacementClasses(placement);

  // Get content based on user level with fallbacks
  const getRelevantContent = () => {
    return content[userLevel] || 
           content.intermediate || 
           content.beginner || 
           content.advanced || 
           'Educational content not available.';
  };

  // Check if there's content for other levels
  const hasMultipleLevels = Object.keys(content).length > 1;
  const availableLevels = Object.keys(content) as ExperienceLevel[];

  const relevantContent = getRelevantContent();

  return (
    <div className={`relative inline-block ${className}`}>
      <button
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => {
          setIsVisible(false);
          setIsExpanded(false);
        }}
        onClick={() => setIsExpanded(!isExpanded)}
        className="text-slate-400 hover:text-slate-300 transition-colors cursor-help"
      >
        <Icon className="h-3 w-3" />
      </button>

      <AnimatePresence>
        {(isVisible || isExpanded) && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className={`absolute ${placementClasses.tooltip} w-80 max-w-sm z-50`}
          >
            <div className={`border rounded-lg p-4 shadow-lg ${colorClasses} backdrop-blur-sm`}>
              {/* Header */}
              {title && (
                <div className="flex items-center space-x-2 mb-2">
                  <Icon className="h-4 w-4 text-slate-300" />
                  <h4 className="text-sm font-medium text-slate-200">{title}</h4>
                </div>
              )}

              {/* Level Indicator */}
              <div className="flex items-center space-x-2 mb-3">
                <div className="text-xs text-slate-400">
                  {userLevel.charAt(0).toUpperCase() + userLevel.slice(1)} Level
                </div>
                {hasMultipleLevels && (
                  <div className="flex items-center space-x-1">
                    {availableLevels.map(level => (
                      <div
                        key={level}
                        className={`w-2 h-2 rounded-full ${
                          level === userLevel 
                            ? 'bg-primary-400' 
                            : 'bg-slate-600'
                        }`}
                        title={`${level} content available`}
                      />
                    ))}
                  </div>
                )}
              </div>

              {/* Content */}
              <div className="text-sm text-slate-300 leading-relaxed">
                {relevantContent}
              </div>

              {/* Multiple Levels Toggle */}
              {hasMultipleLevels && isExpanded && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className="mt-4 pt-3 border-t border-white/10"
                >
                  <div className="text-xs font-medium text-slate-400 mb-2">
                    Other Levels:
                  </div>
                  {availableLevels
                    .filter(level => level !== userLevel)
                    .map(level => (
                      <div key={level} className="mb-2">
                        <div className="text-xs font-medium text-slate-400 mb-1 capitalize">
                          {level}:
                        </div>
                        <div className="text-xs text-slate-400 opacity-75">
                          {content[level]}
                        </div>
                      </div>
                    ))}
                </motion.div>
              )}

              {/* Expand Hint */}
              {hasMultipleLevels && !isExpanded && (
                <div className="mt-3 pt-2 border-t border-white/10">
                  <div className="text-xs text-slate-500">
                    Click to see content for other experience levels
                  </div>
                </div>
              )}
            </div>

            {/* Arrow */}
            <div
              className={`absolute w-2 h-2 ${colorClasses.split(' ')[0]} transform rotate-45 ${placementClasses.arrow}`}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};