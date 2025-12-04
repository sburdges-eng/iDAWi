import React, { useState, useEffect } from 'react';
import { useStore } from '../../store/useStore';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import clsx from 'clsx';
import { VUMeter } from './VUMeter';
import { Knob } from './Knob';

export const Mixer: React.FC = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const { tracks, updateTrack, selectedTrackId, selectTrack, isPlaying } = useStore();
  const [levels, setLevels] = useState<Record<string, { left: number; right: number }>>({});

  // Simulate audio levels (would come from audio engine in production)
  useEffect(() => {
    if (!isPlaying) {
      // Clear levels when not playing
      const clearedLevels: Record<string, { left: number; right: number }> = {};
      tracks.forEach(track => {
        clearedLevels[track.id] = { left: 0, right: 0 };
      });
      setLevels(clearedLevels);
      return;
    }

    const interval = setInterval(() => {
      const newLevels: Record<string, { left: number; right: number }> = {};
      tracks.forEach(track => {
        if (!track.muted) {
          // Simulate stereo levels based on track volume and pan
          const baseLevel = Math.random() * 0.4 + 0.3; // Base random level
          const volumeAdjusted = baseLevel * track.volume;

          // Pan affects stereo balance
          const panFactor = track.pan; // -1 to 1
          const leftLevel = volumeAdjusted * Math.min(1, 1 - panFactor);
          const rightLevel = volumeAdjusted * Math.min(1, 1 + panFactor);

          newLevels[track.id] = {
            left: leftLevel + Math.random() * 0.1,
            right: rightLevel + Math.random() * 0.1
          };
        } else {
          newLevels[track.id] = { left: 0, right: 0 };
        }
      });
      setLevels(newLevels);
    }, 50); // 20fps for smoother animation

    return () => clearInterval(interval);
  }, [tracks, isPlaying]);

  if (isCollapsed) {
    return (
      <div className="w-6 bg-ableton-surface border-l border-ableton-border flex flex-col items-center pt-2">
        <button
          className="p-1 hover:bg-ableton-surface-light rounded"
          onClick={() => setIsCollapsed(false)}
          title="Show Mixer"
        >
          <ChevronLeft size={16} />
        </button>
        <div
          className="mt-4 text-xs text-ableton-text-dim"
          style={{ writingMode: 'vertical-rl' }}
        >
          MIXER
        </div>
      </div>
    );
  }

  return (
    <div className="w-auto bg-ableton-surface border-l border-ableton-border flex flex-col">
      {/* Mixer Header */}
      <div className="h-8 border-b border-ableton-border flex items-center px-2 justify-between">
        <span className="text-xs text-ableton-text-dim uppercase tracking-wider">
          Mixer
        </span>
        <button
          className="p-1 hover:bg-ableton-surface-light rounded"
          onClick={() => setIsCollapsed(true)}
          title="Hide Mixer"
        >
          <ChevronRight size={14} />
        </button>
      </div>

      {/* Mixer Channels */}
      <div className="flex-1 flex overflow-x-auto p-2 gap-1">
        {tracks.map((track) => (
          <MixerChannel
            key={track.id}
            track={track}
            isSelected={track.id === selectedTrackId}
            levels={levels[track.id] || { left: 0, right: 0 }}
            onSelect={() => selectTrack(track.id)}
            onUpdate={(updates) => updateTrack(track.id, updates)}
          />
        ))}

        {/* Master Channel */}
        <MasterChannel levels={levels} tracks={tracks} />
      </div>
    </div>
  );
};

interface MixerChannelProps {
  track: {
    id: string;
    name: string;
    color: string;
    muted: boolean;
    solo: boolean;
    armed: boolean;
    volume: number;
    pan: number;
  };
  isSelected: boolean;
  levels: { left: number; right: number };
  onSelect: () => void;
  onUpdate: (updates: { volume?: number; pan?: number; muted?: boolean; solo?: boolean }) => void;
}

