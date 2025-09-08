import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Info, X, HelpCircle } from 'lucide-react';

interface TouchFriendlyTooltipProps {
  content: React.ReactNode;
  title?: string;
  children: React.ReactNode;
  placement?: 'top' | 'bottom' | 'left' | 'right' | 'auto';
  trigger?: 'hover' | 'click' | 'longpress' | 'both';
  showOnFocus?: boolean;
  delay?: number;
  longPressDelay?: number;
  className?: string;
  tooltipClassName?: string;
  maxWidth?: string;
  disabled?: boolean;
}

export const TouchFriendlyTooltip: React.FC<TouchFriendlyTooltipProps> = ({
  content,
  title,
  children,
  placement = 'auto',
  trigger = 'both',
  showOnFocus = true,
  delay = 300,
  longPressDelay = 600,
  className = '',
  tooltipClassName = '',
  maxWidth = '320px',
  disabled = false
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [actualPlacement, setActualPlacement] = useState<'top' | 'bottom' | 'left' | 'right'>('top');
  const [longPressTimer, setLongPressTimer] = useState<NodeJS.Timeout | null>(null);
  const [isLongPressing, setIsLongPressing] = useState(false);
  
  const triggerRef = useRef<HTMLDivElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);
  const showTimer = useRef<NodeJS.Timeout | null>(null);
  const hideTimer = useRef<NodeJS.Timeout | null>(null);

  // Calculate optimal placement
  const calculatePlacement = (): 'top' | 'bottom' | 'left' | 'right' => {
    if (placement !== 'auto' || !triggerRef.current) {
      return placement as 'top' | 'bottom' | 'left' | 'right';
    }

    const rect = triggerRef.current.getBoundingClientRect();
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    
    const spaceTop = rect.top;
    const spaceBottom = viewportHeight - rect.bottom;
    const spaceLeft = rect.left;
    const spaceRight = viewportWidth - rect.right;

    // Prefer top/bottom for better mobile experience
    if (spaceTop >= 150) return 'top';
    if (spaceBottom >= 150) return 'bottom';
    if (spaceRight >= 200) return 'right';
    if (spaceLeft >= 200) return 'left';
    
    // Fallback to side with most space
    return spaceBottom > spaceTop ? 'bottom' : 'top';
  };

  // Show tooltip
  const showTooltip = () => {
    if (disabled) return;
    
    if (hideTimer.current) {
      clearTimeout(hideTimer.current);
      hideTimer.current = null;
    }

    showTimer.current = setTimeout(() => {
      setActualPlacement(calculatePlacement());
      setIsVisible(true);
    }, delay);
  };

  // Hide tooltip
  const hideTooltip = () => {
    if (showTimer.current) {
      clearTimeout(showTimer.current);
      showTimer.current = null;
    }

    hideTimer.current = setTimeout(() => {
      setIsVisible(false);
    }, 100);
  };

  // Immediate hide (for clicks outside)
  const hideTooltipImmediate = () => {
    if (showTimer.current) {
      clearTimeout(showTimer.current);
      showTimer.current = null;
    }
    if (hideTimer.current) {
      clearTimeout(hideTimer.current);
      hideTimer.current = null;
    }
    setIsVisible(false);
  };

  // Long press handlers
  const handleTouchStart = (e: React.TouchEvent) => {
    if (trigger === 'hover') return;
    
    e.preventDefault();
    setIsLongPressing(true);
    
    const timer = setTimeout(() => {
      showTooltip();
      setIsLongPressing(false);
    }, longPressDelay);
    
    setLongPressTimer(timer);
  };

  const handleTouchEnd = () => {
    if (longPressTimer) {
      clearTimeout(longPressTimer);
      setLongPressTimer(null);
    }
    setIsLongPressing(false);
  };

  // Mouse handlers
  const handleMouseEnter = () => {
    if (trigger === 'click' || trigger === 'longpress') return;
    showTooltip();
  };

  const handleMouseLeave = () => {
    if (trigger === 'click' || trigger === 'longpress') return;
    hideTooltip();
  };

  // Click handlers
  const handleClick = (e: React.MouseEvent) => {
    if (trigger === 'hover' || trigger === 'longpress') return;
    
    e.stopPropagation();
    if (isVisible) {
      hideTooltipImmediate();
    } else {
      showTooltip();
    }
  };

  // Focus handlers
  const handleFocus = () => {
    if (showOnFocus && (trigger === 'both' || trigger === 'hover')) {
      showTooltip();
    }
  };

  const handleBlur = () => {
    if (showOnFocus) {
      hideTooltip();
    }
  };

  // Click outside handler
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent | TouchEvent) => {
      if (
        isVisible &&
        triggerRef.current &&
        tooltipRef.current &&
        !triggerRef.current.contains(event.target as Node) &&
        !tooltipRef.current.contains(event.target as Node)
      ) {
        hideTooltipImmediate();
      }
    };

    if (isVisible) {
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('touchstart', handleClickOutside, { passive: true });
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('touchstart', handleClickOutside);
    };
  }, [isVisible]);

  // Cleanup timers
  useEffect(() => {
    return () => {
      if (showTimer.current) clearTimeout(showTimer.current);
      if (hideTimer.current) clearTimeout(hideTimer.current);
      if (longPressTimer) clearTimeout(longPressTimer);
    };
  }, [longPressTimer]);

  // Get tooltip positioning styles
  const getTooltipStyles = () => {
    const base = 'absolute z-50';
    
    switch (actualPlacement) {
      case 'top':
        return `${base} bottom-full left-1/2 transform -translate-x-1/2 mb-2`;
      case 'bottom':
        return `${base} top-full left-1/2 transform -translate-x-1/2 mt-2`;
      case 'left':
        return `${base} right-full top-1/2 transform -translate-y-1/2 mr-2`;
      case 'right':
        return `${base} left-full top-1/2 transform -translate-y-1/2 ml-2`;
      default:
        return `${base} bottom-full left-1/2 transform -translate-x-1/2 mb-2`;
    }
  };

  // Get arrow positioning styles
  const getArrowStyles = () => {
    const base = 'absolute w-2 h-2 bg-slate-800 border border-slate-600';
    
    switch (actualPlacement) {
      case 'top':
        return `${base} top-full left-1/2 transform -translate-x-1/2 rotate-45 -mt-1 border-t-0 border-l-0`;
      case 'bottom':
        return `${base} bottom-full left-1/2 transform -translate-x-1/2 rotate-45 -mb-1 border-b-0 border-r-0`;
      case 'left':
        return `${base} left-full top-1/2 transform -translate-y-1/2 rotate-45 -ml-1 border-l-0 border-b-0`;
      case 'right':
        return `${base} right-full top-1/2 transform -translate-y-1/2 rotate-45 -mr-1 border-r-0 border-t-0`;
      default:
        return `${base} top-full left-1/2 transform -translate-x-1/2 rotate-45 -mt-1 border-t-0 border-l-0`;
    }
  };

  return (
    <div 
      ref={triggerRef}
      className={`relative inline-block ${className}`}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onTouchStart={handleTouchStart}
      onTouchEnd={handleTouchEnd}
      onTouchCancel={handleTouchEnd}
      onClick={handleClick}
      onFocus={handleFocus}
      onBlur={handleBlur}
    >
      {children}
      
      <AnimatePresence>
        {isVisible && (
          <motion.div
            ref={tooltipRef}
            initial={{ opacity: 0, scale: 0.95, y: actualPlacement === 'top' ? 10 : -10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: actualPlacement === 'top' ? 10 : -10 }}
            transition={{ duration: 0.15, ease: 'easeOut' }}
            className={getTooltipStyles()}
            style={{ maxWidth }}
          >
            {/* Tooltip Content */}
            <div className={`
              bg-slate-800 border border-slate-600 rounded-lg shadow-2xl overflow-hidden
              ${tooltipClassName}
            `}>
              {/* Header with close button for mobile */}
              {(title || trigger === 'click' || trigger === 'longpress') && (
                <div className="flex items-center justify-between p-3 border-b border-slate-700 bg-slate-750">
                  {title && (
                    <div className="font-medium text-slate-200 text-sm">
                      {title}
                    </div>
                  )}
                  {(trigger === 'click' || trigger === 'longpress') && (
                    <button
                      onClick={hideTooltipImmediate}
                      className="p-1 hover:bg-slate-600 rounded transition-colors ml-2"
                      aria-label="Close tooltip"
                    >
                      <X className="h-3 w-3 text-slate-400" />
                    </button>
                  )}
                </div>
              )}
              
              {/* Content */}
              <div className="p-3 text-sm text-slate-300 leading-relaxed">
                {content}
              </div>
            </div>
            
            {/* Arrow */}
            <div className={getArrowStyles()} />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Long press indicator */}
      <AnimatePresence>
        {isLongPressing && trigger !== 'hover' && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            className="absolute inset-0 bg-primary-500/20 rounded-full pointer-events-none"
          />
        )}
      </AnimatePresence>
    </div>
  );
};

