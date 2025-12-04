import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// Types
export interface Track {
  id: string;
  name: string;
  color: string;
  muted: boolean;
  solo: boolean;
  armed: boolean;
  volume: number;
  pan: number;
  type: 'audio' | 'midi' | 'bus';
}

export interface Clip {
  id: string;
  trackId: string;
  name: string;
  startBar: number;
  lengthBars: number;
  color: string;
}

export interface SongIntent {
  coreEmotion: string;
  subEmotion: string;
  vulnerabilityScale: number;
  narrativeArc: 'ascending' | 'descending' | 'circular' | 'static';
  ruleToBreak: string | null;
}

export interface GhostWriterSuggestion {
  id: string;
  type: 'harmony' | 'rhythm' | 'production' | 'arrangement';
  description: string;
  emotionalRationale: string;
  applied: boolean;
}

interface AppState {
  // UI State
  currentSide: 'A' | 'B';
  isFlipping: boolean;
  toggleSide: () => void;

  // Audio State
  isPlaying: boolean;
  isRecording: boolean;
  position: number;  // in samples
  tempo: number;
  timeSignature: { numerator: number; denominator: number };
  loopEnabled: boolean;
  loopStart: number;
  loopEnd: number;

  // Tracks
  tracks: Track[];
  selectedTrackId: string | null;
  addTrack: (type: Track['type']) => void;
  removeTrack: (id: string) => void;
  updateTrack: (id: string, updates: Partial<Track>) => void;
  selectTrack: (id: string | null) => void;

  // Clips
  clips: Clip[];
  selectedClipId: string | null;
  addClip: (clip: Omit<Clip, 'id'>) => void;
  removeClip: (id: string) => void;
  updateClip: (id: string, updates: Partial<Clip>) => void;
  selectClip: (id: string | null) => void;

  // Transport Actions
  play: () => void;
  stop: () => void;
  pause: () => void;
  toggleRecord: () => void;
  setPosition: (pos: number) => void;
  setTempo: (bpm: number) => void;
  setTimeSignature: (num: number, den: number) => void;
  toggleLoop: () => void;
  setLoopPoints: (start: number, end: number) => void;

  // Side B - Emotion Interface
  songIntent: SongIntent;
  updateSongIntent: (updates: Partial<SongIntent>) => void;

  // Ghost Writer
  ghostWriterSuggestions: GhostWriterSuggestion[];
  addGhostWriterSuggestion: (suggestion: Omit<GhostWriterSuggestion, 'id' | 'applied'>) => void;
  applySuggestion: (id: string) => void;
  clearSuggestions: () => void;
}

const generateId = () => Math.random().toString(36).substring(2, 11);

const defaultTrackColors = ['#ff7e3e', '#0066ff', '#00cc00', '#ff3366', '#9933ff', '#ffcc00'];

