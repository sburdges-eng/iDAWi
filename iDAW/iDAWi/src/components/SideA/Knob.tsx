import React, { useState, useRef, useEffect } from 'react';
import clsx from 'clsx';

interface KnobProps {
  value: number;
  onChange: (value: number) => void;
  label?: string;
  min?: number;
  max?: number;
  size?: 'sm' | 'md' | 'lg';
  showValue?: boolean;
  formatValue?: (value: number) => string;
}

export const Knob: React.FC<KnobProps> = ({
  value,
  onChange,
  label,
  min = 0,
  max = 1,
  size = 'md',
  showValue = false,
  formatValue,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const knobRef = useRef<HTMLDivElement>(null);
  const startY = useRef(0);
  const startValue = useRef(0);

  const normalizedValue = (value - min) / (max - min);
  const rotation = -135 + (normalizedValue * 270); // -135 to +135

  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-10 h-10',
    lg: 'w-12 h-12',
  };

  const indicatorClasses = {
    sm: 'h-2 top-0.5',
    md: 'h-3 top-1',
    lg: 'h-4 top-1.5',
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsDragging(true);
    startY.current = e.clientY;
    startValue.current = value;
  };

  // Double-click to reset to center/default
  const handleDoubleClick = () => {
    const centerValue = (min + max) / 2;
    onChange(centerValue);
  };

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging) return;

      const deltaY = startY.current - e.clientY;
      const sensitivity = (max - min) / 100; // 100px for full range
      const newValue = Math.max(min, Math.min(max, startValue.current + deltaY * sensitivity));

      onChange(newValue);
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, min, max, onChange]);

  const displayValue = formatValue
    ? formatValue(value)
    : value === 0
      ? 'C'
      : value < 0
        ? `L${Math.abs(Math.round(value * 50))}`
        : `R${Math.round(value * 50)}`;

  return (
    <div className="flex flex-col items-center gap-1">
      {label && (
        <span className="text-[10px] text-ableton-text-dim uppercase tracking-wide">
          {label}
        </span>
      )}
      <div
        ref={knobRef}
        className={clsx(
          'knob cursor-pointer select-none',
          sizeClasses[size],
          isDragging && 'border-ableton-accent'
        )}
        onMouseDown={handleMouseDown}
        onDoubleClick={handleDoubleClick}
        title="Drag up/down to adjust. Double-click to reset."
      >
        <div
          className={clsx(
            'knob-indicator',
            indicatorClasses[size]
          )}
          style={{ transform: `translateX(-50%) rotate(${rotation}deg)` }}
        />
      </div>
      {showValue && (
        <span className="text-[10px] text-ableton-text-dim font-mono">
          {displayValue}
        </span>
      )}
    </div>
  );
};
