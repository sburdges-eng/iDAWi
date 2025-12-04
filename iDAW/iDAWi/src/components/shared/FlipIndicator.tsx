import React from 'react';
import { useStore } from '../../store/useStore';
import { FlipHorizontal } from 'lucide-react';
import clsx from 'clsx';

export const FlipIndicator: React.FC = () => {
  const { currentSide, toggleSide, isFlipping } = useStore();

  return (
    <div className="fixed bottom-20 right-4 z-50">
      <button
        className={clsx(
          'flex items-center gap-2 px-3 py-2 rounded-lg transition-all',
          'bg-ableton-surface border border-ableton-border',
          'hover:bg-ableton-surface-light hover:border-ableton-accent',
          isFlipping && 'animate-pulse'
        )}
        onClick={toggleSide}
        title={`Switch to Side ${currentSide === 'A' ? 'B (Emotion)' : 'A (DAW)'} (⌘E)`}
      >
        <FlipHorizontal
          size={18}
          className={clsx(
            'transition-transform',
            currentSide === 'B' && 'rotate-180'
          )}
        />
        <div className="text-sm">
          <span className="text-ableton-text-dim">Side</span>{' '}
          <span
            className={clsx(
              'font-bold',
              currentSide === 'A' ? 'text-ableton-accent' : 'text-emotion-love'
            )}
          >
            {currentSide}
          </span>
        </div>
        <div className="text-xs text-ableton-text-dim">
          {currentSide === 'A' ? 'DAW' : 'Emotion'}
        </div>
      </button>

      {/* Keyboard shortcut hint */}
      <div className="text-xs text-ableton-text-dim text-center mt-1">
        ⌘E to flip
      </div>
    </div>
  );
};
