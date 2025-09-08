import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Play, BookOpen, TrendingUp, Building2, Zap, ChevronRight, Star } from 'lucide-react';

interface DemoOption {
  ticker: string;
  companyName: string;
  sector: string;
  description: string;
  highlights: string[];
  mode: 'simple' | 'agentic';
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  duration: string;
  keyLearnings: string[];
}

interface DemoModeSelectorProps {
  onDemoSelect: (ticker: string) => void;
  onClose: () => void;
  isVisible: boolean;
}

const demoOptions: DemoOption[] = [
  {
    ticker: 'TCS.NS',
    companyName: 'Tata Consultancy Services',
    sector: 'Information Technology',
    description: 'Perfect for learning DCF fundamentals with a stable, profitable IT services leader.',
    highlights: [
      'Consistent 12-15% historical growth',
      'Predictable business model',
      'Strong margin expansion story',
      'Market leadership position'
    ],
    mode: 'simple',
    difficulty: 'beginner',
    duration: '8-10 minutes',
    keyLearnings: [
      'Historical validation methodology',
      'Multi-stage growth modeling',
      'GDP blending concepts',
      'Conservative DCF approach'
    ]
  },
  {
    ticker: 'RELIANCE.NS',
    companyName: 'Reliance Industries',
    sector: 'Diversified Conglomerate',
    description: 'Advanced analysis showcasing transformation from oil & gas to digital giant.',
    highlights: [
      'Digital transformation success',
      'Multi-business complexity',
      'Strategic partnerships impact',
      'AI-enhanced projections'
    ],
    mode: 'agentic',
    difficulty: 'advanced',
    duration: '12-15 minutes',
    keyLearnings: [
      'Business transformation analysis',
      'Management guidance integration',
      'Multi-segment valuation',
      'Forward-looking AI insights'
    ]
  },
  {
    ticker: 'HDFCBANK.NS',
    companyName: 'HDFC Bank',
    sector: 'Banking & Financial Services',
    description: 'Intermediate analysis of India\'s leading private bank with unique DCF considerations.',
    highlights: [
      'Banking sector DCF nuances',
      'Credit cycle considerations',
      'ROE and book value dynamics',
      'Regulatory environment impact'
    ],
    mode: 'simple',
    difficulty: 'intermediate',
    duration: '10-12 minutes',
    keyLearnings: [
      'Financial services valuation',
      'Asset quality analysis',
      'Regulatory impact modeling',
      'Bank-specific metrics'
    ]
  }
];

const getDifficultyColor = (difficulty: string) => {
  switch (difficulty) {
    case 'beginner': return 'text-green-400 bg-green-500/20';
    case 'intermediate': return 'text-yellow-400 bg-yellow-500/20';
    case 'advanced': return 'text-red-400 bg-red-500/20';
    default: return 'text-slate-400 bg-slate-500/20';
  }
};

const getModeIcon = (mode: string) => {
  return mode === 'simple' ? BookOpen : Zap;
};