const MixerChannel: React.FC<MixerChannelProps> = ({
  track,
  isSelected,
  levels,
  onSelect,
  onUpdate,
}) => {
  return (
    <div
      className={clsx(
        'mixer-channel',
        isSelected && 'bg-ableton-surface-light'
      )}
      onClick={onSelect}
    >
      {/* Track name */}
      <div
        className="text-xs truncate w-full text-center mb-2"
        title={track.name}
      >
        {track.name}
      </div>

      {/* Pan knob */}
      <Knob
        value={track.pan}
        onChange={(val) => onUpdate({ pan: val })}
        label="PAN"
        min={-1}
        max={1}
        size="sm"
        showValue
      />

      {/* VU Meters + Fader */}
      <div className="flex-1 flex items-end gap-1 mb-2 mt-3">
        {/* Left VU Meter */}
        <VUMeter
          level={track.muted ? 0 : levels.left}
          height="h-28"
        />

        {/* Fader */}
        <div className="h-28 flex flex-col items-center">
          <input
            type="range"
            min={0}
            max={1}
            step={0.01}
            value={track.volume}
            onChange={(e) => onUpdate({ volume: parseFloat(e.target.value) })}
            className="h-24 w-4"
            style={{
              writingMode: 'vertical-lr',
              direction: 'rtl',
              WebkitAppearance: 'slider-vertical',
            }}
            onClick={(e) => e.stopPropagation()}
          />
        </div>

        {/* Right VU Meter */}
        <VUMeter
          level={track.muted ? 0 : levels.right}
          height="h-28"
        />
      </div>

      {/* dB reading */}
      <div className="text-[10px] font-mono text-ableton-text-dim text-center mb-2">
        {track.volume === 0 ? '-∞' : `${Math.round((track.volume - 1) * 40)}dB`}
      </div>

      {/* Mute/Solo Buttons */}
      <div className="flex gap-1 mb-2">
        <button
          className={clsx(
            'px-2 py-1 text-xs rounded transition-colors',
            track.muted
              ? 'bg-ableton-yellow text-black'
              : 'bg-ableton-surface-light text-ableton-text-dim hover:bg-ableton-border'
          )}
          onClick={(e) => {
            e.stopPropagation();
            onUpdate({ muted: !track.muted });
          }}
          title="Mute"
        >
          M
        </button>
        <button
          className={clsx(
            'px-2 py-1 text-xs rounded transition-colors',
            track.solo
              ? 'bg-ableton-accent text-black'
              : 'bg-ableton-surface-light text-ableton-text-dim hover:bg-ableton-border'
          )}
          onClick={(e) => {
            e.stopPropagation();
            onUpdate({ solo: !track.solo });
          }}
          title="Solo"
        >
          S
        </button>
      </div>

      {/* Color indicator */}
      <div
        className="w-full h-2 rounded-sm"
        style={{ backgroundColor: track.color }}
      />
    </div>
  );
};

interface MasterChannelProps {
  levels: Record<string, { left: number; right: number }>;
  tracks: Array<{ id: string; muted: boolean; solo: boolean }>;
}

const MasterChannel: React.FC<MasterChannelProps> = ({ levels, tracks }) => {
  const [masterVolume, setMasterVolume] = useState(0.85);

  // Calculate master levels from all non-muted tracks
  const activeTracks = tracks.filter(t => !t.muted);
  const soloedTracks = tracks.filter(t => t.solo);
  const tracksToSum = soloedTracks.length > 0 ? soloedTracks : activeTracks;

  let masterLeft = 0;
  let masterRight = 0;

  tracksToSum.forEach(track => {
    const trackLevels = levels[track.id];
    if (trackLevels) {
      masterLeft = Math.max(masterLeft, trackLevels.left);
      masterRight = Math.max(masterRight, trackLevels.right);
    }
  });

  // Apply master volume
  masterLeft *= masterVolume;
  masterRight *= masterVolume;

  return (
    <div className="mixer-channel bg-ableton-surface-light border-l-2 border-ableton-accent">
      {/* Track name */}
      <div className="text-xs truncate w-full text-center mb-2 font-medium text-ableton-accent">
        MASTER
      </div>

      {/* Spacer for pan area alignment */}
      <div className="h-14 mb-2" />

      {/* VU Meters + Fader */}
      <div className="flex-1 flex items-end gap-1 mb-2">
        {/* Left VU Meter */}
        <VUMeter level={masterLeft} height="h-28" />

        {/* Fader */}
        <div className="h-28 flex flex-col items-center">
          <input
            type="range"
            min={0}
            max={1}
            step={0.01}
            value={masterVolume}
            onChange={(e) => setMasterVolume(parseFloat(e.target.value))}
            className="h-24 w-4"
            style={{
              writingMode: 'vertical-lr',
              direction: 'rtl',
              WebkitAppearance: 'slider-vertical',
            }}
          />
        </div>

        {/* Right VU Meter */}
        <VUMeter level={masterRight} height="h-28" />
      </div>

      {/* dB reading */}
      <div className="text-[10px] font-mono text-ableton-text-dim text-center mb-2">
        {masterVolume === 0 ? '-∞' : `${Math.round((masterVolume - 1) * 40)}dB`}
      </div>

      {/* Spacer for button alignment */}
      <div className="h-8 mb-2" />

      {/* Color indicator */}
      <div className="w-full h-2 rounded-sm bg-ableton-accent" />
    </div>
  );
};