// Educational tooltip specifically for DCF concepts
export const DCFEducationalTooltip: React.FC<{
  concept: string;
  children: React.ReactNode;
  className?: string;
}> = ({ concept, children, className }) => {
  // Educational content mapping (you can expand this)
  const educationalContent: { [key: string]: { title: string; content: React.ReactNode } } = {
    'dcf': {
      title: 'Discounted Cash Flow',
      content: (
        <div className="space-y-2">
          <p>DCF estimates a company's intrinsic value by:</p>
          <ul className="list-disc list-inside space-y-1 text-xs">
            <li>Projecting future cash flows</li>
            <li>Discounting them to present value</li>
            <li>Adding terminal value</li>
          </ul>
        </div>
      )
    },
    'wacc': {
      title: 'Weighted Average Cost of Capital',
      content: (
        <div className="space-y-2">
          <p>WACC represents the average cost of financing, considering:</p>
          <ul className="list-disc list-inside space-y-1 text-xs">
            <li>Cost of equity (shareholder returns)</li>
            <li>Cost of debt (interest rates)</li>
            <li>Tax benefits of debt</li>
          </ul>
        </div>
      )
    },
    'terminal_value': {
      title: 'Terminal Value',
      content: (
        <div className="space-y-2">
          <p>Value beyond the projection period, typically calculated using:</p>
          <ul className="list-disc list-inside space-y-1 text-xs">
            <li>Perpetual growth method</li>
            <li>Exit multiple method</li>
          </ul>
          <p className="text-xs text-slate-400">Often 60-80% of total value</p>
        </div>
      )
    }
  };

  const content = educationalContent[concept];
  
  if (!content) {
    return <>{children}</>;
  }

  return (
    <TouchFriendlyTooltip
      title={content.title}
      content={content.content}
      placement="auto"
      trigger="both"
      className={className}
      longPressDelay={500}
    >
      {children}
    </TouchFriendlyTooltip>
  );
};

