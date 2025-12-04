import React from 'react';
import {
  Play,
  Pause,
  Square,
  SkipBack,
  SkipForward,
  Circle,
  Repeat,
} from 'lucide-react';
import { useStore } from '../../store/useStore';
import { useTauriAudio } from '../../hooks/useTauriAudio';
import clsx from 'clsx';

export const Transport: React.FC = () => {
  const {
    isPlaying,
    isRecording,
    position,
    tempo,
    timeSignature,
    loopEnabled,
    toggleRecord,
    toggleLoop,
  } = useStore();

  const audio = useTauriAudio();

  // Format time display (bars:beats:ticks)
  const formatTime = (samples: number): string => {
    const sampleRate = 44100;
    const beatsPerBar = timeSignature.numerator;
    const samplesPerBeat = (60 / tempo) * sampleRate;
    const samplesPerBar = samplesPerBeat * beatsPerBar;

    const bars = Math.floor(samples / samplesPerBar) + 1;
    const remainingSamples = samples % samplesPerBar;
    const beats = Math.floor(remainingSamples / samplesPerBeat) + 1;
    const ticks = Math.floor((remainingSamples % samplesPerBeat) / (samplesPerBeat / 16)) + 1;

    return `${bars.toString().padStart(3, '0')}.${beats}.${ticks.toString().padStart(2, '0')}`;
  };

  // Format clock display (mm:ss:ms)
  const formatClock = (samples: number): string => {
    const sampleRate = 44100;
    const totalSeconds = samples / sampleRate;
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = Math.floor(totalSeconds % 60);
    const ms = Math.floor((totalSeconds % 1) * 100);

    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}.${ms.toString().padStart(2, '0')}`;
  };

  return (
    <div className="h-14 bg-ableton-surface border-t border-ableton-border flex items-center px-4 gap-4">
      {/* Transport Controls */}
      <div className="flex items-center gap-1">
        {/* Stop */}
        <button
          className="btn-ableton-icon"
          onClick={audio.stop}
          title="Stop"
        >
          <Square size={16} />
        </button>

        {/* Skip Back */}
        <button
          className="btn-ableton-icon"
          onClick={audio.stop}
          title="Go to Start"
        >
          <SkipBack size={16} />
        </button>

        {/* Play/Pause */}
        <button
          className={clsx(
            'btn-ableton-icon',
            isPlaying && 'bg-ableton-green/20 text-ableton-green'
          )}
          onClick={audio.togglePlayPause}
          title={isPlaying ? 'Pause (Space)' : 'Play (Space)'}
        >
          {isPlaying ? <Pause size={16} /> : <Play size={16} />}
        </button>

        {/* Skip Forward */}
        <button
          className="btn-ableton-icon"
          title="Go to End"
        >
          <SkipForward size={16} />
        </button>

        {/* Record */}
        <button
          className={clsx(
            'btn-ableton-icon',
            isRecording && 'bg-ableton-red/20 text-ableton-red record-pulse'
          )}
          onClick={toggleRecord}
          title="Record"
        >
          <Circle size={16} fill={isRecording ? 'currentColor' : 'none'} />
        </button>
      </div>

      {/* Divider */}
      <div className="w-px h-8 bg-ableton-border" />

      {/* Loop Toggle */}
      <button
        className={clsx(
          'btn-ableton-icon',
          loopEnabled && 'bg-ableton-accent/20 text-ableton-accent'
        )}
        onClick={toggleLoop}
        title="Loop"
      >
        <Repeat size={16} />
      </button>

      {/* Divider */}
      <div className="w-px h-8 bg-ableton-border" />

      {/* Time Display */}
      <div className="flex flex-col items-center min-w-[100px]">
        <div className="font-mono text-lg text-ableton-text tabular-nums">
          {formatTime(position)}
        </div>
        <div className="font-mono text-xs text-ableton-text-dim tabular-nums">
          {formatClock(position)}
        </div>
      </div>

      {/* Divider */}
      <div className="w-px h-8 bg-ableton-border" />

      {/* Tempo */}
      <div className="flex items-center gap-2">
        <span className="text-ableton-text-dim text-xs uppercase">BPM</span>
        <input
          type="number"
          value={tempo}
          onChange={(e) => audio.setTempo(parseFloat(e.target.value) || 120)}
          className="w-16 bg-ableton-bg border border-ableton-border rounded-sm px-2 py-1 text-center font-mono text-sm"
          min={20}
          max={300}
          step={1}
        />
      </div>

      {/* Time Signature */}
      <div className="flex items-center gap-1">
        <span className="text-ableton-text-dim text-xs uppercase">Time</span>
        <div className="flex items-center bg-ableton-bg border border-ableton-border rounded-sm px-2 py-1">
          <span className="font-mono text-sm">{timeSignature.numerator}/{timeSignature.denominator}</span>
        </div>
      </div>

      {/* Spacer */}
      <div className="flex-1" />

      {/* CPU/DSP Meter (placeholder) */}
      <div className="flex items-center gap-2">
        <span className="text-ableton-text-dim text-xs">CPU</span>
        <div className="w-16 h-2 bg-ableton-bg rounded-full overflow-hidden">
          <div className="h-full w-1/4 bg-ableton-green rounded-full" />
        </div>
      </div>

      {/* Status */}
      <div className="flex items-center gap-2">
        {isPlaying && (
          <div className="flex items-center gap-1 text-ableton-green">
            <div className="w-2 h-2 rounded-full bg-ableton-green animate-pulse" />
            <span className="text-xs">Playing</span>
          </div>
        )}
        {isRecording && (
          <div className="flex items-center gap-1 text-ableton-red">
            <div className="w-2 h-2 rounded-full bg-ableton-red record-pulse" />
            <span className="text-xs">Recording</span>
          </div>
        )}
      </div>
    </div>
  );
};
