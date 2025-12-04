import React, { useEffect, useState } from 'react';
import { useMusicBrain } from '../../hooks/useMusicBrain';

interface Emotion {
  name: string;
  category: string;
  intensity: number;
}

interface EmotionWheelProps {
  onSelectEmotion: (emotion: string) => void;
}

export const EmotionWheel: React.FC<EmotionWheelProps> = ({ onSelectEmotion }) => {
  const [emotions, setEmotions] = useState<Emotion[]>([]);
  const [selectedEmotion, setSelectedEmotion] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const { getEmotions } = useMusicBrain();

  useEffect(() => {
    setIsLoading(true);
    getEmotions()
      .then(setEmotions)
      .finally(() => setIsLoading(false));
  }, []);

  const handleSelect = (emotion: string) => {
    setSelectedEmotion(emotion);
    onSelectEmotion(emotion);
  };

  const categoryColors: Record<string, string> = {
    'Sadness': 'bg-emotion-grief',
    'Happiness': 'bg-emotion-joy',
    'Anger': 'bg-emotion-anger',
    'Fear': 'bg-emotion-fear',
    'Love': 'bg-emotion-love',
  };

  const categoryHoverColors: Record<string, string> = {
    'Sadness': 'hover:border-blue-500',
    'Happiness': 'hover:border-yellow-500',
    'Anger': 'hover:border-red-500',
    'Fear': 'hover:border-purple-500',
    'Love': 'hover:border-pink-500',
  };

  if (isLoading) {
    return (
      <div className="p-6">
        <h2 className="text-xl font-bold mb-4">What are you feeling?</h2>
        <div className="grid grid-cols-3 gap-3">
          {[...Array(9)].map((_, i) => (
            <div
              key={i}
              className="p-4 rounded border border-ableton-border animate-pulse bg-ableton-surface"
            >
              <div className="w-3 h-3 rounded-full bg-ableton-border mb-2" />
              <div className="h-4 bg-ableton-border rounded w-3/4 mb-1" />
              <div className="h-3 bg-ableton-border rounded w-1/2" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold mb-4">What are you feeling?</h2>
      <p className="text-ableton-text-dim text-sm mb-6">
        Select an emotion to begin the interrogation process
      </p>

      <div className="grid grid-cols-3 gap-3">
        {emotions.map((emotion) => (
          <button
            key={emotion.name}
            onClick={() => handleSelect(emotion.name)}
            className={`
              p-4 rounded border transition-all text-left
              ${selectedEmotion === emotion.name
                ? 'border-ableton-accent bg-ableton-accent bg-opacity-20 scale-105'
                : `border-ableton-border hover:bg-ableton-surface ${categoryHoverColors[emotion.category] || ''}`
              }
            `}
          >
            <div
              className={`w-3 h-3 rounded-full mb-2 ${categoryColors[emotion.category] || 'bg-ableton-text-dim'}`}
              style={{ opacity: 0.5 + emotion.intensity * 0.5 }}
            />
            <div className="text-sm font-medium">{emotion.name}</div>
            <div className="text-xs text-ableton-text-dim">{emotion.category}</div>
          </button>
        ))}
      </div>
    </div>
  );
};
