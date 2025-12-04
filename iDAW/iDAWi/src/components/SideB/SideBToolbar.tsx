import React from 'react';
import { FlipHorizontal, Sparkles, Save, RotateCcw } from 'lucide-react';
import { useStore } from '../../store/useStore';
import { useMusicBrain } from '../../hooks/useMusicBrain';

export const SideBToolbar: React.FC = () => {
  const { toggleSide, songIntent, clearSuggestions } = useStore();
  const { processIntent, isLoading } = useMusicBrain();

  const handleGenerate = async () => {
    const result = await processIntent();
    if (result) {
      console.log('Generated:', result);
      // Would apply result to DAW state
    }
  };

  return (
    <div className="h-10 bg-ableton-surface border-b border-ableton-border flex items-center px-2 gap-1">
      {/* Back to DAW */}
      <button
        className="btn-ableton-icon bg-ableton-accent/20 hover:bg-ableton-accent/40"
        title="Back to DAW (⌘E)"
        onClick={toggleSide}
      >
        <FlipHorizontal size={16} className="text-ableton-accent" />
      </button>

      <div className="w-px h-6 bg-ableton-border mx-2" />

      {/* Current Intent Summary */}
      <div className="flex-1 flex items-center gap-2 text-sm">
        <span className="text-ableton-text-dim">Intent:</span>
        {songIntent.coreEmotion ? (
          <>
            <span className="text-ableton-accent capitalize">
              {songIntent.coreEmotion}
            </span>
            {songIntent.subEmotion && (
              <>
                <span className="text-ableton-text-dim">→</span>
                <span className="text-ableton-text capitalize">
                  {songIntent.subEmotion}
                </span>
              </>
            )}
            {songIntent.ruleToBreak && (
              <>
                <span className="text-ableton-text-dim">|</span>
                <span className="text-ableton-yellow text-xs">
                  Breaking: {songIntent.ruleToBreak}
                </span>
              </>
            )}
          </>
        ) : (
          <span className="text-ableton-text-dim italic">No emotion selected</span>
        )}
      </div>

      {/* Actions */}
      <div className="flex items-center gap-1">
        <button
          className="btn-ableton-icon"
          title="Clear Suggestions"
          onClick={clearSuggestions}
        >
          <RotateCcw size={16} />
        </button>

        <button
          className="btn-ableton-icon"
          title="Save Intent"
        >
          <Save size={16} />
        </button>

        <button
          className={`btn-ableton flex items-center gap-2 ${isLoading ? 'opacity-50' : ''}`}
          onClick={handleGenerate}
          disabled={isLoading}
        >
          <Sparkles size={16} />
          {isLoading ? 'Generating...' : 'Generate'}
        </button>
      </div>
    </div>
  );
};
