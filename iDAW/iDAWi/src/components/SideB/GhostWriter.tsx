import React, { useState } from 'react';
import { useStore } from '../../store/useStore';
import { useMusicBrain } from '../../hooks/useMusicBrain';
import {
  Sparkles,
  Check,
  Music,
  Zap,
  Sliders,
  Layout,
  Loader2,
} from 'lucide-react';
import clsx from 'clsx';

const categoryIcons = {
  harmony: <Music size={16} />,
  rhythm: <Zap size={16} />,
  production: <Sliders size={16} />,
  arrangement: <Layout size={16} />,
};

const categoryColors = {
  harmony: 'border-ableton-blue',
  rhythm: 'border-ableton-yellow',
  production: 'border-ableton-green',
  arrangement: 'border-emotion-love',
};

export const GhostWriter: React.FC = () => {
  const {
    ghostWriterSuggestions,
    applySuggestion,
    songIntent,
  } = useStore();
  const { suggestRuleBreak, isLoading } = useMusicBrain();
  const [activeTab, setActiveTab] = useState<'suggestions' | 'applied'>('suggestions');

  const handleGenerate = async () => {
    // Generate suggestions based on current intent
    await suggestRuleBreak(songIntent.coreEmotion);
  };

  const pendingSuggestions = ghostWriterSuggestions.filter((s) => !s.applied);
  const appliedSuggestions = ghostWriterSuggestions.filter((s) => s.applied);

  return (
    <div className="p-4 h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Sparkles size={18} className="text-ableton-accent" />
          <span className="font-medium">Ghost Writer</span>
        </div>
        <button
          className={clsx(
            'btn-ableton flex items-center gap-2',
            isLoading && 'opacity-50'
          )}
          onClick={handleGenerate}
          disabled={isLoading}
        >
          {isLoading ? (
            <Loader2 size={14} className="animate-spin" />
          ) : (
            <Sparkles size={14} />
          )}
          Generate Ideas
        </button>
      </div>

      {/* Philosophy Quote */}
      <div className="p-3 bg-ableton-surface rounded mb-4 text-sm italic text-ableton-text-dim">
        {'"The tool shouldn\'t finish art for people. It should make them braver."'}
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-4">
        <button
          className={clsx(
            'px-3 py-1 rounded text-sm transition-colors',
            activeTab === 'suggestions'
              ? 'bg-ableton-accent text-black'
              : 'bg-ableton-surface hover:bg-ableton-surface-light'
          )}
          onClick={() => setActiveTab('suggestions')}
        >
          Suggestions ({pendingSuggestions.length})
        </button>
        <button
          className={clsx(
            'px-3 py-1 rounded text-sm transition-colors',
            activeTab === 'applied'
              ? 'bg-ableton-accent text-black'
              : 'bg-ableton-surface hover:bg-ableton-surface-light'
          )}
          onClick={() => setActiveTab('applied')}
        >
          Applied ({appliedSuggestions.length})
        </button>
      </div>

      {/* Suggestions List */}
      <div className="flex-1 overflow-auto space-y-2">
        {activeTab === 'suggestions' && (
          <>
            {pendingSuggestions.length === 0 ? (
              <div className="text-center py-8 text-ableton-text-dim">
                <Sparkles size={24} className="mx-auto mb-2 opacity-50" />
                <p>No suggestions yet.</p>
                <p className="text-sm">Click &quot;Generate Ideas&quot; to get started.</p>
              </div>
            ) : (
              pendingSuggestions.map((suggestion) => (
                <SuggestionCard
                  key={suggestion.id}
                  suggestion={suggestion}
                  onApply={() => applySuggestion(suggestion.id)}
                />
              ))
            )}
          </>
        )}

        {activeTab === 'applied' && (
          <>
            {appliedSuggestions.length === 0 ? (
              <div className="text-center py-8 text-ableton-text-dim">
                <Check size={24} className="mx-auto mb-2 opacity-50" />
                <p>No applied suggestions yet.</p>
              </div>
            ) : (
              appliedSuggestions.map((suggestion) => (
                <div
                  key={suggestion.id}
                  className="p-3 bg-ableton-surface rounded border-l-2 border-ableton-green"
                >
                  <div className="flex items-center gap-2 mb-1">
                    <Check size={14} className="text-ableton-green" />
                    <span className="text-sm font-medium">{suggestion.description}</span>
                  </div>
                  <p className="text-xs text-ableton-text-dim">
                    {suggestion.emotionalRationale}
                  </p>
                </div>
              ))
            )}
          </>
        )}
      </div>

      {/* Current Intent Summary */}
      <div className="mt-4 pt-4 border-t border-ableton-border">
        <div className="text-xs text-ableton-text-dim uppercase mb-2">
          Current Emotional Intent
        </div>
        <div className="flex flex-wrap gap-2">
          <span className="px-2 py-1 bg-ableton-surface rounded text-xs">
            {songIntent.coreEmotion}
          </span>
          <span className="px-2 py-1 bg-ableton-surface rounded text-xs">
            {songIntent.subEmotion}
          </span>
          <span className="px-2 py-1 bg-ableton-surface rounded text-xs">
            Arc: {songIntent.narrativeArc}
          </span>
          <span className="px-2 py-1 bg-ableton-surface rounded text-xs">
            Vulnerability: {songIntent.vulnerabilityScale}/10
          </span>
          {songIntent.ruleToBreak && (
            <span className="px-2 py-1 bg-ableton-yellow/20 text-ableton-yellow rounded text-xs">
              Breaking: {songIntent.ruleToBreak.split('_').pop()}
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

interface SuggestionCardProps {
  suggestion: {
    id: string;
    type: 'harmony' | 'rhythm' | 'production' | 'arrangement';
    description: string;
    emotionalRationale: string;
  };
  onApply: () => void;
}

const SuggestionCard: React.FC<SuggestionCardProps> = ({ suggestion, onApply }) => {
  return (
    <div
      className={clsx(
        'ghost-writer-suggestion border-l-2',
        categoryColors[suggestion.type]
      )}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-ableton-text-dim">
              {categoryIcons[suggestion.type]}
            </span>
            <span className="text-xs uppercase text-ableton-text-dim">
              {suggestion.type}
            </span>
          </div>
          <p className="text-sm font-medium mb-1">{suggestion.description}</p>
          <p className="text-xs text-ableton-text-dim">
            {suggestion.emotionalRationale}
          </p>
        </div>
        <button
          className="p-2 bg-ableton-accent/20 hover:bg-ableton-accent/40 rounded transition-colors"
          onClick={onApply}
          title="Apply this suggestion"
        >
          <Check size={16} className="text-ableton-accent" />
        </button>
      </div>
    </div>
  );
};
