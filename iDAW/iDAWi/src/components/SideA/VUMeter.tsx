import React, { useEffect, useState } from 'react';

interface VUMeterProps {
  level: number; // 0.0 to 1.0
  peak?: number;
  height?: string;
}

export const VUMeter: React.FC<VUMeterProps> = ({
  level,
  peak = 0,
  height = 'h-32'
}) => {
  const [peakHold, setPeakHold] = useState(0);

  useEffect(() => {
    if (peak > peakHold) {
      setPeakHold(peak);
      // Reset peak after 1 second
      setTimeout(() => setPeakHold(0), 1000);
    }
  }, [peak, peakHold]);

  // Also use level for peak if peak not provided
  useEffect(() => {
    if (level > peakHold && peak === 0) {
      setPeakHold(level);
      setTimeout(() => setPeakHold(0), 1000);
    }
  }, [level, peakHold, peak]);

  return (
    <div className={`relative ${height} w-3 bg-ableton-bg border border-ableton-border rounded-sm overflow-hidden`}>
      {/* Level bar with gradient */}
      <div
        className="absolute bottom-0 w-full transition-all duration-75 origin-bottom"
        style={{
          height: `${Math.min(level, 1) * 100}%`,
          background: 'linear-gradient(to top, #00ff00 0%, #00ff00 60%, #ffff00 80%, #ff0000 100%)'
        }}
      />

      {/* Peak indicator */}
      {peakHold > 0.1 && (
        <div
          className="absolute w-full h-0.5 bg-ableton-red"
          style={{ bottom: `${peakHold * 100}%` }}
        />
      )}

      {/* Scale marks */}
      {[0.9, 0.7, 0.5, 0.3].map((mark) => (
        <div
          key={mark}
          className="absolute w-full h-px bg-ableton-border opacity-30"
          style={{ bottom: `${mark * 100}%` }}
        />
      ))}
    </div>
  );
};