const DemoCard: React.FC<{ demo: DemoOption; onSelect: () => void }> = ({ demo, onSelect }) => {
  const [isHovered, setIsHovered] = useState(false);
  const ModeIcon = getModeIcon(demo.mode);
  
  return (
    <motion.div
      whileHover={{ scale: 1.02, y: -4 }}
      whileTap={{ scale: 0.98 }}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
      onClick={onSelect}
      className="bg-slate-800/50 border border-slate-700 hover:border-slate-600 rounded-xl p-6 cursor-pointer transition-all duration-300 relative overflow-hidden"
    >
      {/* Background Gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary-900/10 to-blue-900/10 opacity-0 hover:opacity-100 transition-opacity duration-300" />
      
      {/* Header */}
      <div className="relative z-10 flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-primary-500/20 rounded-lg">
            <Building2 className="h-6 w-6 text-primary-400" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-slate-100">{demo.companyName}</h3>
            <p className="text-sm text-slate-400">{demo.ticker} • {demo.sector}</p>
          </div>
        </div>
        
        <motion.div
          animate={{ x: isHovered ? 4 : 0 }}
          className="flex items-center space-x-2"
        >
          <Play className="h-5 w-5 text-primary-400" />
        </motion.div>
      </div>

      {/* Tags */}
      <div className="relative z-10 flex items-center space-x-2 mb-4">
        <div className={`px-2 py-1 rounded text-xs font-medium ${getDifficultyColor(demo.difficulty)}`}>
          {demo.difficulty.toUpperCase()}
        </div>
        <div className={`px-2 py-1 rounded text-xs font-medium flex items-center space-x-1 ${
          demo.mode === 'simple' 
            ? 'text-green-400 bg-green-500/20' 
            : 'text-blue-400 bg-blue-500/20'
        }`}>
          <ModeIcon className="h-3 w-3" />
          <span>{demo.mode.toUpperCase()} MODE</span>
        </div>
        <div className="px-2 py-1 bg-slate-700/50 rounded text-xs text-slate-400">
          {demo.duration}
        </div>
      </div>

      {/* Description */}
      <p className="relative z-10 text-sm text-slate-300 mb-4 leading-relaxed">
        {demo.description}
      </p>

      {/* Highlights */}
      <div className="relative z-10 mb-4">
        <h4 className="text-xs font-medium text-slate-400 mb-2">Key Highlights:</h4>
        <div className="grid grid-cols-2 gap-2">
          {demo.highlights.map((highlight, index) => (
            <div key={index} className="flex items-center space-x-2">
              <Star className="h-3 w-3 text-yellow-500 flex-shrink-0" />
              <span className="text-xs text-slate-400">{highlight}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Learning Objectives */}
      <div className="relative z-10">
        <h4 className="text-xs font-medium text-slate-400 mb-2">You'll Learn:</h4>
        <div className="space-y-1">
          {demo.keyLearnings.slice(0, 2).map((learning, index) => (
            <div key={index} className="flex items-center space-x-2">
              <ChevronRight className="h-3 w-3 text-primary-400 flex-shrink-0" />
              <span className="text-xs text-slate-400">{learning}</span>
            </div>
          ))}
          {demo.keyLearnings.length > 2 && (
            <div className="text-xs text-slate-500">
              +{demo.keyLearnings.length - 2} more concepts...
            </div>
          )}
        </div>
      </div>

      {/* Start Button */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: isHovered ? 1 : 0, y: isHovered ? 0 : 10 }}
        className="absolute bottom-4 right-4 z-10"
      >
        <div className="bg-primary-500 hover:bg-primary-600 text-white px-3 py-1 rounded-lg text-xs font-medium flex items-center space-x-1">
          <Play className="h-3 w-3" />
          <span>Start Demo</span>
        </div>
      </motion.div>
    </motion.div>
  );
};

export const DemoModeSelector: React.FC<DemoModeSelectorProps> = ({
  onDemoSelect,
  onClose,
  isVisible
}) => {
  if (!isVisible) return null;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 20 }}
        onClick={(e) => e.stopPropagation()}
        className="bg-slate-900 border border-slate-700 rounded-2xl p-8 max-w-6xl w-full max-h-[90vh] overflow-y-auto"
      >
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center space-x-3 mb-4">
            <div className="p-3 bg-gradient-to-r from-primary-500 to-blue-500 rounded-xl">
              <Play className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-slate-100">Demo Mode</h1>
              <p className="text-slate-400">Interactive DCF Analysis Walkthroughs</p>
            </div>
          </div>
          
          <p className="text-slate-300 max-w-2xl mx-auto">
            Experience our 10-year multi-stage DCF system through guided analyses of popular Indian stocks. 
            Each demo showcases different aspects of our advanced valuation methodology.
          </p>
        </div>

        {/* Demo Options */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {demoOptions.map((demo) => (
            <DemoCard
              key={demo.ticker}
              demo={demo}
              onSelect={() => onDemoSelect(demo.ticker)}
            />
          ))}
        </div>

        {/* Learning Path Suggestion */}
        <div className="bg-gradient-to-r from-blue-900/20 to-purple-900/20 border border-blue-500/30 rounded-xl p-6">
          <div className="flex items-center space-x-3 mb-4">
            <TrendingUp className="h-6 w-6 text-blue-400" />
            <h3 className="text-lg font-semibold text-slate-100">Recommended Learning Path</h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="w-8 h-8 bg-green-500 text-white rounded-full flex items-center justify-center mx-auto mb-2 text-sm font-bold">1</div>
              <h4 className="font-medium text-green-300 mb-1">Start with TCS</h4>
              <p className="text-xs text-slate-400">Learn DCF fundamentals with a stable, predictable business</p>
            </div>
            
            <div className="text-center">
              <div className="w-8 h-8 bg-yellow-500 text-slate-900 rounded-full flex items-center justify-center mx-auto mb-2 text-sm font-bold">2</div>
              <h4 className="font-medium text-yellow-300 mb-1">Progress to HDFC Bank</h4>
              <p className="text-xs text-slate-400">Explore sector-specific considerations in financial services</p>
            </div>
            
            <div className="text-center">
              <div className="w-8 h-8 bg-red-500 text-white rounded-full flex items-center justify-center mx-auto mb-2 text-sm font-bold">3</div>
              <h4 className="font-medium text-red-300 mb-1">Master with Reliance</h4>
              <p className="text-xs text-slate-400">Advanced AI-enhanced analysis of complex transformations</p>
            </div>
          </div>
        </div>

        {/* Close Button */}
        <div className="flex justify-center mt-8">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg transition-colors"
          >
            Close
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
};