import React, { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { BookOpen, TrendingUp, Users, Lightbulb, X } from 'lucide-react';
import { ProgressiveDisclosure, ExperienceLevel } from '../common/ProgressiveDisclosure';
import { 
  DCF_10_YEAR_EDUCATIONAL_CONTENT, 
  DCF_COMPONENT_EXPLANATIONS,
  generateDynamicEducationalContent 
} from '../../data/dcfEducationalContent';
import type { MultiStageDCFResponse } from '../../types';

interface DCFEducationalPanelProps {
  dcfResponse?: MultiStageDCFResponse;
  userLevel: ExperienceLevel;
  focusArea?: 'basics' | 'growth_analysis' | 'mode_selection' | 'interpretation' | 'advanced';
  isVisible: boolean;
  onClose: () => void;
  className?: string;
}

interface TopicSelectorProps {
  activeTopics: string[];
  onTopicToggle: (topic: string) => void;
  availableTopics: Array<{ key: string; label: string; description: string; icon: React.ComponentType<{ className?: string }> }>;
}

const TopicSelector: React.FC<TopicSelectorProps> = ({
  activeTopics,
  onTopicToggle,
  availableTopics
}) => {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-6">
      {availableTopics.map(topic => {
        const Icon = topic.icon;
        const isActive = activeTopics.includes(topic.key);
        
        return (
          <motion.button
            key={topic.key}
            onClick={() => onTopicToggle(topic.key)}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className={`p-3 rounded-lg border text-left transition-all ${
              isActive
                ? 'border-primary-500 bg-primary-900/20 text-primary-300'
                : 'border-slate-600 bg-slate-800/30 text-slate-400 hover:border-slate-500 hover:text-slate-300'
            }`}
          >
            <div className="flex items-center space-x-2 mb-1">
              <Icon className="h-4 w-4" />
              <span className="font-medium text-sm">{topic.label}</span>
            </div>
            <p className="text-xs opacity-75">{topic.description}</p>
          </motion.button>
        );
      })}
    </div>
  );
};

