import React from 'react';
import {
  Plus,
  Undo2,
  Redo2,
  Save,
  FolderOpen,
  Settings,
  FlipHorizontal,
} from 'lucide-react';
import { useStore } from '../../store/useStore';

export const Toolbar: React.FC = () => {
  const { addTrack, toggleSide } = useStore();

  return (
    <div className="h-10 bg-ableton-surface border-b border-ableton-border flex items-center px-2 gap-1">
      {/* File operations */}
      <div className="flex items-center gap-1 pr-2 border-r border-ableton-border">
        <button className="btn-ableton-icon" title="New Project (⌘N)">
          <FolderOpen size={16} />
        </button>
        <button className="btn-ableton-icon" title="Save (⌘S)">
          <Save size={16} />
        </button>
      </div>

      {/* Edit operations */}
      <div className="flex items-center gap-1 px-2 border-r border-ableton-border">
        <button className="btn-ableton-icon" title="Undo (⌘Z)">
          <Undo2 size={16} />
        </button>
        <button className="btn-ableton-icon" title="Redo (⌘⇧Z)">
          <Redo2 size={16} />
        </button>
      </div>

      {/* Track operations */}
      <div className="flex items-center gap-1 px-2 border-r border-ableton-border">
        <button
          className="btn-ableton-icon"
          title="Add MIDI Track"
          onClick={() => addTrack({
            name: 'New Track',
            type: 'midi',
            color: '#00aaff',
            volume: 0.7,
            pan: 0,
            muted: false,
            solo: false,
            armed: false,
            clips: [],
          })}
        >
          <Plus size={16} />
        </button>
      </div>

      {/* Spacer */}
      <div className="flex-1" />

      {/* iDAWi Logo/Title */}
      <div className="px-4 text-ableton-text-dim font-medium text-sm">
        iDAWi
      </div>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Right side tools */}
      <div className="flex items-center gap-1 pl-2 border-l border-ableton-border">
        <button className="btn-ableton-icon" title="Settings">
          <Settings size={16} />
        </button>
        <button
          className="btn-ableton-icon bg-ableton-accent/20 hover:bg-ableton-accent/40"
          title="Flip to Emotion Interface (⌘E)"
          onClick={toggleSide}
        >
          <FlipHorizontal size={16} className="text-ableton-accent" />
        </button>
      </div>
    </div>
  );
};
