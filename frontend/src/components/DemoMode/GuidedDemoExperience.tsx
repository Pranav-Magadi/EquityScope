import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Play, 
  Pause, 
  SkipForward, 
  SkipBack, 
  X, 
  BookOpen, 
  Lightbulb,
  CheckCircle,
  ArrowRight,
  Target,
  TrendingUp,
  Brain
} from 'lucide-react';
import { MultiStageValuationOutput } from '../DCFValuation/MultiStageValuationOutput';
import { DCFEducationalPanel } from '../DCFValuation/DCFEducationalPanel';
import { DEMO_ANALYSES, type DemoAnalysis } from '../../data/demoAnalyses';

interface GuidedDemoExperienceProps {
  ticker: string;
  onClose: () => void;
  isVisible: boolean;
}

interface DemoStep {
  id: string;
  title: string;
  description: string;
  content: React.ReactNode;
  duration: number; // seconds
  highlights: string[];
  interactionRequired?: boolean;
  educationalFocus?: string[];
}

const DemoControls: React.FC<{
  isPlaying: boolean;
  onPlayPause: () => void;
  currentStep: number;
  totalSteps: number;
  onPrevious: () => void;
  onNext: () => void;
  onClose: () => void;
}> = ({
  isPlaying,
  onPlayPause,
  currentStep,
  totalSteps,
  onPrevious,
  onNext,
  onClose
}) => {
  return (
    <div className="fixed bottom-0 left-0 right-0 bg-slate-900/95 backdrop-blur-sm border-t border-slate-700 p-4 z-60">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Progress */}
        <div className="flex items-center space-x-4">
          <div className="text-sm text-slate-400">
            Step {currentStep + 1} of {totalSteps}
          </div>
          <div className="w-32 bg-slate-700 rounded-full h-2">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${((currentStep + 1) / totalSteps) * 100}%` }}
              className="bg-primary-500 h-2 rounded-full"
              transition={{ duration: 0.5 }}
            />
          </div>
        </div>

        {/* Controls */}
        <div className="flex items-center space-x-2">
          <button
            onClick={onPrevious}
            disabled={currentStep === 0}
            className="p-2 bg-slate-700 hover:bg-slate-600 disabled:bg-slate-800 disabled:text-slate-600 text-slate-300 rounded-lg transition-colors"
          >
            <SkipBack className="h-5 w-5" />
          </button>
          
          <button
            onClick={onPlayPause}
            className="p-3 bg-primary-500 hover:bg-primary-600 text-white rounded-lg transition-colors"
          >
            {isPlaying ? <Pause className="h-5 w-5" /> : <Play className="h-5 w-5" />}
          </button>
          
          <button
            onClick={onNext}
            disabled={currentStep === totalSteps - 1}
            className="p-2 bg-slate-700 hover:bg-slate-600 disabled:bg-slate-800 disabled:text-slate-600 text-slate-300 rounded-lg transition-colors"
          >
            <SkipForward className="h-5 w-5" />
          </button>
        </div>

        {/* Close */}
        <button
          onClick={onClose}
          className="p-2 text-slate-400 hover:text-slate-200 transition-colors"
        >
          <X className="h-5 w-5" />
        </button>
      </div>
    </div>
  );
};

const DemoStepContent: React.FC<{
  step: DemoStep;
  demoAnalysis: DemoAnalysis;
  isActive: boolean;
}> = ({ step, demoAnalysis, isActive }) => {
  return (
    <AnimatePresence mode="wait">
      {isActive && (
        <motion.div
          key={step.id}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.5 }}
          className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full"
        >
          {/* Left Panel - Step Information */}
          <div className="lg:col-span-1 bg-slate-800/50 rounded-xl p-6 border border-slate-700">
            <div className="flex items-center space-x-3 mb-4">
              <div className="p-2 bg-primary-500/20 rounded-lg">
                <Target className="h-5 w-5 text-primary-400" />
              </div>
              <h3 className="text-lg font-semibold text-slate-100">{step.title}</h3>
            </div>
            
            <p className="text-sm text-slate-300 mb-6 leading-relaxed">
              {step.description}
            </p>

            {/* Highlights */}
            {step.highlights.length > 0 && (
              <div className="mb-6">
                <h4 className="text-sm font-medium text-slate-400 mb-3 flex items-center space-x-2">
                  <Lightbulb className="h-4 w-4" />
                  <span>Key Points</span>
                </h4>
                <div className="space-y-2">
                  {step.highlights.map((highlight, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="flex items-start space-x-2"
                    >
                      <CheckCircle className="h-4 w-4 text-green-400 mt-0.5 flex-shrink-0" />
                      <span className="text-xs text-slate-400">{highlight}</span>
                    </motion.div>
                  ))}
                </div>
              </div>
            )}

            {/* Educational Focus */}
            {step.educationalFocus && step.educationalFocus.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-slate-400 mb-3 flex items-center space-x-2">
                  <BookOpen className="h-4 w-4" />
                  <span>Learning Focus</span>
                </h4>
                <div className="flex flex-wrap gap-2">
                  {step.educationalFocus.map((focus, index) => (
                    <span
                      key={index}
                      className="px-2 py-1 bg-blue-500/20 text-blue-300 rounded text-xs"
                    >
                      {focus}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Right Panel - Content */}
          <div className="lg:col-span-2">
            {step.content}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export const GuidedDemoExperience: React.FC<GuidedDemoExperienceProps> = ({
  ticker,
  onClose,
  isVisible
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);

  // Auto-advance logic - must be before any early returns
  useEffect(() => {
    if (!isVisible) return;
    
    let interval: NodeJS.Timeout;
    
    if (isPlaying && currentStep < 6) { // assuming max 6 demo steps
      interval = setInterval(() => {
        setProgress(prev => {
          const newProgress = prev + 1;
          if (newProgress >= 15) { // default duration
            setCurrentStep(curr => curr + 1);
            return 0;
          }
          return newProgress;
        });
      }, 1000);
    }

    return () => clearInterval(interval);
  }, [isVisible, isPlaying, currentStep]);

  // Reset progress when step changes - must be before any early returns
  useEffect(() => {
    if (!isVisible) return;
    setProgress(0);
  }, [isVisible, currentStep]);

  const demoAnalysis = DEMO_ANALYSES[ticker];

  if (!demoAnalysis) {
    return null;
  }

  // Create demo steps dynamically based on the analysis
  const demoSteps: DemoStep[] = [
    {
      id: 'introduction',
      title: 'Welcome to the Demo',
      description: demoAnalysis.demoNarrative.introduction,
      content: (
        <div className="bg-gradient-to-r from-blue-900/20 to-purple-900/20 border border-blue-500/30 rounded-xl p-8 h-full flex flex-col justify-center">
          <div className="text-center">
            <div className="w-24 h-24 bg-primary-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
              <Brain className="h-12 w-12 text-primary-400" />
            </div>
            <h1 className="text-3xl font-bold text-slate-100 mb-4">{demoAnalysis.companyName}</h1>
            <p className="text-xl text-slate-300 mb-6">{demoAnalysis.description}</p>
            <div className="grid grid-cols-2 gap-4 max-w-md mx-auto">
              {demoAnalysis.highlights.slice(0, 4).map((highlight, index) => (
                <div key={index} className="bg-slate-800/50 rounded-lg p-3">
                  <span className="text-sm text-slate-300">{highlight}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      ),
      duration: 10,
      highlights: demoAnalysis.demoNarrative.learningObjectives,
      educationalFocus: ['Introduction', 'Company Overview']
    },
    {
      id: 'company_analysis',
      title: 'Company Analysis Overview',
      description: 'Let\'s start by understanding the company\'s fundamental characteristics, market position, and recent performance.',
      content: (
        <div className="space-y-6">
          {/* Company Info Card */}
          <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
            <h3 className="text-lg font-semibold text-slate-100 mb-4">Company Overview</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-xs text-slate-400">Sector</p>
                <p className="text-sm font-medium text-slate-200">{demoAnalysis.companyAnalysis.company_info.sector}</p>
              </div>
              <div>
                <p className="text-xs text-slate-400">Market Cap</p>
                <p className="text-sm font-medium text-slate-200">
                  ₹{(demoAnalysis.companyAnalysis.company_info.market_cap! / 1000000000000).toFixed(1)}T
                </p>
              </div>
              <div>
                <p className="text-xs text-slate-400">Current Price</p>
                <p className="text-sm font-medium text-slate-200">
                  ₹{demoAnalysis.companyAnalysis.stock_price.current_price.toFixed(2)}
                </p>
              </div>
              <div>
                <p className="text-xs text-slate-400">P/E Ratio</p>
                <p className="text-sm font-medium text-slate-200">
                  {demoAnalysis.companyAnalysis.stock_price.pe_ratio?.toFixed(1)}x
                </p>
              </div>
            </div>
          </div>

          {/* SWOT Preview */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-green-900/20 border border-green-500/30 rounded-xl p-4">
              <h4 className="font-medium text-green-300 mb-2">Key Strengths</h4>
              <ul className="space-y-1">
                {demoAnalysis.companyAnalysis.swot.strengths.slice(0, 2).map((strength, index) => (
                  <li key={index} className="text-xs text-slate-300">• {strength}</li>
                ))}
              </ul>
            </div>
            <div className="bg-blue-900/20 border border-blue-500/30 rounded-xl p-4">
              <h4 className="font-medium text-blue-300 mb-2">Key Opportunities</h4>
              <ul className="space-y-1">
                {demoAnalysis.companyAnalysis.swot.opportunities.slice(0, 2).map((opportunity, index) => (
                  <li key={index} className="text-xs text-slate-300">• {opportunity}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      ),
      duration: 15,
      highlights: [
        'Review company fundamentals and market position',
        'Understand sector-specific characteristics',
        'Identify key strengths and growth opportunities',
        'Assess current valuation metrics'
      ],
      educationalFocus: ['Company Analysis', 'Market Position', 'Qualitative Factors']
    },
    {
      id: 'mode_selection',
      title: 'DCF Mode Selection',
      description: demoAnalysis.demoNarrative.modeExplanation,
      content: (
        <div className="space-y-6">
          <div className={`border-2 rounded-xl p-6 ${
            demoAnalysis.dcfResponse.mode === 'simple'
              ? 'border-green-500/50 bg-green-900/20'
              : 'border-blue-500/50 bg-blue-900/20'
          }`}>
            <div className="flex items-center space-x-3 mb-4">
              {demoAnalysis.dcfResponse.mode === 'simple' ? (
                <BookOpen className="h-8 w-8 text-green-400" />
              ) : (
                <Brain className="h-8 w-8 text-blue-400" />
              )}
              <div>
                <h3 className="text-xl font-semibold text-slate-100">
                  {demoAnalysis.dcfResponse.mode.charAt(0).toUpperCase() + demoAnalysis.dcfResponse.mode.slice(1)} Mode Selected
                </h3>
                <p className="text-sm text-slate-400">
                  {demoAnalysis.dcfResponse.education_content.mode_explanation}
                </p>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-medium text-slate-300 mb-2">Key Benefits</h4>
                <p className="text-sm text-slate-400">{demoAnalysis.dcfResponse.education_content.key_benefits}</p>
              </div>
              <div>
                <h4 className="font-medium text-slate-300 mb-2">Best For</h4>
                <p className="text-sm text-slate-400">{demoAnalysis.dcfResponse.education_content.best_for}</p>
              </div>
            </div>
          </div>

          <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
            <h4 className="font-medium text-slate-300 mb-3">Growth Methodology</h4>
            <p className="text-sm text-slate-400 mb-4">{demoAnalysis.dcfResponse.education_content.growth_methodology}</p>
            
            <div className="grid grid-cols-4 gap-3">
              {demoAnalysis.dcfResponse.growth_stages_summary.map((stage, index) => (
                <div key={index} className="text-center">
                  <div className="text-lg font-bold text-primary-400">{stage.growth_rate}</div>
                  <div className="text-xs text-slate-400">Years {stage.years}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      ),
      duration: 20,
      highlights: demoAnalysis.demoNarrative.keyInsights.slice(0, 3),
      educationalFocus: ['Mode Selection', 'Growth Methodology', 'AI Enhancement']
    },
    {
      id: 'dcf_results',
      title: '10-Year DCF Analysis Results',
      description: 'Now let\'s explore the detailed DCF analysis results, including the multi-stage growth projections and valuation output.',
      content: (
        <MultiStageValuationOutput
          dcfResponse={demoAnalysis.dcfResponse}
          userLevel="intermediate"
          isLoading={false}
        />
      ),
      duration: 30,
      highlights: [
        'Multi-stage growth waterfall visualization',
        '10-year projection charts and analysis', 
        'GDP blending methodology in action',
        'Intrinsic value calculation breakdown'
      ],
      educationalFocus: ['DCF Results', 'Valuation Output', 'Growth Stages', 'Present Value']
    },
    {
      id: 'key_insights',
      title: 'Key Investment Insights',
      description: 'Let\'s summarize the key insights from our analysis and what they mean for investment decisions.',
      content: (
        <div className="space-y-6">
          <div className="bg-gradient-to-r from-primary-900/20 to-blue-900/20 border border-primary-500/30 rounded-xl p-6">
            <h3 className="text-xl font-semibold text-slate-100 mb-4">Investment Summary</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-3xl font-bold text-primary-400 mb-2">
                  ₹{demoAnalysis.dcfResponse.valuation.intrinsic_value_per_share.toFixed(0)}
                </div>
                <div className="text-sm text-slate-400">Intrinsic Value</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-slate-300 mb-2">
                  ₹{demoAnalysis.dcfResponse.valuation.current_stock_price.toFixed(0)}
                </div>
                <div className="text-sm text-slate-400">Current Price</div>
              </div>
              <div className="text-center">
                <div className={`text-3xl font-bold mb-2 ${
                  demoAnalysis.dcfResponse.valuation.upside_downside > 0 ? 'text-green-400' : 'text-red-400'
                }`}>
                  {demoAnalysis.dcfResponse.valuation.upside_downside > 0 ? '+' : ''}{demoAnalysis.dcfResponse.valuation.upside_downside.toFixed(1)}%
                </div>
                <div className="text-sm text-slate-400">
                  {demoAnalysis.dcfResponse.valuation.upside_downside > 0 ? 'Upside' : 'Downside'}
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700">
              <h4 className="font-medium text-slate-300 mb-3">Key Insights</h4>
              <ul className="space-y-2">
                {demoAnalysis.demoNarrative.keyInsights.map((insight, index) => (
                  <li key={index} className="flex items-start space-x-2">
                    <TrendingUp className="h-4 w-4 text-green-400 mt-0.5 flex-shrink-0" />
                    <span className="text-sm text-slate-400">{insight}</span>
                  </li>
                ))}
              </ul>
            </div>
            
            <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700">
              <h4 className="font-medium text-slate-300 mb-3">Conclusion Points</h4>
              <ul className="space-y-2">
                {demoAnalysis.demoNarrative.conclusionPoints.map((conclusion, index) => (
                  <li key={index} className="flex items-start space-x-2">
                    <CheckCircle className="h-4 w-4 text-blue-400 mt-0.5 flex-shrink-0" />
                    <span className="text-sm text-slate-400">{conclusion}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      ),
      duration: 20,
      highlights: demoAnalysis.demoNarrative.conclusionPoints,
      educationalFocus: ['Investment Decision', 'Valuation Interpretation', 'Risk Assessment']
    }
  ];

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handleNext = () => {
    if (currentStep < demoSteps.length - 1) {
      setCurrentStep(currentStep + 1);
      setProgress(0);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
      setProgress(0);
    }
  };

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 bg-slate-900 z-50">
      {/* Main Content */}
      <div className="h-full overflow-y-auto pb-20">
        <div className="max-w-7xl mx-auto p-6">
          <DemoStepContent
            step={demoSteps[currentStep]}
            demoAnalysis={demoAnalysis}
            isActive={true}
          />
        </div>
      </div>

      {/* Controls */}
      <DemoControls
        isPlaying={isPlaying}
        onPlayPause={handlePlayPause}
        currentStep={currentStep}
        totalSteps={demoSteps.length}
        onPrevious={handlePrevious}
        onNext={handleNext}
        onClose={onClose}
      />
    </div>
  );
};