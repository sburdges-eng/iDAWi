import React from 'react';
import { Timeline } from './Timeline';
import { Mixer } from './Mixer';
import { Transport } from './Transport';

export const SideA: React.FC = () => {
  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <div className="h-12 bg-ableton-surface border-b border-ableton-border flex items-center px-4">
        <h1 className="text-lg font-bold">iDAWi</h1>
        <span className="text-ableton-text-dim text-sm ml-2">Side A: Professional</span>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Timeline */}
        <div className="flex-1 flex flex-col">
          <Timeline />
          <Transport />
        </div>

        {/* Mixer */}
        <div className="w-80">
          <Mixer />
        </div>
      </div>
    </div>
  );
};