// Info icon tooltip for help text
export const InfoTooltip: React.FC<{
  content: React.ReactNode;
  title?: string;
  placement?: 'top' | 'bottom' | 'left' | 'right' | 'auto';
  className?: string;
}> = ({ content, title, placement = 'auto', className = '' }) => {
  return (
    <TouchFriendlyTooltip
      content={content}
      title={title}
      placement={placement}
      trigger="both"
      className={className}
    >
      <Info className="h-4 w-4 text-slate-400 cursor-help hover:text-primary-400 transition-colors" />
    </TouchFriendlyTooltip>
  );
};

// Help circle tooltip for questions
export const HelpTooltip: React.FC<{
  content: React.ReactNode;
  title?: string;
  placement?: 'top' | 'bottom' | 'left' | 'right' | 'auto';
  className?: string;
}> = ({ content, title, placement = 'auto', className = '' }) => {
  return (
    <TouchFriendlyTooltip
      content={content}
      title={title}
      placement={placement}
      trigger="both"
      className={className}
    >
      <HelpCircle className="h-4 w-4 text-slate-400 cursor-help hover:text-primary-400 transition-colors" />
    </TouchFriendlyTooltip>
  );
};

// Mobile-optimized tooltip for touch devices
export const MobileTooltip: React.FC<{
  content: React.ReactNode;
  title?: string;
  children: React.ReactNode;
  className?: string;
}> = ({ content, title, children, className }) => {
  return (
    <TouchFriendlyTooltip
      content={content}
      title={title}
      placement="auto"
      trigger="longpress"
      longPressDelay={400}
      maxWidth="280px"
      className={className}
    >
      {children}
    </TouchFriendlyTooltip>
  );
};