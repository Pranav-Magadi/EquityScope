import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ChevronDown, 
  ChevronRight, 
  BookOpen, 
  GraduationCap, 
  TrendingUp,
  Info,
  Lightbulb,
  Target,
  AlertTriangle,
  CheckCircle
} from 'lucide-react';

export type ExperienceLevel = 'beginner' | 'intermediate' | 'advanced';
export type ContentType = 'concept' | 'methodology' | 'interpretation' | 'warning' | 'tip';

interface EducationalContentItem {
  id: string;
  type: ContentType;
  title: string;
  content: string;
  levels: ExperienceLevel[];
  priority: 'high' | 'medium' | 'low';
  relatedConcepts?: string[];
}

interface ProgressiveDisclosureProps {
  topic: string;
  userLevel: ExperienceLevel;
  contentItems: EducationalContentItem[];
  className?: string;
}

interface ExpandableContentProps {
  item: EducationalContentItem;
  isExpanded: boolean;
  onToggle: () => void;
  userLevel: ExperienceLevel;
}

const getContentIcon = (type: ContentType) => {
  switch (type) {
    case 'concept': return BookOpen;
    case 'methodology': return Target;
    case 'interpretation': return TrendingUp;
    case 'warning': return AlertTriangle;
    case 'tip': return Lightbulb;
    default: return Info;
  }
};

const getContentColor = (type: ContentType) => {
  switch (type) {
    case 'concept': return 'text-blue-400 bg-blue-500/20 border-blue-500/30';
    case 'methodology': return 'text-green-400 bg-green-500/20 border-green-500/30';
    case 'interpretation': return 'text-purple-400 bg-purple-500/20 border-purple-500/30';
    case 'warning': return 'text-yellow-400 bg-yellow-500/20 border-yellow-500/30';
    case 'tip': return 'text-amber-400 bg-amber-500/20 border-amber-500/30';
    default: return 'text-slate-400 bg-slate-500/20 border-slate-500/30';
  }
};

const getLevelIcon = (level: ExperienceLevel) => {
  switch (level) {
    case 'beginner': return '🎯';
    case 'intermediate': return '📈';
    case 'advanced': return '🎓';
  }
};

