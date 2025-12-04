import React, { useState, useEffect } from 'react';
import { Sparkles, Copy, RefreshCw, Check } from 'lucide-react';
import { useMusicBrain } from '../../hooks/useMusicBrain';

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

interface GhostWriterProps {
  emotion: string | null;
  intent: Record<string, unknown> | null;
}

export const GhostWriter: React.FC<GhostWriterProps> = ({ emotion, intent }) => {
  const [suggestions, setSuggestions] = useState<RuleBreakSuggestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ProcessIntentResult | null>(null);
  const [copied, setCopied] = useState(false);
  const { suggestRuleBreak, processIntent } = useMusicBrain();

  useEffect(() => {
    if (emotion) {
      loadSuggestions();
    }
  }, [emotion]);

  useEffect(() => {
    if (intent) {
      generateMusic();
    }
  }, [intent]);

  const loadSuggestions = async () => {
    if (!emotion) return;

    setLoading(true);
    try {
      const data = await suggestRuleBreak(emotion);
      setSuggestions(data);
    } catch (error) {
      console.error('Failed to load suggestions:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateMusic = async () => {
    if (!intent) return;

    setLoading(true);
    try {
      const data = await processIntent(intent);
      setResult(data);
    } catch (error) {
      console.error('Failed to generate music:', error);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!emotion) {
    return (
      <div className="p-6 border-t border-ableton-border">
        <div className="flex items-center gap-2 mb-4">
          <Sparkles className="text-ableton-accent" size={20} />
          <h3 className="font-bold">Ghost Writer</h3>
        </div>
        <p className="text-ableton-text-dim text-sm">
          Complete the interrogation to receive AI-powered suggestions
        </p>
        <div className="mt-6 p-4 bg-ableton-bg rounded border border-ableton-border border-dashed">
          <div className="text-center text-ableton-text-dim text-sm">
            Waiting for emotional input...
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 border-t border-ableton-border overflow-auto max-h-full">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Sparkles className="text-ableton-accent" size={20} />
          <h3 className="font-bold">Ghost Writer</h3>
        </div>
        <button
          onClick={loadSuggestions}
          className="btn-ableton p-2"
          disabled={loading}
          title="Refresh suggestions"
        >
          <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
        </button>
      </div>

      {/* Rule-Breaking Suggestions */}
      {suggestions.length > 0 && (
        <div className="mb-6">
          <h4 className="text-sm font-medium mb-3 text-ableton-text-dim">
            Suggested Rule Violations for &ldquo;{emotion}&rdquo;
          </h4>
          <div className="space-y-2">
            {suggestions.map((suggestion, i) => (
              <div
                key={i}
                className="p-3 bg-ableton-surface border border-ableton-border rounded hover:border-ableton-accent transition-colors"
              >
                <div className="font-mono text-sm mb-1 text-ableton-accent">
                  {suggestion.rule}
                </div>
                <div className="text-xs text-ableton-text-dim mb-2">
                  <span className="text-ableton-text">Effect:</span> {suggestion.effect}
                </div>
                <div className="text-xs italic text-ableton-text-dim border-l-2 border-ableton-accent pl-2">
                  &ldquo;{suggestion.justification}&rdquo;
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Generated Music */}
      {result && (
        <div className="border-t border-ableton-border pt-4">
          <h4 className="text-sm font-medium mb-3 flex items-center gap-2">
            <Check size={16} className="text-green-500" />
            Generated Music
          </h4>

          <div className="space-y-3">
            {/* Chord Progression */}
            <div className="p-3 bg-ableton-surface rounded border border-ableton-border">
              <div className="text-xs text-ableton-text-dim mb-1">Chord Progression</div>
              <div className="font-mono text-lg">
                {result.harmony?.join(' - ') || 'N/A'}
              </div>
              <button
                onClick={() => copyToClipboard(result.harmony?.join(' - ') || '')}
                className="btn-ableton mt-2 text-xs flex items-center gap-1"
              >
                {copied ? <Check size={12} /> : <Copy size={12} />}
                {copied ? 'Copied!' : 'Copy to Timeline'}
              </button>
            </div>

            {/* Tempo and Key */}
            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 bg-ableton-surface rounded border border-ableton-border">
                <div className="text-xs text-ableton-text-dim mb-1">Tempo</div>
                <div className="font-mono text-2xl">{result.tempo} <span className="text-sm">BPM</span></div>
              </div>

              <div className="p-3 bg-ableton-surface rounded border border-ableton-border">
                <div className="text-xs text-ableton-text-dim mb-1">Key</div>
                <div className="font-mono text-2xl">{result.key}</div>
              </div>
            </div>

            {/* Mixer Settings */}
            {result.mixer_params && (
              <div className="p-3 bg-ableton-surface rounded border border-ableton-border">
                <div className="text-xs text-ableton-text-dim mb-2">Suggested Mixer Settings</div>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  {Object.entries(result.mixer_params).map(([key, value]) => (
                    <div key={key} className="flex justify-between">
                      <span className="capitalize">{key}:</span>
                      <span className="font-mono text-ableton-accent">
                        {typeof value === 'number' ? `${Math.round(value * 100)}%` : value}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Philosophy Quote */}
      <div className="mt-6 p-3 bg-ableton-bg bg-opacity-50 rounded text-xs text-ableton-text-dim italic border-l-2 border-ableton-accent">
        &ldquo;Interrogate Before Generate&rdquo; - Every suggestion is
        justified by emotional intent, not arbitrary technical choices.
      </div>
    </div>
  );
};
