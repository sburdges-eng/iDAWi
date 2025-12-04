import React, { useState, useRef, useEffect } from 'react';

interface KnobProps {
  value: number; // 0.0 to 1.0
  onChange: (value: number) => void;
  label?: string;
  min?: number;
  max?: number;
}

export const Knob: React.FC<KnobProps> = ({
  value,
  onChange,
  label,
  min = 0,
  max = 1
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const knobRef = useRef<HTMLDivElement>(null);
  const startY = useRef(0);
  const startValue = useRef(0);

  const normalizedValue = (value - min) / (max - min);
  const rotation = -135 + (normalizedValue * 270); // -135 to +135

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    startY.current = e.clientY;
    startValue.current = value;
  };

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging) return;

      const deltaY = startY.current - e.clientY;
      const sensitivity = 0.01;
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

  return (
    <div className="flex flex-col items-center gap-1">
      <div
        ref={knobRef}
        className="knob"
        onMouseDown={handleMouseDown}
      >
        <div
          className="knob-indicator"
          style={{ transform: `translateX(-50%) rotate(${rotation}deg)` }}
        />
      </div>
      {label && (
        <span className="text-xs text-ableton-text-dim">{label}</span>
      )}
    </div>
  );
};