const ExpandableContent: React.FC<ExpandableContentProps> = ({
  item,
  isExpanded,
  onToggle,
  userLevel
}) => {
  const Icon = getContentIcon(item.type);
  const colorClasses = getContentColor(item.type);
  const isRelevantForUser = item.levels.includes(userLevel);
  const shouldAutoExpand = item.priority === 'high' && isRelevantForUser;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`border rounded-lg overflow-hidden ${colorClasses} ${
        isRelevantForUser ? 'opacity-100' : 'opacity-75'
      }`}
    >
      {/* Header */}
      <button
        onClick={onToggle}
        className="w-full p-4 flex items-center justify-between hover:bg-white/5 transition-colors"
      >
        <div className="flex items-center space-x-3">
          <Icon className="h-5 w-5 flex-shrink-0" />
          <div className="text-left">
            <h4 className="font-medium text-slate-100">{item.title}</h4>
            <div className="flex items-center space-x-2 mt-1">
              <div className="flex items-center space-x-1">
                {item.levels.map(level => (
                  <span key={level} className="text-xs" title={`${level} level`}>
                    {getLevelIcon(level)}
                  </span>
                ))}
              </div>
              {item.priority === 'high' && (
                <div className="px-2 py-0.5 bg-white/10 rounded text-xs font-medium">
                  Essential
                </div>
              )}
              {isRelevantForUser && (
                <CheckCircle className="h-3 w-3 text-green-400" />
              )}
            </div>
          </div>
        </div>
        
        <motion.div
          animate={{ rotate: isExpanded ? 90 : 0 }}
          transition={{ duration: 0.2 }}
        >
          <ChevronRight className="h-4 w-4" />
        </motion.div>
      </button>

      {/* Content */}
      <AnimatePresence>
        {(isExpanded || shouldAutoExpand) && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            <div className="px-4 pb-4 border-t border-white/10">
              <div className="mt-3 text-sm text-slate-300 leading-relaxed">
                {item.content}
              </div>
              
              {item.relatedConcepts && item.relatedConcepts.length > 0 && (
                <div className="mt-4 pt-3 border-t border-white/10">
                  <h5 className="text-xs font-medium text-slate-400 mb-2">Related Concepts:</h5>
                  <div className="flex flex-wrap gap-2">
                    {item.relatedConcepts.map(concept => (
                      <span
                        key={concept}
                        className="px-2 py-1 bg-white/10 rounded text-xs text-slate-300"
                      >
                        {concept}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export const ProgressiveDisclosure: React.FC<ProgressiveDisclosureProps> = ({
  topic,
  userLevel,
  contentItems,
  className = ""
}) => {
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());
  const [showAllLevels, setShowAllLevels] = useState(false);

  const toggleExpanded = (itemId: string) => {
    const newExpanded = new Set(expandedItems);
    if (newExpanded.has(itemId)) {
      newExpanded.delete(itemId);
    } else {
      newExpanded.add(itemId);
    }
    setExpandedItems(newExpanded);
  };

  const expandAll = () => {
    const allIds = contentItems.map(item => item.id);
    setExpandedItems(new Set(allIds));
  };

  const collapseAll = () => {
    setExpandedItems(new Set());
  };

  // Filter and sort content based on user level and preferences
  const filteredContent = contentItems
    .filter(item => showAllLevels || item.levels.includes(userLevel))
    .sort((a, b) => {
      // Sort by priority first, then by relevance to user level
      const priorityOrder = { high: 0, medium: 1, low: 2 };
      const aPriorityScore = priorityOrder[a.priority];
      const bPriorityScore = priorityOrder[b.priority];
      
      if (aPriorityScore !== bPriorityScore) {
        return aPriorityScore - bPriorityScore;
      }
      
      const aRelevant = a.levels.includes(userLevel) ? 0 : 1;
      const bRelevant = b.levels.includes(userLevel) ? 0 : 1;
      
      return aRelevant - bRelevant;
    });

  const relevantCount = contentItems.filter(item => item.levels.includes(userLevel)).length;
  const totalCount = contentItems.length;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`space-y-4 ${className}`}
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <GraduationCap className="h-6 w-6 text-primary-400" />
          <div>
            <h3 className="text-lg font-semibold text-slate-100">{topic}</h3>
            <p className="text-sm text-slate-400">
              {getLevelIcon(userLevel)} {userLevel} level • {relevantCount} of {totalCount} concepts
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowAllLevels(!showAllLevels)}
            className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
              showAllLevels
                ? 'bg-primary-500 text-white'
                : 'bg-slate-700 text-slate-400 hover:text-slate-300'
            }`}
          >
            {showAllLevels ? 'My Level Only' : 'Show All'}
          </button>
          
          <button
            onClick={expandedItems.size > 0 ? collapseAll : expandAll}
            className="px-3 py-1 bg-slate-700 text-slate-400 hover:text-slate-300 rounded text-xs font-medium transition-colors"
          >
            {expandedItems.size > 0 ? 'Collapse All' : 'Expand All'}
          </button>
        </div>
      </div>

      {/* Content Items */}
      <div className="space-y-3">
        {filteredContent.map(item => (
          <ExpandableContent
            key={item.id}
            item={item}
            isExpanded={expandedItems.has(item.id)}
            onToggle={() => toggleExpanded(item.id)}
            userLevel={userLevel}
          />
        ))}
      </div>

      {/* Learning Progress */}
      <div className="mt-6 p-4 bg-slate-800/50 rounded-lg border border-slate-700">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-slate-300">Learning Progress</span>
          <span className="text-sm text-slate-400">
            {expandedItems.size} of {filteredContent.length} explored
          </span>
        </div>
        <div className="w-full bg-slate-700 rounded-full h-2">
          <motion.div
            initial={{ width: 0 }}
            animate={{ 
              width: filteredContent.length > 0 
                ? `${(expandedItems.size / filteredContent.length) * 100}%` 
                : '0%' 
            }}
            className="bg-gradient-to-r from-primary-500 to-blue-500 h-2 rounded-full"
            transition={{ duration: 0.5 }}
          />
        </div>
      </div>
    </motion.div>
  );
};