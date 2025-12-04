import React, { useEffect, useState } from 'react';

interface VUMeterProps {
  level: number; // 0.0 to 1.0
  peak?: number;
}

export const VUMeter: React.FC<VUMeterProps> = ({ level, peak = 0 }) => {
  const [peakHold, setPeakHold] = useState(0);

  useEffect(() => {
    if (peak > peakHold) {
      setPeakHold(peak);
      // Reset peak after 1 second
      setTimeout(() => setPeakHold(0), 1000);
    }
  }, [peak, peakHold]);

  const getColor = (value: number) => {
    if (value > 0.9) return 'bg-ableton-red';
    if (value > 0.7) return 'bg-ableton-yellow';
    return 'bg-ableton-green';
  };

  return (
    <div className="relative h-32 w-4 bg-ableton-bg border border-ableton-border rounded overflow-hidden">
      {/* Level bar */}
      <div
        className={`absolute bottom-0 w-full transition-all duration-75 ${getColor(level)}`}
        style={{ height: `${level * 100}%` }}
      />

      {/* Peak indicator */}
      {peakHold > 0 && (
        <div
          className="absolute w-full h-1 bg-ableton-red"
          style={{ bottom: `${peakHold * 100}%` }}
        />
      )}

      {/* Scale marks */}
      {[0.9, 0.7, 0.5, 0.3].map((mark) => (
        <div
          key={mark}
          className="absolute w-full h-px bg-ableton-border opacity-50"
          style={{ bottom: `${mark * 100}%` }}
        />
      ))}
    </div>
  );
};