export const useStore = create<AppState>()(
  persist(
    (set) => ({
      // UI State
      currentSide: 'A',
      isFlipping: false,
      toggleSide: () => {
        set({ isFlipping: true });
        setTimeout(() => {
          set((state) => ({
            currentSide: state.currentSide === 'A' ? 'B' : 'A',
            isFlipping: false,
          }));
        }, 300);
      },

      // Audio State
      isPlaying: false,
      isRecording: false,
      position: 0,
      tempo: 120,
      timeSignature: { numerator: 4, denominator: 4 },
      loopEnabled: false,
      loopStart: 0,
      loopEnd: 8 * 44100 * 4, // 8 bars at 120bpm

      // Tracks
      tracks: [
        { id: '1', name: 'Drums', color: '#ff7e3e', muted: false, solo: false, armed: false, volume: 0.8, pan: 0, type: 'midi' },
        { id: '2', name: 'Bass', color: '#0066ff', muted: false, solo: false, armed: false, volume: 0.75, pan: 0, type: 'midi' },
        { id: '3', name: 'Keys', color: '#00cc00', muted: false, solo: false, armed: false, volume: 0.7, pan: -0.2, type: 'midi' },
        { id: '4', name: 'Vocal', color: '#ff3366', muted: false, solo: false, armed: false, volume: 0.85, pan: 0, type: 'audio' },
      ],
      selectedTrackId: null,

      addTrack: (type) => set((state) => ({
        tracks: [...state.tracks, {
          id: generateId(),
          name: `${type.charAt(0).toUpperCase() + type.slice(1)} ${state.tracks.length + 1}`,
          color: defaultTrackColors[state.tracks.length % defaultTrackColors.length],
          muted: false,
          solo: false,
          armed: false,
          volume: 0.8,
          pan: 0,
          type,
        }],
      })),

      removeTrack: (id) => set((state) => ({
        tracks: state.tracks.filter((t) => t.id !== id),
        clips: state.clips.filter((c) => c.trackId !== id),
        selectedTrackId: state.selectedTrackId === id ? null : state.selectedTrackId,
      })),

      updateTrack: (id, updates) => set((state) => ({
        tracks: state.tracks.map((t) => t.id === id ? { ...t, ...updates } : t),
      })),

      selectTrack: (id) => set({ selectedTrackId: id }),

      // Clips
      clips: [
        { id: 'c1', trackId: '1', name: 'Beat', startBar: 0, lengthBars: 4, color: '#ff7e3e' },
        { id: 'c2', trackId: '2', name: 'Bass Line', startBar: 4, lengthBars: 8, color: '#0066ff' },
        { id: 'c3', trackId: '3', name: 'Chords', startBar: 0, lengthBars: 8, color: '#00cc00' },
      ],
      selectedClipId: null,

      addClip: (clip) => set((state) => ({
        clips: [...state.clips, { ...clip, id: generateId() }],
      })),

      removeClip: (id) => set((state) => ({
        clips: state.clips.filter((c) => c.id !== id),
        selectedClipId: state.selectedClipId === id ? null : state.selectedClipId,
      })),

      updateClip: (id, updates) => set((state) => ({
        clips: state.clips.map((c) => c.id === id ? { ...c, ...updates } : c),
      })),

      selectClip: (id) => set({ selectedClipId: id }),

      // Transport Actions
      play: () => set({ isPlaying: true }),
      stop: () => set({ isPlaying: false, isRecording: false, position: 0 }),
      pause: () => set({ isPlaying: false }),
      toggleRecord: () => set((state) => ({ isRecording: !state.isRecording })),
      setPosition: (pos) => set({ position: pos }),
      setTempo: (tempo) => set({ tempo: Math.min(300, Math.max(20, tempo)) }),
      setTimeSignature: (num, den) => set({ timeSignature: { numerator: num, denominator: den } }),
      toggleLoop: () => set((state) => ({ loopEnabled: !state.loopEnabled })),
      setLoopPoints: (start, end) => set({ loopStart: start, loopEnd: end }),

      // Side B - Emotion Interface
      songIntent: {
        coreEmotion: 'grief',
        subEmotion: 'yearning',
        vulnerabilityScale: 7,
        narrativeArc: 'ascending',
        ruleToBreak: null,
      },

      updateSongIntent: (updates) => set((state) => ({
        songIntent: { ...state.songIntent, ...updates },
      })),

      // Ghost Writer
      ghostWriterSuggestions: [],

      addGhostWriterSuggestion: (suggestion) => set((state) => ({
        ghostWriterSuggestions: [
          ...state.ghostWriterSuggestions,
          { ...suggestion, id: generateId(), applied: false },
        ],
      })),

      applySuggestion: (id) => set((state) => ({
        ghostWriterSuggestions: state.ghostWriterSuggestions.map((s) =>
          s.id === id ? { ...s, applied: true } : s
        ),
      })),

      clearSuggestions: () => set({ ghostWriterSuggestions: [] }),
    }),
    {
      name: 'idawi-storage',
      partialize: (state) => ({
        tempo: state.tempo,
        timeSignature: state.timeSignature,
        songIntent: state.songIntent,
      }),
    }
  )
);
