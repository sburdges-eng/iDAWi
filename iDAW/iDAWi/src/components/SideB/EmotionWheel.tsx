import React, { useState, useEffect } from 'react';
import { useStore } from '../../store/useStore';
import { useMusicBrain } from '../../hooks/useMusicBrain';
import clsx from 'clsx';

interface EmotionCategory {
  name: string;
  color: string;
  emotions: string[];
}

const EMOTION_CATEGORIES: EmotionCategory[] = [
  {
    name: 'Sadness',
    color: 'emotion-grief',
    emotions: ['Grief', 'Yearning', 'Melancholy', 'Loneliness', 'Despair', 'Sorrow'],
  },
  {
    name: 'Joy',
    color: 'emotion-joy',
    emotions: ['Happiness', 'Euphoria', 'Contentment', 'Bliss', 'Elation', 'Delight'],
  },
  {
    name: 'Anger',
    color: 'emotion-anger',
    emotions: ['Rage', 'Frustration', 'Resentment', 'Fury', 'Irritation', 'Wrath'],
  },
  {
    name: 'Fear',
    color: 'emotion-fear',
    emotions: ['Terror', 'Anxiety', 'Dread', 'Panic', 'Unease', 'Paranoia'],
  },
  {
    name: 'Love',
    color: 'emotion-love',
    emotions: ['Devotion', 'Passion', 'Tenderness', 'Adoration', 'Longing', 'Desire'],
  },
  {
    name: 'Hope',
    color: 'emotion-hope',
    emotions: ['Optimism', 'Faith', 'Anticipation', 'Trust', 'Wonder', 'Aspiration'],
  },
];

export const EmotionWheel: React.FC = () => {
  const { songIntent, updateSongIntent } = useStore();
  useMusicBrain(); // Hook for future music brain integration
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [vulnerabilityScale, setVulnerabilityScale] = useState(songIntent.vulnerabilityScale);

  // Find the category for the current emotion
  useEffect(() => {
    for (const category of EMOTION_CATEGORIES) {
      if (category.emotions.some((e) => e.toLowerCase() === songIntent.subEmotion.toLowerCase())) {
        setSelectedCategory(category.name);
        break;
      }
    }
  }, [songIntent.subEmotion]);

  const handleCategorySelect = (category: EmotionCategory) => {
    setSelectedCategory(category.name);
    updateSongIntent({
      coreEmotion: category.name.toLowerCase(),
      subEmotion: category.emotions[0].toLowerCase(),
    });
  };

  const handleEmotionSelect = (emotion: string) => {
    updateSongIntent({
      subEmotion: emotion.toLowerCase(),
    });
  };

  const handleVulnerabilityChange = (value: number) => {
    setVulnerabilityScale(value);
    updateSongIntent({ vulnerabilityScale: value });
  };

  return (
    <div className="space-y-4">
      {/* Emotion Categories (Ring) */}
      <div className="grid grid-cols-3 gap-2">
        {EMOTION_CATEGORIES.map((category) => (
          <button
            key={category.name}
            className={clsx(
              'p-3 rounded-lg border transition-all text-sm font-medium',
              selectedCategory === category.name
                ? `bg-${category.color}/20 border-${category.color} text-${category.color}`
                : 'bg-ableton-surface border-ableton-border hover:border-ableton-accent text-ableton-text-dim'
            )}
            style={{
              backgroundColor: selectedCategory === category.name
                ? `var(--tw-${category.color})`
                : undefined,
            }}
            onClick={() => handleCategorySelect(category)}
          >
            {category.name}
          </button>
        ))}
      </div>

      {/* Sub-emotions */}
      {selectedCategory && (
        <div className="mt-4">
          <div className="text-xs text-ableton-text-dim uppercase mb-2">
            {selectedCategory} Spectrum
          </div>
          <div className="grid grid-cols-2 gap-2">
            {EMOTION_CATEGORIES.find((c) => c.name === selectedCategory)?.emotions.map((emotion) => (
              <button
                key={emotion}
                className={clsx(
                  'p-2 rounded border text-sm transition-all',
                  songIntent.subEmotion.toLowerCase() === emotion.toLowerCase()
                    ? 'bg-ableton-accent border-ableton-accent text-black font-medium'
                    : 'bg-ableton-surface border-ableton-border hover:border-ableton-accent text-ableton-text'
                )}
                onClick={() => handleEmotionSelect(emotion)}
              >
                {emotion}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Vulnerability Scale */}
      <div className="mt-6 pt-4 border-t border-ableton-border">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs text-ableton-text-dim uppercase">
            Vulnerability Scale
          </span>
          <span className="text-sm font-mono text-ableton-accent">
            {vulnerabilityScale}/10
          </span>
        </div>
        <input
          type="range"
          min={1}
          max={10}
          value={vulnerabilityScale}
          onChange={(e) => handleVulnerabilityChange(parseInt(e.target.value))}
          className="w-full"
        />
        <div className="flex justify-between text-xs text-ableton-text-dim mt-1">
          <span>Guarded</span>
          <span>Raw</span>
        </div>
      </div>

      {/* Narrative Arc */}
      <div className="mt-4">
        <div className="text-xs text-ableton-text-dim uppercase mb-2">
          Narrative Arc
        </div>
        <div className="grid grid-cols-2 gap-2">
          {(['ascending', 'descending', 'circular', 'static'] as const).map((arc) => (
            <button
              key={arc}
              className={clsx(
                'p-2 rounded border text-sm capitalize transition-all',
                songIntent.narrativeArc === arc
                  ? 'bg-ableton-accent border-ableton-accent text-black font-medium'
                  : 'bg-ableton-surface border-ableton-border hover:border-ableton-accent text-ableton-text'
              )}
              onClick={() => updateSongIntent({ narrativeArc: arc })}
            >
              {arc === 'ascending' && '↗ '}
              {arc === 'descending' && '↘ '}
              {arc === 'circular' && '↻ '}
              {arc === 'static' && '→ '}
              {arc}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
