import React, { useState } from 'react';
import { EmotionWheel } from './EmotionWheel';
import { Interrogator } from './Interrogator';
import { GhostWriter } from './GhostWriter';

export const SideB: React.FC = () => {
  const [selectedEmotion, setSelectedEmotion] = useState<string | null>(null);
  const [completedIntent, setCompletedIntent] = useState<Record<string, unknown> | null>(null);

  const handleEmotionSelect = (emotion: string) => {
    setSelectedEmotion(emotion);
    setCompletedIntent(null); // Reset intent when emotion changes
  };

  const handleIntentComplete = (intent: Record<string, unknown>) => {
    setCompletedIntent(intent);
  };

  return (
    <div className="h-screen flex flex-col overflow-hidden bg-ableton-bg">
      {/* Header */}
      <div className="h-12 bg-ableton-surface border-b border-ableton-border flex items-center px-4">
        <h1 className="text-lg font-bold">iDAWi</h1>
        <span className="text-ableton-text-dim text-sm ml-2">Side B: Emotion</span>
        {selectedEmotion && (
          <span className="ml-auto text-sm">
            Feeling: <span className="text-ableton-accent font-medium">{selectedEmotion}</span>
          </span>
        )}
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        <div className="grid grid-cols-2 h-full">
          {/* Left Column - Emotion Selection & Interrogation */}
          <div className="flex flex-col overflow-auto border-r border-ableton-border">
            <EmotionWheel onSelectEmotion={handleEmotionSelect} />
            <div className="border-t border-ableton-border">
              <Interrogator
                emotion={selectedEmotion}
                onComplete={handleIntentComplete}
              />
            </div>
          </div>

          {/* Right Column - Ghost Writer */}
          <div className="overflow-auto">
            <GhostWriter
              emotion={selectedEmotion}
              intent={completedIntent}
            />
          </div>
        </div>
      </div>
    </div>
  );
};
