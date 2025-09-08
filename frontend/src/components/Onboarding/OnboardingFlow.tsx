import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  PlayCircle, 
  ArrowRight, 
  ArrowLeft, 
  Check, 
  TrendingUp, 
  BarChart3, 
  Calculator, 
  Lightbulb,
  X,
  ChevronRight,
  Star,
  Target,
  Brain
} from 'lucide-react';

interface OnboardingFlowProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete: () => void;
}

interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  icon: React.ComponentType<any>;
  content: React.ReactNode;
  interactiveDemo?: boolean;
}

const WelcomeStep: React.FC = () => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    className="text-center space-y-6"
  >
    <div className="w-20 h-20 bg-gradient-to-r from-primary-500 to-primary-600 rounded-full flex items-center justify-center mx-auto">
      <TrendingUp className="h-10 w-10 text-white" />
    </div>
    <div>
      <h2 className="text-2xl font-bold text-slate-100 mb-3">Welcome to EquityScope!</h2>
      <p className="text-slate-400 text-lg leading-relaxed">
        Your AI-powered DCF analysis platform that transforms complex financial modeling 
        into clear, actionable insights.
      </p>
    </div>
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
      <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
        <Brain className="h-8 w-8 text-primary-400 mb-2" />
        <h3 className="font-semibold text-slate-200 mb-1">AI-Powered Analysis</h3>
        <p className="text-sm text-slate-400">Advanced AI agents analyze companies for you</p>
      </div>
      <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
        <Calculator className="h-8 w-8 text-primary-400 mb-2" />
        <h3 className="font-semibold text-slate-200 mb-1">10-Year DCF Models</h3>
        <p className="text-sm text-slate-400">Multi-stage growth projections with validation</p>
      </div>
      <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
        <Lightbulb className="h-8 w-8 text-primary-400 mb-2" />
        <h3 className="font-semibold text-slate-200 mb-1">Educational Insights</h3>
        <p className="text-sm text-slate-400">Learn DCF concepts as you analyze</p>
      </div>
    </div>
  </motion.div>
);

const DCFBasicsStep: React.FC = () => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    className="space-y-6"
  >
    <div className="text-center">
      <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
        <Calculator className="h-8 w-8 text-white" />
      </div>
      <h2 className="text-xl font-bold text-slate-100 mb-3">DCF Analysis Fundamentals</h2>
      <p className="text-slate-400">
        Discounted Cash Flow (DCF) analysis estimates a company's intrinsic value based on future cash flows.
      </p>
    </div>

    <div className="bg-slate-800/30 rounded-lg p-6 border border-slate-700">
      <h3 className="font-semibold text-slate-200 mb-4">Key Components:</h3>
      <div className="space-y-4">
        <div className="flex items-start space-x-3">
          <div className="w-6 h-6 bg-primary-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
            <span className="text-white text-sm font-bold">1</span>
          </div>
          <div>
            <h4 className="font-medium text-slate-200">Revenue Projections</h4>
            <p className="text-sm text-slate-400">Forecast future sales growth based on market analysis</p>
          </div>
        </div>
        <div className="flex items-start space-x-3">
          <div className="w-6 h-6 bg-primary-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
            <span className="text-white text-sm font-bold">2</span>
          </div>
          <div>
            <h4 className="font-medium text-slate-200">Cash Flow Calculation</h4>
            <p className="text-sm text-slate-400">Convert revenues to free cash flows after expenses and taxes</p>
          </div>
        </div>
        <div className="flex items-start space-x-3">
          <div className="w-6 h-6 bg-primary-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
            <span className="text-white text-sm font-bold">3</span>
          </div>
          <div>
            <h4 className="font-medium text-slate-200">Discount Rate (WACC)</h4>
            <p className="text-sm text-slate-400">Risk-adjusted rate to bring future cash flows to present value</p>
          </div>
        </div>
        <div className="flex items-start space-x-3">
          <div className="w-6 h-6 bg-primary-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
            <span className="text-white text-sm font-bold">4</span>
          </div>
          <div>
            <h4 className="font-medium text-slate-200">Terminal Value</h4>
            <p className="text-sm text-slate-400">Value beyond the projection period, typically the largest component</p>
          </div>
        </div>
      </div>
    </div>

    <div className="bg-gradient-to-r from-primary-500/10 to-blue-500/10 rounded-lg p-4 border border-primary-500/20">
      <div className="flex items-center space-x-2 mb-2">
        <Lightbulb className="h-5 w-5 text-primary-400" />
        <span className="font-medium text-primary-300">Pro Tip</span>
      </div>
      <p className="text-sm text-slate-300">
        DCF analysis is most reliable for companies with predictable cash flows. 
        Our AI helps identify the best valuation approach for each company.
      </p>
    </div>
  </motion.div>
);

