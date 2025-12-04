import React, { useState } from 'react';
import { useStore } from '../../store/useStore';
import { ChevronRight, Lightbulb, HelpCircle } from 'lucide-react';
import clsx from 'clsx';

interface InterrogatorQuestion {
  id: string;
  phase: 0 | 1 | 2;
  question: string;
  hint: string;
}

const INTERROGATOR_QUESTIONS: InterrogatorQuestion[] = [
  // Phase 0: Core Wound/Desire
  {
    id: 'core_event',
    phase: 0,
    question: "What is the core event or memory this song is about?",
    hint: "The specific moment or experience that haunts or inspires this piece.",
  },
  {
    id: 'core_resistance',
    phase: 0,
    question: "What truth are you resisting admitting?",
    hint: "The uncomfortable realization you're dancing around.",
  },
  {
    id: 'core_longing',
    phase: 0,
    question: "What do you desperately want but can't have?",
    hint: "The ache at the center of this song.",
  },
  // Phase 1: Emotional Intent
  {
    id: 'emotion_primary',
    phase: 1,
    question: "If the listener feels only ONE thing, what should it be?",
    hint: "Not what you feel - what you want THEM to feel.",
  },
  {
    id: 'emotion_journey',
    phase: 1,
    question: "How should the emotional state change from start to finish?",
    hint: "Despair → acceptance? Anger → exhaustion? Joy → bittersweetness?",
  },
  {
    id: 'emotion_moment',
    phase: 1,
    question: "Where is the moment of maximum emotional impact?",
    hint: "The point where the listener should feel it most intensely.",
  },
  // Phase 2: Technical Constraints
  {
    id: 'tech_reference',
    phase: 2,
    question: "What existing song captures this feeling?",
    hint: "Not the style, but the emotional weight.",
  },
  {
    id: 'tech_avoid',
    phase: 2,
    question: "What must this song absolutely NOT sound like?",
    hint: "The production choices that would undermine the emotion.",
  },
  {
    id: 'tech_rule',
    phase: 2,
    question: "What conventional rule should this song break, and why?",
    hint: "Rule-breaking with emotional justification.",
  },
];

export const Interrogator: React.FC = () => {
  const { songIntent } = useStore();
  const [currentPhase, setCurrentPhase] = useState<0 | 1 | 2>(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [showHint, setShowHint] = useState(false);

  const phaseQuestions = INTERROGATOR_QUESTIONS.filter((q) => q.phase === currentPhase);
  const currentQuestion = phaseQuestions[currentQuestionIndex];
  const progress = ((currentPhase * 3 + currentQuestionIndex + 1) / 9) * 100;

  const handleAnswer = (answer: string) => {
    setAnswers({ ...answers, [currentQuestion.id]: answer });
  };

  const handleNext = () => {
    if (currentQuestionIndex < phaseQuestions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    } else if (currentPhase < 2) {
      setCurrentPhase((currentPhase + 1) as 0 | 1 | 2);
      setCurrentQuestionIndex(0);
    }
    setShowHint(false);
  };

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    } else if (currentPhase > 0) {
      setCurrentPhase((currentPhase - 1) as 0 | 1 | 2);
      const prevPhaseQuestions = INTERROGATOR_QUESTIONS.filter((q) => q.phase === currentPhase - 1);
      setCurrentQuestionIndex(prevPhaseQuestions.length - 1);
    }
    setShowHint(false);
  };

  const phaseLabels = ['Core Wound', 'Emotional Intent', 'Technical Constraints'];
  const phaseColors = ['text-emotion-grief', 'text-emotion-love', 'text-ableton-accent'];

  return (
    <div className="p-4 h-full flex flex-col">
      {/* Phase Indicator */}
      <div className="flex items-center gap-2 mb-4">
        {[0, 1, 2].map((phase) => (
          <React.Fragment key={phase}>
            <button
              className={clsx(
                'text-xs uppercase font-medium transition-colors',
                currentPhase === phase
                  ? phaseColors[phase]
                  : currentPhase > phase
                  ? 'text-ableton-text'
                  : 'text-ableton-text-dim'
              )}
              onClick={() => {
                setCurrentPhase(phase as 0 | 1 | 2);
                setCurrentQuestionIndex(0);
              }}
            >
              Phase {phase}: {phaseLabels[phase]}
            </button>
            {phase < 2 && (
              <ChevronRight size={14} className="text-ableton-text-dim" />
            )}
          </React.Fragment>
        ))}
      </div>

      {/* Progress Bar */}
      <div className="h-1 bg-ableton-bg rounded-full mb-6 overflow-hidden">
        <div
          className="h-full bg-ableton-accent transition-all duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Current Question */}
      <div className="flex-1">
        <div className="flex items-start gap-2 mb-4">
          <div className="text-lg font-medium text-ableton-text flex-1">
            {currentQuestion?.question}
          </div>
          <button
            className="p-1 hover:bg-ableton-surface rounded"
            onClick={() => setShowHint(!showHint)}
            title="Show hint"
          >
            <HelpCircle size={18} className="text-ableton-text-dim" />
          </button>
        </div>

        {/* Hint */}
        {showHint && (
          <div className="flex items-start gap-2 p-3 bg-ableton-surface-light rounded mb-4">
            <Lightbulb size={16} className="text-ableton-yellow shrink-0 mt-0.5" />
            <p className="text-sm text-ableton-text-dim italic">
              {currentQuestion?.hint}
            </p>
          </div>
        )}

        {/* Answer Input */}
        <textarea
          value={answers[currentQuestion?.id] || ''}
          onChange={(e) => handleAnswer(e.target.value)}
          placeholder="Take your time. Be honest with yourself..."
          className="w-full h-32 bg-ableton-bg border border-ableton-border rounded p-3 text-ableton-text resize-none focus:outline-none focus:border-ableton-accent"
        />

        {/* Current Emotion Context */}
        <div className="mt-4 p-3 bg-ableton-surface rounded">
          <div className="text-xs text-ableton-text-dim uppercase mb-1">
            Current Intent
          </div>
          <div className="text-sm">
            <span className="text-ableton-accent capitalize">
              {songIntent.coreEmotion}
            </span>
            <span className="text-ableton-text-dim"> → </span>
            <span className="text-ableton-text capitalize">
              {songIntent.subEmotion}
            </span>
            <span className="text-ableton-text-dim"> | </span>
            <span className="text-ableton-text">
              Vulnerability: {songIntent.vulnerabilityScale}/10
            </span>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex items-center justify-between mt-4 pt-4 border-t border-ableton-border">
        <button
          className="btn-ableton"
          onClick={handlePrevious}
          disabled={currentPhase === 0 && currentQuestionIndex === 0}
        >
          Previous
        </button>

        <div className="text-sm text-ableton-text-dim">
          Question {currentPhase * 3 + currentQuestionIndex + 1} of 9
        </div>

        <button
          className="btn-ableton"
          onClick={handleNext}
          disabled={currentPhase === 2 && currentQuestionIndex === phaseQuestions.length - 1}
        >
          {currentPhase === 2 && currentQuestionIndex === phaseQuestions.length - 1
            ? 'Complete'
            : 'Next'}
        </button>
      </div>
    </div>
  );
};
