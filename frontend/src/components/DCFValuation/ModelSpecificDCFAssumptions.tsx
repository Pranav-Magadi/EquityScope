import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Info, 
  RotateCcw, 
  TrendingUp, 
  Percent, 
  Brain, 
  BarChart3, 
  AlertTriangle, 
  Target, 
  Shield, 
  Beaker, 
  Layers 
} from 'lucide-react';
import { DCFModelType, DCFModelAssumptions, DCFModelDefaults } from '../../types/dcfModels';
import { DCFModelConfigurations, getEnhancedTooltip, validateAssumption } from '../../utils/dcfModelConfig';

// Icon mapping for model-specific assumptions
const IconMap: Record<string, React.ComponentType<{ className?: string }>> = {
  'TrendingUp': TrendingUp,
  'Percent': Percent,
  'Brain': Brain,
  'BarChart3': BarChart3,
  'AlertTriangle': AlertTriangle,
  'Target': Target,
  'Shield': Shield,
  'Beaker': Beaker,
  'Layers': Layers
};

interface ModelSpecificDCFAssumptionsProps {
  modelType: DCFModelType;
  assumptions: DCFModelAssumptions;
  defaults: DCFModelDefaults;
  onUpdateAssumption: (key: string, value: number) => void;
  onResetToDefaults: () => void;
  sector: string;
  mode?: 'simple' | 'agentic'; // For multi-stage DCF
}

interface SliderInputProps {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  suffix: string;
  tooltip: string;
  onChange: (value: number) => void;
  defaultValue?: number;
  icon: React.ComponentType<{ className?: string }>;
  category: string;
}

const SliderInput: React.FC<SliderInputProps> = ({
  label,
  value,
  min,
  max,
  step,
  suffix,
  tooltip,
  onChange,
  defaultValue,
  icon: Icon,
  category
}) => {
  const [showTooltip, setShowTooltip] = useState(false);
  const [validationError, setValidationError] = useState<string | undefined>();
  const isModified = defaultValue !== undefined && Math.abs(value - defaultValue) > 0.01;

  // Calculate slider position percentage
  const percentage = ((value - min) / (max - min)) * 100;

  // Category color mapping
  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'growth': return 'text-green-400';
      case 'profitability': return 'text-blue-400';
      case 'risk': return 'text-red-400';
      case 'operational': return 'text-yellow-400';
      case 'regulatory': return 'text-purple-400';
      default: return 'text-primary-400';
    }
  };

  const handleChange = (newValue: number) => {
    setValidationError(undefined);
    onChange(newValue);
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Icon className={`h-4 w-4 ${getCategoryColor(category)}`} />
          <label className="text-sm font-medium text-slate-200">{label}</label>
          <div className="relative">
            <Info
              className="h-3 w-3 text-slate-400 cursor-help hover:text-slate-300 transition-colors"
              onMouseEnter={() => setShowTooltip(true)}
              onMouseLeave={() => setShowTooltip(false)}
              data-testid="info-icon"
            />
            {showTooltip && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="absolute z-10 w-80 p-3 mt-1 text-xs text-slate-200 bg-slate-800 border border-slate-600 rounded-lg shadow-lg -left-32"
              >
                <div className="font-medium text-slate-100 mb-1">{label}</div>
                <div>{tooltip}</div>
              </motion.div>
            )}
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <span className={`text-sm font-mono ${isModified ? 'text-primary-300' : 'text-slate-300'}`}>
            {value.toFixed(step < 1 ? 1 : 0)}{suffix}
          </span>
          {isModified && (
            <div className="w-2 h-2 rounded-full bg-primary-400"></div>
          )}
        </div>
      </div>

      <div className="relative">
        {/* Slider Track */}
        <div className="w-full h-2 bg-slate-700 rounded-full">
          {/* Progress Fill */}
          <div 
            className="h-2 bg-gradient-to-r from-primary-500 to-primary-400 rounded-full transition-all duration-200"
            style={{ width: `${percentage}%` }}
          />
        </div>
        
        {/* Slider Input */}
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={(e) => handleChange(Number(e.target.value))}
          className="absolute inset-0 w-full h-2 opacity-0 cursor-pointer"
          role="slider"
          aria-label={label}
        />
        
        {/* Slider Thumb */}
        <div 
          className="absolute top-0 w-4 h-2 -ml-2 transition-all duration-200"
          style={{ left: `${percentage}%` }}
        >
          <div className="w-4 h-4 bg-primary-400 border-2 border-slate-800 rounded-full shadow-lg transform -translate-y-1 hover:scale-110 transition-transform"></div>
        </div>
      </div>

      <div className="flex justify-between text-xs text-slate-500">
        <span>{min}{suffix}</span>
        <span>{max}{suffix}</span>
      </div>

      {validationError && (
        <div className="text-xs text-red-400 mt-1">{validationError}</div>
      )}
    </div>
  );
};