const FeaturesStep: React.FC = () => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    className="space-y-6"
  >
    <div className="text-center">
      <div className="w-16 h-16 bg-gradient-to-r from-green-500 to-green-600 rounded-full flex items-center justify-center mx-auto mb-4">
        <Star className="h-8 w-8 text-white" />
      </div>
      <h2 className="text-xl font-bold text-slate-100 mb-3">Powerful Features</h2>
      <p className="text-slate-400">
        Discover what makes EquityScope the most advanced DCF analysis platform.
      </p>
    </div>

    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div className="bg-slate-800/50 rounded-lg p-5 border border-slate-700 hover:border-primary-500/50 transition-colors">
        <div className="flex items-center space-x-3 mb-3">
          <div className="w-10 h-10 bg-primary-500/20 rounded-lg flex items-center justify-center">
            <Brain className="h-5 w-5 text-primary-400" />
          </div>
          <h3 className="font-semibold text-slate-200">AI Investment Committee</h3>
        </div>
        <p className="text-sm text-slate-400 mb-3">
          Multiple AI agents debate valuation like a real investment committee, providing balanced perspectives.
        </p>
        <div className="text-xs text-primary-400 font-medium">
          ✓ Bull, Bear, and Neutral viewpoints
        </div>
      </div>

      <div className="bg-slate-800/50 rounded-lg p-5 border border-slate-700 hover:border-primary-500/50 transition-colors">
        <div className="flex items-center space-x-3 mb-3">
          <div className="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center">
            <BarChart3 className="h-5 w-5 text-blue-400" />
          </div>
          <h3 className="font-semibold text-slate-200">Progressive Disclosure</h3>
        </div>
        <p className="text-sm text-slate-400 mb-3">
          Start with simple summaries, dive deeper into detailed analysis as you learn.
        </p>
        <div className="text-xs text-blue-400 font-medium">
          ✓ Beginner to Expert modes
        </div>
      </div>

      <div className="bg-slate-800/50 rounded-lg p-5 border border-slate-700 hover:border-primary-500/50 transition-colors">
        <div className="flex items-center space-x-3 mb-3">
          <div className="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center">
            <Target className="h-5 w-5 text-purple-400" />
          </div>
          <h3 className="font-semibold text-slate-200">Multi-Model Valuation</h3>
        </div>
        <p className="text-sm text-slate-400 mb-3">
          DCF, DDM, and Asset-based models automatically selected based on company characteristics.
        </p>
        <div className="text-xs text-purple-400 font-medium">
          ✓ Smart model selection
        </div>
      </div>

      <div className="bg-slate-800/50 rounded-lg p-5 border border-slate-700 hover:border-primary-500/50 transition-colors">
        <div className="flex items-center space-x-3 mb-3">
          <div className="w-10 h-10 bg-orange-500/20 rounded-lg flex items-center justify-center">
            <Lightbulb className="h-5 w-5 text-orange-400" />
          </div>
          <h3 className="font-semibold text-slate-200">Educational Insights</h3>
        </div>
        <p className="text-sm text-slate-400 mb-3">
          "What This Means" sections explain complex concepts in plain English.
        </p>
        <div className="text-xs text-orange-400 font-medium">
          ✓ Learn while you analyze
        </div>
      </div>
    </div>

    <div className="bg-gradient-to-r from-green-500/10 to-blue-500/10 rounded-lg p-4 border border-green-500/20">
      <div className="flex items-center space-x-2 mb-2">
        <Star className="h-5 w-5 text-green-400" />
        <span className="font-medium text-green-300">Getting Started</span>
      </div>
      <p className="text-sm text-slate-300">
        Try our demo analyses (TCS, Reliance, HDFC Bank) to see these features in action!
      </p>
    </div>
  </motion.div>
);

