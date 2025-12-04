import { useEffect, useCallback } from 'react';
import { useStore } from '../store/useStore';

// Tauri API - optional, will fallback if not available
let invoke: ((cmd: string, args?: Record<string, unknown>) => Promise<unknown>) | null = null;
try {
  // Dynamic import for optional Tauri dependency
  // eslint-disable-next-line @typescript-eslint/no-var-requires
  const tauriApi = require('@tauri-apps/api/core');
  invoke = tauriApi.invoke;
} catch {
  // Tauri not available, will use fallbacks
}

interface AudioEngineState {
  is_playing: boolean;
  position_samples: number;
  tempo_bpm: number;
  sample_rate: number;
}

export function useTauriAudio() {
  const {
    play,
    stop,
    pause,
    setTempo,
    setPosition,
    isPlaying,
    tempo,
  } = useStore();

  const handlePlay = useCallback(async () => {
    try {
      if (invoke) {
        await invoke('audio_play');
      }
      play();
    } catch (error) {
      console.error('Failed to play:', error);
      // Fallback to local state if Tauri is not available
      play();
    }
  }, [play]);

  const handleStop = useCallback(async () => {
    try {
      if (invoke) {
        await invoke('audio_stop');
      }
      stop();
    } catch (error) {
      console.error('Failed to stop:', error);
      stop();
    }
  }, [stop]);

  const handlePause = useCallback(async () => {
    try {
      if (invoke) {
        await invoke('audio_pause');
      }
      pause();
    } catch (error) {
      console.error('Failed to pause:', error);
      pause();
    }
  }, [pause]);

  const handleSetTempo = useCallback(async (bpm: number) => {
    try {
      if (invoke) {
        await invoke('audio_set_tempo', { bpm });
      }
      setTempo(bpm);
    } catch (error) {
      console.error('Failed to set tempo:', error);
      setTempo(bpm);
    }
  }, [setTempo]);

  const togglePlayPause = useCallback(async () => {
    if (isPlaying) {
      await handlePause();
    } else {
      await handlePlay();
    }
  }, [isPlaying, handlePlay, handlePause]);

  // Poll audio state every 100ms when playing
  useEffect(() => {
    if (!isPlaying) return;

    const interval = setInterval(async () => {
      try {
        if (invoke) {
          const state = await invoke('audio_get_state') as AudioEngineState;
          setPosition(state.position_samples);
        } else {
          // Fallback: simulate position advancement
          setPosition((prev: number) => prev + (tempo / 60) * 44100 * 0.1);
        }
      } catch {
        // Fallback: simulate position advancement
        const currentPosition = useStore.getState().position;
        setPosition(currentPosition + (tempo / 60) * 44100 * 0.1);
      }
    }, 100);

    return () => clearInterval(interval);
  }, [isPlaying, setPosition, tempo]);

  return {
    play: handlePlay,
    stop: handleStop,
    pause: handlePause,
    setTempo: handleSetTempo,
    togglePlayPause,
  };
}
