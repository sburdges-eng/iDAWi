import React from 'react';
import { Play, Pause, Square, SkipBack, SkipForward, Circle } from 'lucide-react';
import { useStore } from '../../store/useStore';

export const Transport: React.FC = () => {
  const {
    isPlaying,
    isRecording,
    currentTime,
    tempo,
    timeSignature,
    setPlaying,
    setRecording,
    setCurrentTime,
    setTempo
  } = useStore();

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    const ms = Math.floor((seconds % 1) * 100);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}.${ms.toString().padStart(2, '0')}`;
  };

  const calculateBarBeat = (seconds: number) => {
    const beatsPerSecond = tempo / 60;
    const totalBeats = seconds * beatsPerSecond;
    const bar = Math.floor(totalBeats / timeSignature[0]) + 1;
    const beat = Math.floor(totalBeats % timeSignature[0]) + 1;
    return `${bar}.${beat}`;
  };

  return (
    <div className="h-16 bg-ableton-surface border-t border-ableton-border flex items-center px-4 gap-4">
      {/* Transport Controls */}
      <div className="flex items-center gap-2">
        <button
          onClick={() => setCurrentTime(0)}
          className="btn-ableton p-2"
          title="Go to start"
        >
          <SkipBack size={18} />
        </button>

        <button
          onClick={() => setPlaying(!isPlaying)}
          className={`btn-ableton p-2 ${isPlaying ? 'btn-ableton-active' : ''}`}
          title={isPlaying ? 'Pause' : 'Play'}
        >
          {isPlaying ? <Pause size={18} /> : <Play size={18} />}
        </button>

        <button
          onClick={() => {
            setPlaying(false);
            setCurrentTime(0);
          }}
          className="btn-ableton p-2"
          title="Stop"
        >
          <Square size={18} />
        </button>

        <button
          onClick={() => setRecording(!isRecording)}
          className={`btn-ableton p-2 ${isRecording ? 'bg-red-600 hover:bg-red-500' : ''}`}
          title={isRecording ? 'Stop Recording' : 'Record'}
        >
          <Circle size={18} fill={isRecording ? '#fff' : 'none'} />
        </button>
      </div>

      {/* Time Display */}
      <div className="flex items-center gap-4 font-mono text-sm">
        <div className="flex flex-col items-center">
          <span className="text-xs text-ableton-text-dim">Time</span>
          <span className="text-lg">{formatTime(currentTime)}</span>
        </div>
        <div className="flex flex-col items-center">
          <span className="text-xs text-ableton-text-dim">Bar.Beat</span>
          <span className="text-lg">{calculateBarBeat(currentTime)}</span>
        </div>
      </div>

      {/* Tempo */}
      <div className="flex items-center gap-2">
        <span className="text-xs text-ableton-text-dim">BPM</span>
        <input
          type="number"
          value={tempo}
          onChange={(e) => setTempo(Math.max(20, Math.min(300, Number(e.target.value))))}
          className="w-16 bg-ableton-bg border border-ableton-border rounded px-2 py-1 text-center font-mono"
          min="20"
          max="300"
        />
      </div>

      {/* Time Signature */}
      <div className="flex items-center gap-1">
        <span className="text-xs text-ableton-text-dim">Time Sig</span>
        <span className="font-mono">{timeSignature[0]}/{timeSignature[1]}</span>
      </div>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Status indicators */}
      <div className="flex items-center gap-4">
        {isRecording && (
          <div className="flex items-center gap-1 text-red-500">
            <Circle size={8} fill="currentColor" className="animate-pulse" />
            <span className="text-xs">REC</span>
          </div>
        )}
        {isPlaying && (
          <div className="flex items-center gap-1 text-green-500">
            <Play size={8} fill="currentColor" />
            <span className="text-xs">PLAY</span>
          </div>
        )}
      </div>
    </div>
  );
};