const DemoStep: React.FC<{ onTryDemo: () => void }> = ({ onTryDemo }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    className="space-y-6"
  >
    <div className="text-center">
      <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
        <PlayCircle className="h-8 w-8 text-white" />
      </div>
      <h2 className="text-xl font-bold text-slate-100 mb-3">Try a Demo Analysis</h2>
      <p className="text-slate-400">
        Experience the power of EquityScope with our pre-built demo analyses.
      </p>
    </div>

    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <motion.div
        whileHover={{ scale: 1.02 }}
        className="bg-slate-800/50 rounded-lg p-5 border border-slate-700 hover:border-primary-500/50 transition-all cursor-pointer"
        onClick={onTryDemo}
      >
        <div className="text-center space-y-3">
          <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center mx-auto">
            <span className="text-green-400 font-bold text-lg">T</span>
          </div>
          <div>
            <h3 className="font-semibold text-slate-200">TCS Limited</h3>
            <p className="text-sm text-slate-400">Technology Services</p>
          </div>
          <div className="text-xs text-green-400 font-medium">Beginner Friendly</div>
        </div>
      </motion.div>

      <motion.div
        whileHover={{ scale: 1.02 }}
        className="bg-slate-800/50 rounded-lg p-5 border border-slate-700 hover:border-primary-500/50 transition-all cursor-pointer"
        onClick={onTryDemo}
      >
        <div className="text-center space-y-3">
          <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center mx-auto">
            <span className="text-blue-400 font-bold text-lg">R</span>
          </div>
          <div>
            <h3 className="font-semibold text-slate-200">Reliance Industries</h3>
            <p className="text-sm text-slate-400">Diversified Conglomerate</p>
          </div>
          <div className="text-xs text-blue-400 font-medium">Intermediate</div>
        </div>
      </motion.div>

      <motion.div
        whileHover={{ scale: 1.02 }}
        className="bg-slate-800/50 rounded-lg p-5 border border-slate-700 hover:border-primary-500/50 transition-all cursor-pointer"
        onClick={onTryDemo}
      >
        <div className="text-center space-y-3">
          <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center mx-auto">
            <span className="text-purple-400 font-bold text-lg">H</span>
          </div>
          <div>
            <h3 className="font-semibold text-slate-200">HDFC Bank</h3>
            <p className="text-sm text-slate-400">Private Banking</p>
          </div>
          <div className="text-xs text-purple-400 font-medium">Advanced</div>
        </div>
      </motion.div>
    </div>

    <div className="bg-slate-800/30 rounded-lg p-4 border border-slate-700">
      <div className="flex items-start space-x-3">
        <PlayCircle className="h-5 w-5 text-primary-400 mt-0.5 flex-shrink-0" />
        <div>
          <h4 className="font-medium text-slate-200 mb-1">What you'll experience:</h4>
          <ul className="text-sm text-slate-400 space-y-1">
            <li>• Complete AI-powered analysis in under 30 seconds</li>
            <li>• Multi-perspective investment committee discussion</li>
            <li>• 10-year DCF projections with scenario analysis</li>
            <li>• Educational insights explaining every concept</li>
          </ul>
        </div>
      </div>
    </div>

    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onTryDemo}
      className="w-full bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 text-white py-3 px-6 rounded-lg font-medium transition-all flex items-center justify-center space-x-2"
    >
      <PlayCircle className="h-5 w-5" />
      <span>Try TCS Demo Analysis</span>
      <ChevronRight className="h-4 w-4" />
    </motion.button>
  </motion.div>
);