export const DCFEducationalPanel: React.FC<DCFEducationalPanelProps> = ({
  dcfResponse,
  userLevel,
  focusArea = 'basics',
  isVisible,
  onClose,
  className = ""
}) => {
  const [activeTopics, setActiveTopics] = useState<string[]>([
    focusArea === 'basics' ? 'dcf_basics' : focusArea
  ]);

  const availableTopics = useMemo(() => [
    {
      key: 'dcf_basics',
      label: 'DCF Fundamentals',
      description: 'Core concepts and principles',
      icon: BookOpen
    },
    {
      key: 'multi_stage_growth',
      label: '10-Year Model',
      description: 'Multi-stage growth approach',
      icon: TrendingUp
    },
    {
      key: 'mode_selection',
      label: 'Analysis Modes',
      description: 'Simple vs Agentic modes',
      icon: Users
    },
    {
      key: 'growth_analysis',
      label: 'Growth Analysis',
      description: 'Historical trends and projections',
      icon: TrendingUp
    },
    {
      key: 'valuation_interpretation',
      label: 'Results Interpretation',
      description: 'Understanding your valuation',
      icon: Lightbulb
    },
    {
      key: 'common_pitfalls',
      label: 'Common Mistakes',
      description: 'Avoid typical DCF errors',
      icon: Lightbulb
    }
  ], []);

  const handleTopicToggle = (topic: string) => {
    setActiveTopics(prev =>
      prev.includes(topic)
        ? prev.filter(t => t !== topic)
        : [...prev, topic]
    );
  };

  // Generate combined educational content
  const combinedContent = useMemo(() => {
    let allContent: any[] = [];

    // Add static content from selected topics
    activeTopics.forEach(topic => {
      if (DCF_10_YEAR_EDUCATIONAL_CONTENT[topic]) {
        allContent = [...allContent, ...DCF_10_YEAR_EDUCATIONAL_CONTENT[topic]];
      }
    });

    // Add component-specific explanations if relevant
    if (activeTopics.includes('valuation_interpretation')) {
      if (DCF_COMPONENT_EXPLANATIONS['growth_waterfall']) {
        allContent = [...allContent, ...DCF_COMPONENT_EXPLANATIONS['growth_waterfall']];
      }
      if (DCF_COMPONENT_EXPLANATIONS['projection_charts']) {
        allContent = [...allContent, ...DCF_COMPONENT_EXPLANATIONS['projection_charts']];
      }
    }

    // Add dynamic content based on analysis results
    if (dcfResponse && activeTopics.includes('valuation_interpretation')) {
      const dynamicContent = generateDynamicEducationalContent(dcfResponse.valuation, userLevel);
      allContent = [...allContent, ...dynamicContent];
    }

    return allContent;
  }, [activeTopics, dcfResponse, userLevel]);

  if (!isVisible) return null;

  return (
    <motion.div
      initial={{ opacity: 0, x: 300 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 300 }}
      transition={{ duration: 0.3 }}
      className={`fixed right-0 top-0 h-full w-96 bg-slate-900 border-l border-slate-700 shadow-2xl z-50 overflow-hidden ${className}`}
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-slate-800 to-slate-900 p-4 border-b border-slate-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-primary-500/20 rounded-lg">
              <BookOpen className="h-5 w-5 text-primary-400" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-slate-100">
                DCF Learning Center
              </h2>
              <p className="text-sm text-slate-400">
                Interactive educational content
              </p>
            </div>
          </div>
          
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-200 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="h-full overflow-y-auto pb-20">
        <div className="p-4">
          {/* Experience Level Indicator */}
          <div className="mb-4 p-3 bg-slate-800/50 rounded-lg border border-slate-700">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-slate-300">
                Learning Level: {userLevel.charAt(0).toUpperCase() + userLevel.slice(1)}
              </span>
              <div className="text-xs text-slate-400">
                {userLevel === 'beginner' && '🎯 Building fundamentals'}
                {userLevel === 'intermediate' && '📈 Applying concepts'}
                {userLevel === 'advanced' && '🎓 Mastering techniques'}
              </div>
            </div>
          </div>

          {/* Topic Selector */}
          <div className="mb-6">
            <h3 className="text-sm font-medium text-slate-300 mb-3">
              Choose Learning Topics
            </h3>
            <TopicSelector
              activeTopics={activeTopics}
              onTopicToggle={handleTopicToggle}
              availableTopics={availableTopics}
            />
          </div>

          {/* Progressive Disclosure Content */}
          {activeTopics.length > 0 && combinedContent.length > 0 && (
            <ProgressiveDisclosure
              topic="10-Year DCF Analysis"
              userLevel={userLevel}
              contentItems={combinedContent}
            />
          )}

          {/* No Content State */}
          {activeTopics.length === 0 && (
            <div className="text-center py-8">
              <BookOpen className="h-12 w-12 text-slate-600 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-slate-300 mb-2">
                Select Learning Topics
              </h3>
              <p className="text-sm text-slate-400">
                Choose topics above to access educational content
              </p>
            </div>
          )}

          {/* Analysis-Specific Insights */}
          {dcfResponse && activeTopics.includes('valuation_interpretation') && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-6 p-4 bg-gradient-to-r from-blue-900/20 to-purple-900/20 border border-blue-500/30 rounded-lg"
            >
              <div className="flex items-center space-x-2 mb-3">
                <Lightbulb className="h-5 w-5 text-blue-400" />
                <h4 className="text-sm font-medium text-blue-300">
                  Analysis-Specific Insights
                </h4>
              </div>
              
              <div className="space-y-3 text-sm">
                <div>
                  <span className="font-medium text-slate-300">Mode Used:</span>
                  <span className="ml-2 text-slate-400 capitalize">
                    {dcfResponse.mode} Mode
                  </span>
                </div>
                
                <div>
                  <span className="font-medium text-slate-300">Key Benefit:</span>
                  <span className="ml-2 text-slate-400">
                    {dcfResponse.education_content.key_benefits}
                  </span>
                </div>
                
                <div>
                  <span className="font-medium text-slate-300">Best For:</span>
                  <span className="ml-2 text-slate-400">
                    {dcfResponse.education_content.best_for}
                  </span>
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </motion.div>
  );
};