export const ModelSpecificDCFAssumptions: React.FC<ModelSpecificDCFAssumptionsProps> = ({
  modelType,
  assumptions,
  defaults,
  onUpdateAssumption,
  onResetToDefaults,
  sector,
  mode
}) => {
  // Get model-specific configuration
  const modelConfig = DCFModelConfigurations[modelType];
  
  if (!modelConfig || modelConfig.length === 0) {
    return (
      <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700/50">
        <div className="text-center text-slate-400">
          <AlertTriangle className="h-8 w-8 mx-auto mb-2" />
          <div className="text-sm">Configuration not yet implemented for {modelType}</div>
        </div>
      </div>
    );
  }

  // Check for modifications
  const hasModifications = modelConfig.some(config => {
    const currentValue = (assumptions as any)[config.key];
    const defaultValue = (defaults as any)[config.key];
    return currentValue !== undefined && defaultValue !== undefined && 
           Math.abs(currentValue - defaultValue) > 0.01;
  });

  // Get model-specific title and description
  const getModelInfo = () => {
    switch (modelType) {
      case DCFModelType.MULTI_STAGE_SIMPLE:
        return {
          title: '10-Year Multi-Stage DCF (Simple Mode)',
          description: 'Historical validation with GDP blending over 10 years'
        };
      case DCFModelType.MULTI_STAGE_AGENTIC:
        return {
          title: '10-Year Multi-Stage DCF (Agentic Mode)',
          description: 'AI-enhanced analysis with management guidance integration'
        };
      case DCFModelType.BANKING_DCF:
        return {
          title: 'Banking DCF (Excess Return Model)',
          description: 'ROE-based projections with regulatory capital requirements'
        };
      case DCFModelType.PHARMA_DCF:
        return {
          title: 'Pharmaceutical DCF (R&D Pipeline)',
          description: 'R&D-adjusted with patent pipeline and regulatory risk'
        };
      default:
        return {
          title: 'DCF Assumptions',
          description: 'Configure valuation assumptions'
        };
    }
  };

  const modelInfo = getModelInfo();

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className="bg-slate-800/50 rounded-xl p-6 border border-slate-700/50"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-slate-100 mb-1">
            {modelInfo.title}
          </h3>
          <p className="text-sm text-slate-400">
            {modelInfo.description}
          </p>
        </div>
        
        {hasModifications && (
          <motion.button
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            onClick={onResetToDefaults}
            className="flex items-center space-x-2 px-3 py-1.5 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg text-sm transition-colors"
          >
            <RotateCcw className="h-3 w-3" />
            <span>Reset to Defaults</span>
          </motion.button>
        )}
      </div>

      {/* Sector Badge */}
      <div className="mb-6">
        <div className="inline-flex items-center space-x-2 px-3 py-1 bg-primary-500/20 text-primary-300 rounded-full text-sm">
          <div className="w-2 h-2 rounded-full bg-primary-400"></div>
          <span>{sector} Sector</span>
          {mode && (
            <>
              <span className="text-slate-400">•</span>
              <span className="capitalize">{mode} Mode</span>
            </>
          )}
        </div>
      </div>

      {/* Assumption Sliders */}
      <div className="space-y-6">
        {modelConfig.map((config) => {
          const currentValue = (assumptions as any)[config.key];
          const defaultValue = (defaults as any)[config.key];
          const Icon = IconMap[config.icon] || Percent;
          
          if (currentValue === undefined) {
            console.warn(`Missing assumption value for ${config.key} in model ${modelType}`);
            return null;
          }

          return (
            <SliderInput
              key={config.key}
              label={config.label}
              value={currentValue}
              min={config.min}
              max={config.max}
              step={config.step}
              suffix={config.suffix}
              tooltip={getEnhancedTooltip(modelType, config.key, defaults.rationale)}
              onChange={(value) => onUpdateAssumption(config.key, value)}
              defaultValue={defaultValue}
              icon={Icon}
              category={config.category}
            />
          );
        })}
      </div>

      {/* Data Sources Section */}
      {defaults.data_sources && Object.keys(defaults.data_sources).length > 0 && (
        <div className="mt-6 pt-4 border-t border-slate-700">
          <h4 className="text-sm font-medium text-slate-300 mb-2">Data Sources</h4>
          <div className="text-xs text-slate-500 space-y-1">
            {Object.entries(defaults.data_sources).map(([key, source]) => (
              <div key={key} className="flex justify-between">
                <span className="text-slate-400">{key}:</span>
                <span>{source}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Modifications Summary */}
      {hasModifications && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="mt-6 pt-4 border-t border-slate-700"
        >
          <div className="text-xs text-slate-400">
            <span className="text-primary-400 font-medium">
              {modelConfig.filter(config => {
                const currentValue = (assumptions as any)[config.key];
                const defaultValue = (defaults as any)[config.key];
                return currentValue !== undefined && defaultValue !== undefined && 
                       Math.abs(currentValue - defaultValue) > 0.01;
              }).length}
            </span> assumption(s) modified from defaults
          </div>
        </motion.div>
      )}
    </motion.div>
  );
};