export const OnboardingFlow: React.FC<OnboardingFlowProps> = ({
  isOpen,
  onClose,
  onComplete
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState<Set<number>>(new Set());

  const steps: OnboardingStep[] = [
    {
      id: 'welcome',
      title: 'Welcome',
      description: 'Introduction to EquityScope',
      icon: TrendingUp,
      content: <WelcomeStep />
    },
    {
      id: 'dcf-basics',
      title: 'DCF Fundamentals',
      description: 'Learn the basics of DCF analysis',
      icon: Calculator,
      content: <DCFBasicsStep />
    },
    {
      id: 'features',
      title: 'Key Features',
      description: 'Discover our powerful capabilities',
      icon: Star,
      content: <FeaturesStep />
    },
    {
      id: 'demo',
      title: 'Try Demo',
      description: 'Experience our platform firsthand',
      icon: PlayCircle,
      content: <DemoStep onTryDemo={() => handleDemoClick()} />
    }
  ];

  const handleDemoClick = () => {
    // Trigger demo mode and close onboarding
    onComplete();
    onClose();
    // In a real implementation, this would navigate to demo mode
    // For now, we'll just complete the onboarding
  };

  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setCompletedSteps(prev => new Set(Array.from(prev).concat(currentStep)));
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = () => {
    setCompletedSteps(prev => new Set(Array.from(prev).concat(currentStep)));
    onComplete();
    onClose();
  };

  const isLastStep = currentStep === steps.length - 1;

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="bg-slate-900 rounded-2xl border border-slate-700 w-full max-w-4xl max-h-[90vh] overflow-hidden shadow-2xl"
        >
          {/* Header */}
          <div className="bg-slate-800/50 border-b border-slate-700 p-6 flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-r from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
                  <TrendingUp className="h-4 w-4 text-white" />
                </div>
                <span className="font-semibold text-slate-100">EquityScope Onboarding</span>
              </div>
              <div className="text-sm text-slate-400">
                Step {currentStep + 1} of {steps.length}
              </div>
            </div>
            <button
              onClick={onClose}
              className="w-8 h-8 bg-slate-700 hover:bg-slate-600 rounded-lg flex items-center justify-center text-slate-400 hover:text-slate-200 transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          {/* Progress Bar */}
          <div className="bg-slate-800 px-6 py-3">
            <div className="flex items-center space-x-2">
              {steps.map((step, index) => (
                <div key={step.id} className="flex items-center">
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-all ${
                      index < currentStep
                        ? 'bg-primary-500 text-white'
                        : index === currentStep
                        ? 'bg-primary-500 text-white ring-2 ring-primary-400'
                        : 'bg-slate-700 text-slate-400'
                    }`}
                  >
                    {completedSteps.has(index) ? (
                      <Check className="h-4 w-4" />
                    ) : (
                      index + 1
                    )}
                  </div>
                  {index < steps.length - 1 && (
                    <div
                      className={`w-8 h-0.5 mx-2 transition-colors ${
                        index < currentStep ? 'bg-primary-500' : 'bg-slate-700'
                      }`}
                    />
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Content */}
          <div className="p-6 overflow-y-auto max-h-[60vh]">
            <AnimatePresence mode="wait">
              <motion.div
                key={currentStep}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
              >
                {steps[currentStep].content}
              </motion.div>
            </AnimatePresence>
          </div>

          {/* Footer */}
          <div className="bg-slate-800/50 border-t border-slate-700 p-6 flex items-center justify-between">
            <button
              onClick={prevStep}
              disabled={currentStep === 0}
              className="flex items-center space-x-2 px-4 py-2 text-slate-400 hover:text-slate-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <ArrowLeft className="h-4 w-4" />
              <span>Previous</span>
            </button>

            <div className="flex items-center space-x-3">
              <button
                onClick={() => {
                  onComplete();
                  onClose();
                }}
                className="text-slate-400 hover:text-slate-200 text-sm transition-colors"
              >
                Skip Tutorial
              </button>
              
              {isLastStep ? (
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleComplete}
                  className="bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 text-white px-6 py-2 rounded-lg font-medium transition-all flex items-center space-x-2"
                >
                  <span>Get Started</span>
                  <ArrowRight className="h-4 w-4" />
                </motion.button>
              ) : (
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={nextStep}
                  className="bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 text-white px-6 py-2 rounded-lg font-medium transition-all flex items-center space-x-2"
                >
                  <span>Next</span>
                  <ArrowRight className="h-4 w-4" />
                </motion.button>
              )}
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};