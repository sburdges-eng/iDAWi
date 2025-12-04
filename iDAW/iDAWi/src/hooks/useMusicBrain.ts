import { useCallback, useState } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { useStore, GhostWriterSuggestion } from '../store/useStore';

interface PythonBridgeResponse {
  success: boolean;
  data?: unknown;
  error?: string;
}

interface RuleBreakSuggestion {
  rule: string;
  effect: string;
  examples: string[];
  mixer_params?: Record<string, number>;
}

interface EmotionInfo {
  name: string;
  category: string;
  intensity: number;
}

export function useMusicBrain() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { songIntent, addGhostWriterSuggestion } = useStore();

  const callMusicBrain = useCallback(async (
    command: string,
    args: Record<string, unknown> = {}
  ): Promise<PythonBridgeResponse> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await invoke<PythonBridgeResponse>('music_brain_command', {
        command,
        args,
      });

      if (!response.success && response.error) {
        setError(response.error);
      }

      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setIsLoading(false);
    }
  }, []);

  const suggestRuleBreak = useCallback(async (emotion: string): Promise<RuleBreakSuggestion[]> => {
    const response = await callMusicBrain('suggest_rule_break', { emotion });

    if (response.success && response.data) {
      const suggestions = response.data as RuleBreakSuggestion[];

      // Add suggestions to Ghost Writer
      suggestions.forEach((suggestion) => {
        addGhostWriterSuggestion({
          type: categorizeRuleBreak(suggestion.rule),
          description: `${suggestion.rule}: ${suggestion.effect}`,
          emotionalRationale: `Breaking this rule creates ${emotion} through ${suggestion.effect.toLowerCase()}`,
        });
      });

      return suggestions;
    }

    return [];
  }, [callMusicBrain, addGhostWriterSuggestion]);

  const processIntent = useCallback(async () => {
    const response = await callMusicBrain('process_intent', {
      intent: {
        song_root: {
          core_emotion: songIntent.coreEmotion,
          sub_emotion: songIntent.subEmotion,
        },
        song_intent: {
          vulnerability_scale: songIntent.vulnerabilityScale,
          narrative_arc: songIntent.narrativeArc,
        },
        technical_constraints: {
          rule_to_break: songIntent.ruleToBreak,
        },
      },
    });

    if (response.success && response.data) {
      return response.data as {
        harmony: string[];
        tempo: number;
        key: string;
        mixer_params: Record<string, number>;
      };
    }

    return null;
  }, [callMusicBrain, songIntent]);

  const getEmotions = useCallback(async (): Promise<EmotionInfo[]> => {
    const response = await callMusicBrain('get_emotions');

    if (response.success && response.data) {
      return response.data as EmotionInfo[];
    }

    // Fallback emotions if Music Brain is not available
    return [
      { name: 'Grief', category: 'Sadness', intensity: 0.8 },
      { name: 'Yearning', category: 'Sadness', intensity: 0.6 },
      { name: 'Joy', category: 'Happiness', intensity: 0.9 },
      { name: 'Contentment', category: 'Happiness', intensity: 0.5 },
      { name: 'Rage', category: 'Anger', intensity: 1.0 },
      { name: 'Frustration', category: 'Anger', intensity: 0.6 },
      { name: 'Terror', category: 'Fear', intensity: 1.0 },
      { name: 'Anxiety', category: 'Fear', intensity: 0.7 },
      { name: 'Love', category: 'Connection', intensity: 0.9 },
      { name: 'Loneliness', category: 'Connection', intensity: 0.7 },
      { name: 'Hope', category: 'Anticipation', intensity: 0.8 },
      { name: 'Dread', category: 'Anticipation', intensity: 0.7 },
    ];
  }, [callMusicBrain]);

  return {
    isLoading,
    error,
    suggestRuleBreak,
    processIntent,
    getEmotions,
  };
}

// Helper function to categorize rule breaks
function categorizeRuleBreak(rule: string): GhostWriterSuggestion['type'] {
  const ruleLower = rule.toLowerCase();

  if (ruleLower.includes('harmony') || ruleLower.includes('chord') || ruleLower.includes('key')) {
    return 'harmony';
  }
  if (ruleLower.includes('rhythm') || ruleLower.includes('tempo') || ruleLower.includes('groove')) {
    return 'rhythm';
  }
  if (ruleLower.includes('arrangement') || ruleLower.includes('structure')) {
    return 'arrangement';
  }
  return 'production';
}
