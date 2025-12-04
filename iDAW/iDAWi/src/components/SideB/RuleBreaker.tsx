import React from 'react';
import { useStore } from '../../store/useStore';
import { useMusicBrain } from '../../hooks/useMusicBrain';
import { Zap, Music, Sliders, Layout } from 'lucide-react';
import clsx from 'clsx';

interface RuleBreakOption {
  id: string;
  category: 'harmony' | 'rhythm' | 'production' | 'arrangement';
  name: string;
  effect: string;
  icon: React.ReactNode;
}

const RULE_BREAK_OPTIONS: RuleBreakOption[] = [
  {
    id: 'HARMONY_AvoidTonicResolution',
    category: 'harmony',
    name: 'Avoid Tonic Resolution',
    effect: 'Creates unresolved yearning',
    icon: <Music size={16} />,
  },
  {
    id: 'HARMONY_ParallelFifths',
    category: 'harmony',
    name: 'Use Parallel Fifths',
    effect: 'Raw, primal power',
    icon: <Music size={16} />,
  },
  {
    id: 'HARMONY_ModalMixture',
    category: 'harmony',
    name: 'Modal Mixture',
    effect: 'Bittersweet complexity',
    icon: <Music size={16} />,
  },
  {
    id: 'RHYTHM_ConstantDisplacement',
    category: 'rhythm',
    name: 'Constant Displacement',
    effect: 'Anxiety and restlessness',
    icon: <Zap size={16} />,
  },
  {
    id: 'RHYTHM_AgainstTheGrid',
    category: 'rhythm',
    name: 'Against the Grid',
    effect: 'Human imperfection',
    icon: <Zap size={16} />,
  },
  {
    id: 'PRODUCTION_BuriedVocals',
    category: 'production',
    name: 'Buried Vocals',
    effect: 'Dissociation, distance',
    icon: <Sliders size={16} />,
  },
  {
    id: 'PRODUCTION_LoFiHiFi',
    category: 'production',
    name: 'Lo-Fi in Hi-Fi',
    effect: 'Memory, nostalgia',
    icon: <Sliders size={16} />,
  },
  {
    id: 'ARRANGEMENT_EmptySpace',
    category: 'arrangement',
    name: 'Extreme Empty Space',
    effect: 'Isolation, focus',
    icon: <Layout size={16} />,
  },
];

const categoryColors = {
  harmony: 'text-ableton-blue',
  rhythm: 'text-ableton-yellow',
  production: 'text-ableton-green',
  arrangement: 'text-emotion-love',
};

export const RuleBreaker: React.FC = () => {
  const { songIntent, updateSongIntent } = useStore();
  const { suggestRuleBreak, isLoading } = useMusicBrain();

  const handleSelectRule = (ruleId: string) => {
    updateSongIntent({
      ruleToBreak: songIntent.ruleToBreak === ruleId ? null : ruleId,
    });
  };

  const handleSuggest = async () => {
    if (songIntent.coreEmotion) {
      await suggestRuleBreak(songIntent.coreEmotion);
    }
  };

  return (
    <div className="p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="text-xs text-ableton-text-dim">
          Select a rule to intentionally break:
        </div>
        <button
          className="text-xs text-ableton-accent hover:underline disabled:opacity-50 disabled:cursor-not-allowed"
          onClick={handleSuggest}
          disabled={isLoading || !songIntent.coreEmotion}
        >
          {isLoading ? 'Suggesting...' : 'Suggest for emotion'}
        </button>
      </div>

      <div className="grid grid-cols-4 gap-2">
        {RULE_BREAK_OPTIONS.map((rule) => (
          <button
            key={rule.id}
            className={clsx(
              'p-2 rounded border text-left transition-all group',
              songIntent.ruleToBreak === rule.id
                ? 'bg-ableton-accent/20 border-ableton-accent'
                : 'bg-ableton-surface border-ableton-border hover:border-ableton-accent'
            )}
            onClick={() => handleSelectRule(rule.id)}
          >
            <div className="flex items-center gap-1 mb-1">
              <span className={categoryColors[rule.category]}>
                {rule.icon}
              </span>
              <span className="text-xs font-medium truncate">
                {rule.name}
              </span>
            </div>
            <div className="text-xs text-ableton-text-dim truncate">
              {rule.effect}
            </div>
          </button>
        ))}
      </div>

      {songIntent.ruleToBreak && (
        <div className="mt-3 p-2 bg-ableton-surface-light rounded flex items-center gap-2">
          <Zap size={14} className="text-ableton-yellow" />
          <span className="text-sm text-ableton-text">
            Breaking:{' '}
            <span className="text-ableton-accent">
              {RULE_BREAK_OPTIONS.find((r) => r.id === songIntent.ruleToBreak)?.name}
            </span>
          </span>
        </div>
      )}
    </div>
  );
};
