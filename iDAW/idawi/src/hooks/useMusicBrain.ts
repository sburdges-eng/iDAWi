// Music Brain integration hook
// In production, this would use Tauri's invoke to call Python
import React from 'react';

interface Emotion {
  name: string;
  category: string;
  intensity: number;
}

interface RuleBreakSuggestion {
  rule: string;
  effect: string;
  use_when: string;
  justification: string;
}

interface ProcessIntentResult {
  harmony: string[];
  tempo: number;
  key: string;
  mixer_params: Record<string, number | string>;
}

// Default emotions for when Music Brain is not available
const defaultEmotions: Emotion[] = [
  { name: 'Grief', category: 'Sadness', intensity: 0.9 },
  { name: 'Melancholy', category: 'Sadness', intensity: 0.6 },
  { name: 'Longing', category: 'Sadness', intensity: 0.7 },
  { name: 'Joy', category: 'Happiness', intensity: 0.8 },
  { name: 'Euphoria', category: 'Happiness', intensity: 1.0 },
  { name: 'Contentment', category: 'Happiness', intensity: 0.5 },
  { name: 'Rage', category: 'Anger', intensity: 1.0 },
  { name: 'Frustration', category: 'Anger', intensity: 0.6 },
  { name: 'Resentment', category: 'Anger', intensity: 0.7 },
  { name: 'Terror', category: 'Fear', intensity: 1.0 },
  { name: 'Anxiety', category: 'Fear', intensity: 0.6 },
  { name: 'Dread', category: 'Fear', intensity: 0.8 },
  { name: 'Passion', category: 'Love', intensity: 0.9 },
  { name: 'Tenderness', category: 'Love', intensity: 0.5 },
  { name: 'Devotion', category: 'Love', intensity: 0.8 },
];

// Rule-breaking suggestions based on emotions
const ruleBreakingDatabase: Record<string, RuleBreakSuggestion[]> = {
  Grief: [
    {
      rule: 'HARMONY_AvoidTonicResolution',
      effect: 'Creates unresolved yearning that mirrors emotional state',
      use_when: 'The listener should feel the loss is still unprocessed',
      justification: 'Grief rarely resolves cleanly. Music that refuses resolution honors that truth.',
    },
    {
      rule: 'ARRANGEMENT_BuriedVocals',
      effect: 'Creates dissociation, words half-heard like fading memories',
      use_when: 'The subject is too painful to confront directly',
      justification: 'Sometimes the truth is easier to bear when obscured.',
    },
  ],
  Anxiety: [
    {
      rule: 'RHYTHM_ConstantDisplacement',
      effect: 'Never lets listener settle into comfortable expectation',
      use_when: 'Representing intrusive thoughts or restlessness',
      justification: 'Anxiety never follows a predictable pattern.',
    },
    {
      rule: 'HARMONY_UnresolvedSuspensions',
      effect: 'Creates tension that never fully releases',
      use_when: 'Showing the impossibility of finding peace',
      justification: 'The anxious mind cannot find resolution.',
    },
  ],
  Rage: [
    {
      rule: 'DYNAMICS_ExtremeContrasts',
      effect: 'Jarring shifts that mirror emotional volatility',
      use_when: 'The anger comes in unpredictable waves',
      justification: 'Rage rarely announces itself politely.',
    },
    {
      rule: 'FORM_StructuralCollapse',
      effect: 'Traditional form breaks down as control is lost',
      use_when: 'Representing loss of composure',
      justification: 'Anger destroys structure by nature.',
    },
  ],
  Joy: [
    {
      rule: 'HARMONY_ModalInterchange',
      effect: 'Unexpected brightness from borrowed chords',
      use_when: 'Joy that contains complexity and depth',
      justification: 'Real joy often comes from unexpected places.',
    },
  ],
  Love: [
    {
      rule: 'PRODUCTION_PitchImperfection',
      effect: 'Vulnerability through imperfect tuning',
      use_when: 'Love that is honest and unpolished',
      justification: 'Perfect pitch is a lie we tell ourselves.',
    },
  ],
};

export function useMusicBrain() {
  const [isLoading, setIsLoading] = React.useState(false);

  const getEmotions = async (): Promise<Emotion[]> => {
    setIsLoading(true);
    try {
      // In production: return invoke('music_brain_command', { command: 'get_emotions', args: {} });
      return new Promise((resolve) => {
        setTimeout(() => {
          setIsLoading(false);
          resolve(defaultEmotions);
        }, 300);
      });
    } catch (error) {
      setIsLoading(false);
      throw error;
    }
  };

  const suggestRuleBreak = async (emotion: string): Promise<RuleBreakSuggestion[]> => {
    setIsLoading(true);
    try {
      // In production: return invoke('music_brain_command', { command: 'suggest_rule_break', args: { emotion } });
      return new Promise((resolve) => {
        setTimeout(() => {
          const suggestions = ruleBreakingDatabase[emotion] || [
            {
              rule: 'HARMONY_ModalInterchange',
              effect: 'Unexpected harmonic color',
              use_when: 'You want to surprise the listener',
              justification: 'Breaking expectations creates emotional impact.',
            },
          ];
          setIsLoading(false);
          resolve(suggestions);
        }, 500);
      });
    } catch (error) {
      setIsLoading(false);
      throw error;
    }
  };

  const processIntent = async (intent?: Record<string, unknown>): Promise<ProcessIntentResult> => {
    setIsLoading(true);
    try {
      // In production: return invoke('music_brain_command', { command: 'process_intent', args: { intent } });
      return new Promise((resolve) => {
        setTimeout(() => {
          // Generate contextual results based on intent
          const intentData = intent || {};
          const emotion = (intentData.song_intent as Record<string, string>)?.mood_primary || 'neutral';
          const key = (intentData.technical_constraints as Record<string, string>)?.technical_key || 'C';

          const harmonyByEmotion: Record<string, string[]> = {
            Grief: ['Am', 'F', 'C', 'G'],
            Anxiety: ['Dm', 'Am/E', 'Bb', 'F/A'],
            Rage: ['Em', 'C', 'G', 'D'],
            Joy: ['C', 'G', 'Am', 'F'],
            Love: ['F', 'Am', 'Dm', 'C'],
          };

          const tempoByEmotion: Record<string, number> = {
            Grief: 72,
            Anxiety: 140,
            Rage: 160,
            Joy: 120,
            Love: 90,
          };

          setIsLoading(false);
          resolve({
            harmony: harmonyByEmotion[emotion] || ['C', 'Am', 'F', 'G'],
            tempo: tempoByEmotion[emotion] || 120,
            key,
            mixer_params: {
              reverb: emotion === 'Grief' ? 0.7 : 0.3,
              delay: emotion === 'Anxiety' ? 0.5 : 0.2,
              compression: emotion === 'Rage' ? 0.8 : 0.4,
              warmth: emotion === 'Love' ? 0.6 : 0.3,
            },
          });
        }, 800);
      });
    } catch (error) {
      setIsLoading(false);
      throw error;
    }
  };

  return {
    getEmotions,
    suggestRuleBreak,
    processIntent,
    isLoading,
  };
}
