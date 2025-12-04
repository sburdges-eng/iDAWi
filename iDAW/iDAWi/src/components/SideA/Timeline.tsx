import React, { useMemo } from 'react';
import { useStore, Track, Clip } from '../../store/useStore';
import { Volume2, VolumeX, Headphones, CircleDot, Trash2 } from 'lucide-react';
import clsx from 'clsx';

const PIXELS_PER_BAR = 80;
const TOTAL_BARS = 32;

export const Timeline: React.FC = () => {
  const {
    tracks,
    clips,
    selectedTrackId,
    selectedClipId,
    selectTrack,
    selectClip,
    updateTrack,
    removeTrack,
    position,
    tempo,
    timeSignature,
  } = useStore();

  // Calculate playhead position
  const playheadPosition = useMemo(() => {
    const sampleRate = 44100;
    const beatsPerBar = timeSignature.numerator;
    const samplesPerBeat = (60 / tempo) * sampleRate;
    const samplesPerBar = samplesPerBeat * beatsPerBar;
    const bars = position / samplesPerBar;
    return bars * PIXELS_PER_BAR;
  }, [position, tempo, timeSignature]);

  // Get clips for a specific track
  const getTrackClips = (trackId: string): Clip[] => {
    return clips.filter((c) => c.trackId === trackId);
  };

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Timeline Header (Bar numbers) */}
      <div className="h-6 bg-ableton-bg border-b border-ableton-border flex">
        {/* Track header spacer */}
        <div className="w-48 bg-ableton-surface border-r border-ableton-border" />

        {/* Bar numbers */}
        <div className="flex-1 overflow-hidden relative">
          <div className="flex absolute top-0 left-0">
            {Array.from({ length: TOTAL_BARS }, (_, i) => (
              <div
                key={i}
                className="flex-shrink-0 text-xs text-ableton-text-dim font-mono px-1 border-r border-ableton-border/30"
                style={{ width: PIXELS_PER_BAR }}
              >
                {i + 1}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Tracks Container */}
      <div className="flex-1 overflow-auto">
        {tracks.map((track) => (
          <TrackRow
            key={track.id}
            track={track}
            clips={getTrackClips(track.id)}
            isSelected={track.id === selectedTrackId}
            selectedClipId={selectedClipId}
            onSelectTrack={() => selectTrack(track.id)}
            onSelectClip={selectClip}
            onUpdateTrack={(updates) => updateTrack(track.id, updates)}
            onRemoveTrack={() => removeTrack(track.id)}
            playheadPosition={playheadPosition}
          />
        ))}

        {/* Empty track placeholder */}
        {tracks.length === 0 && (
          <div className="h-32 flex items-center justify-center text-ableton-text-dim">
            No tracks. Click + to add a track.
          </div>
        )}
      </div>

      {/* Playhead overlay */}
      <div
        className="absolute top-6 bottom-14 w-px bg-ableton-accent pointer-events-none z-20"
        style={{ left: 192 + playheadPosition }} // 192 = track header width (w-48 = 12rem = 192px)
      />
    </div>
  );
};

interface TrackRowProps {
  track: Track;
  clips: Clip[];
  isSelected: boolean;
  selectedClipId: string | null;
  onSelectTrack: () => void;
  onSelectClip: (id: string | null) => void;
  onUpdateTrack: (updates: Partial<Track>) => void;
  onRemoveTrack: () => void;
  playheadPosition: number;
}

const TrackRow: React.FC<TrackRowProps> = ({
  track,
  clips,
  isSelected,
  selectedClipId,
  onSelectTrack,
  onSelectClip,
  onUpdateTrack,
  onRemoveTrack,
}) => {
  return (
    <div
      className={clsx(
        'track flex',
        isSelected && 'track-selected'
      )}
      onClick={onSelectTrack}
    >
      {/* Track Header */}
      <div className="w-48 bg-ableton-surface-light border-r border-ableton-border flex items-center px-2 gap-2 shrink-0">
        {/* Color indicator */}
        <div
          className="w-3 h-10 rounded-sm cursor-pointer"
          style={{ backgroundColor: track.color }}
        />

        {/* Track name */}
        <div className="flex-1 min-w-0">
          <input
            type="text"
            value={track.name}
            onChange={(e) => onUpdateTrack({ name: e.target.value })}
            className="w-full bg-transparent text-sm truncate outline-none focus:bg-ableton-bg px-1 rounded"
            onClick={(e) => e.stopPropagation()}
          />
          <div className="text-xs text-ableton-text-dim uppercase">
            {track.type}
          </div>
        </div>

        {/* Track controls */}
        <div className="flex items-center gap-1">
          {/* Mute */}
          <button
            className={clsx(
              'p-1 rounded-sm transition-colors',
              track.muted
                ? 'bg-ableton-yellow/30 text-ableton-yellow'
                : 'hover:bg-ableton-surface text-ableton-text-dim'
            )}
            onClick={(e) => {
              e.stopPropagation();
              onUpdateTrack({ muted: !track.muted });
            }}
            title="Mute"
          >
            {track.muted ? <VolumeX size={14} /> : <Volume2 size={14} />}
          </button>

          {/* Solo */}
          <button
            className={clsx(
              'p-1 rounded-sm transition-colors',
              track.solo
                ? 'bg-ableton-blue/30 text-ableton-blue'
                : 'hover:bg-ableton-surface text-ableton-text-dim'
            )}
            onClick={(e) => {
              e.stopPropagation();
              onUpdateTrack({ solo: !track.solo });
            }}
            title="Solo"
          >
            <Headphones size={14} />
          </button>

          {/* Arm for recording */}
          <button
            className={clsx(
              'p-1 rounded-sm transition-colors',
              track.armed
                ? 'bg-ableton-red/30 text-ableton-red'
                : 'hover:bg-ableton-surface text-ableton-text-dim'
            )}
            onClick={(e) => {
              e.stopPropagation();
              onUpdateTrack({ armed: !track.armed });
            }}
            title="Arm for Recording"
          >
            <CircleDot size={14} />
          </button>

          {/* Delete */}
          <button
            className="p-1 rounded-sm hover:bg-ableton-red/30 hover:text-ableton-red text-ableton-text-dim transition-colors"
            onClick={(e) => {
              e.stopPropagation();
              onRemoveTrack();
            }}
            title="Delete Track"
          >
            <Trash2 size={14} />
          </button>
        </div>
      </div>

      {/* Track Content (Clips) */}
      <div className="flex-1 relative">
        {/* Grid lines */}
        <div className="absolute inset-0 flex pointer-events-none">
          {Array.from({ length: TOTAL_BARS }, (_, i) => (
            <div
              key={i}
              className="border-r border-ableton-border/20"
              style={{ width: PIXELS_PER_BAR }}
            />
          ))}
        </div>

        {/* Clips */}
        {clips.map((clip) => (
          <div
            key={clip.id}
            className={clsx(
              'clip cursor-pointer',
              selectedClipId === clip.id && 'ring-2 ring-white'
            )}
            style={{
              left: clip.startBar * PIXELS_PER_BAR + 2,
              width: clip.lengthBars * PIXELS_PER_BAR - 4,
              backgroundColor: clip.color + '80',
              borderColor: clip.color,
            }}
            onClick={(e) => {
              e.stopPropagation();
              onSelectClip(clip.id);
            }}
          >
            <div className="px-2 py-1 text-xs truncate font-medium text-white">
              {clip.name}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
