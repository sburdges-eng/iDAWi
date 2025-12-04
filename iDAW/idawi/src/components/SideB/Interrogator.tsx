import React, { useState } from 'react';
import { ChevronRight, ChevronLeft } from 'lucide-react';

interface InterrogatorProps {
  emotion: string | null;
  onComplete: (intent: Record<string, unknown>) => void;
}

export const Interrogator: React.FC<InterrogatorProps> = ({ emotion, onComplete }) => {
  const [phase, setPhase] = useState<0 | 1 | 2>(0);
  const [answers, setAnswers] = useState({
    // Phase 0: Core Wound/Desire
    core_event: '',
    core_resistance: '',
    core_longing: '',

    // Phase 1: Emotional Intent
    mood_primary: emotion || '',
    mood_secondary_tension: 0.5,
    vulnerability_scale: 'Medium',

    // Phase 2: Technical Constraints
    technical_key: 'C',
    technical_rule_to_break: '',
    rule_breaking_justification: '',
  });

  // Update mood_primary when emotion prop changes
  React.useEffect(() => {
    if (emotion) {
      setAnswers(prev => ({ ...prev, mood_primary: emotion }));
    }
  }, [emotion]);

  const phases = [
    {
      title: 'Phase 0: Core Wound/Desire',
      subtitle: 'What truth are you carrying?',
      questions: [
        { key: 'core_event', label: 'What happened?', placeholder: 'The event that hurt or moved you...' },
        { key: 'core_resistance', label: 'What holds you back?', placeholder: 'What makes this hard to express...' },
        { key: 'core_longing', label: 'What do you want to feel?', placeholder: 'The emotional resolution you seek...' },
      ],
    },
    {
      title: 'Phase 1: Emotional Intent',
      subtitle: 'How should it feel?',
      questions: [
        { key: 'mood_primary', label: 'Primary Emotion', placeholder: emotion || '', disabled: true },
        { key: 'vulnerability_scale', label: 'Vulnerability Level', type: 'select', options: ['Low', 'Medium', 'High', 'Devastating'] },
      ],
    },
    {
      title: 'Phase 2: Technical Constraints',
      subtitle: 'What rules will you break?',
      questions: [
        { key: 'technical_key', label: 'Musical Key', type: 'select', options: ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B', 'Am', 'Dm', 'Em'] },
        { key: 'technical_rule_to_break', label: 'Rule to Break (optional)', placeholder: 'e.g., HARMONY_ModalInterchange' },
        { key: 'rule_breaking_justification', label: 'Why break this rule?', placeholder: 'How does this serve the emotion...' },
      ],
    },
  ];

  const currentPhase = phases[phase];

  const handleNext = () => {
    if (phase < 2) {
      setPhase((phase + 1) as 0 | 1 | 2);
    } else {
      // Build complete intent object
      const intent = {
        song_root: {
          core_event: answers.core_event,
          core_resistance: answers.core_resistance,
          core_longing: answers.core_longing,
        },
        song_intent: {
          mood_primary: answers.mood_primary,
          mood_secondary_tension: answers.mood_secondary_tension,
          vulnerability_scale: answers.vulnerability_scale,
        },
        technical_constraints: {
          technical_key: answers.technical_key,
          technical_rule_to_break: answers.technical_rule_to_break,
          rule_breaking_justification: answers.rule_breaking_justification,
        },
      };

      onComplete(intent);
    }
  };

  const handleBack = () => {
    if (phase > 0) {
      setPhase((phase - 1) as 0 | 1 | 2);
    }
  };

  if (!emotion) {
    return (
      <div className="p-6 text-center">
        <div className="text-ableton-text-dim mb-4">
          Select an emotion from the wheel above to begin
        </div>
        <div className="text-4xl opacity-20">...</div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h2 className="text-xl font-bold">{currentPhase.title}</h2>
        <p className="text-sm text-ableton-text-dim">{currentPhase.subtitle}</p>
        <div className="flex gap-2 mt-3">
          {[0, 1, 2].map((p) => (
            <div
              key={p}
              className={`h-1 flex-1 rounded transition-all ${
                p === phase ? 'bg-ableton-accent' : p < phase ? 'bg-ableton-accent opacity-50' : 'bg-ableton-border'
              }`}
            />
          ))}
        </div>
      </div>

      <div className="space-y-4">
<<<<<<< Current (Your changes)
        {currentPhase.questions.map((q) => (
          <div key={q.key}>
            <label className="block text-sm font-medium mb-2">
              {q.label}
            </label>

            {q.type === 'select' ? (
              <select
                value={(answers as Record<string, string | number>)[q.key] as string}
                onChange={(e) => setAnswers({ ...answers, [q.key]: e.target.value })}
                className="w-full bg-ableton-bg border border-ableton-border rounded px-3 py-2 focus:border-ableton-accent focus:outline-none"
              >
                {q.options?.map((opt) => (
                  <option key={opt} value={opt}>{opt}</option>
                ))}
              </select>
            ) : (
              <textarea
                value={(answers as Record<string, string | number>)[q.key] as string}
                onChange={(e) => setAnswers({ ...answers, [q.key]: e.target.value })}
                placeholder={q.placeholder}
                disabled={q.disabled}
                className={`w-full bg-ableton-bg border border-ableton-border rounded px-3 py-2 min-h-[80px] focus:border-ableton-accent focus:outline-none resize-none ${
                  q.disabled ? 'opacity-60 cursor-not-allowed' : ''
                }`}
              />
            )}
          </div>
        ))}
=======
        {currentPhase.questions.map((q) => {
          const isDisabled = 'disabled' in q && q.disabled;
          return (
            <div key={q.key}>
              <label className="block text-sm font-medium mb-2">
                {q.label}
              </label>

              {'type' in q && q.type === 'select' ? (
                <select
                  value={(answers as Record<string, string | number>)[q.key] as string}
                  onChange={(e) => setAnswers({ ...answers, [q.key]: e.target.value })}
                  className="w-full bg-ableton-bg border border-ableton-border rounded px-3 py-2 focus:border-ableton-accent focus:outline-none"
                >
                  {q.options?.map((opt) => (
                    <option key={opt} value={opt}>{opt}</option>
                  ))}
                </select>
              ) : (
                <textarea
                  value={(answers as Record<string, string | number>)[q.key] as string}
                  onChange={(e) => setAnswers({ ...answers, [q.key]: e.target.value })}
                  placeholder={'placeholder' in q ? q.placeholder : ''}
                  disabled={isDisabled}
                  className={`w-full bg-ableton-bg border border-ableton-border rounded px-3 py-2 min-h-[80px] focus:border-ableton-accent focus:outline-none resize-none ${
                    isDisabled ? 'opacity-60 cursor-not-allowed' : ''
                  }`}
                />
              )}
            </div>
          );
        })}
>>>>>>> Incoming (Background Agent changes)
      </div>

      <div className="flex gap-2 mt-6">
        {phase > 0 && (
          <button
            onClick={handleBack}
            className="btn-ableton flex-1 flex items-center justify-center gap-2"
          >
            <ChevronLeft size={16} />
            Back
          </button>
        )}
        <button
          onClick={handleNext}
          className="btn-ableton-active flex-1 flex items-center justify-center gap-2"
        >
          {phase < 2 ? 'Next Phase' : 'Generate Music'}
          <ChevronRight size={16} />
        </button>
      </div>
    </div>
  );
};
