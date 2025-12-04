import React from 'react';
import { Transport } from './Transport';
import { Timeline } from './Timeline';
import { Mixer } from './Mixer';
import { Toolbar } from './Toolbar';

export const SideA: React.FC = () => {
  return (
    <div className="w-full h-full flex flex-col bg-ableton-bg">
      {/* Top Toolbar */}
      <Toolbar />

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Timeline Area */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <Timeline />
        </div>

        {/* Mixer Panel (collapsible) */}
        <Mixer />
      </div>

      {/* Transport Bar */}
      <Transport />
    </div>
  );
};
