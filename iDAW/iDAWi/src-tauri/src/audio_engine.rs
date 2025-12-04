//! iDAWi Audio Engine
//! Lightweight audio state management with Rust

use serde::{Deserialize, Serialize};
use std::sync::{Arc, Mutex};

/// Audio engine state
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AudioEngineState {
    pub is_playing: bool,
    pub is_recording: bool,
    pub position_samples: u64,
    pub tempo_bpm: f32,
    pub sample_rate: u32,
    pub loop_enabled: bool,
    pub loop_start: u64,
    pub loop_end: u64,
}

impl Default for AudioEngineState {
    fn default() -> Self {
        Self {
            is_playing: false,
            is_recording: false,
            position_samples: 0,
            tempo_bpm: 120.0,
            sample_rate: 44100,
            loop_enabled: false,
            loop_start: 0,
            loop_end: 44100 * 8, // 8 seconds default loop
        }
    }
}

/// Main audio engine struct
pub struct AudioEngine {
    state: Arc<Mutex<AudioEngineState>>,
}

impl AudioEngine {
    /// Create a new audio engine instance
    pub fn new() -> Self {
        Self {
            state: Arc::new(Mutex::new(AudioEngineState::default())),
        }
    }

    /// Start playback
    pub fn play(&self) -> Result<(), String> {
        let mut state = self.state.lock().map_err(|e| e.to_string())?;
        state.is_playing = true;
        Ok(())
    }

    /// Stop playback and reset position
    pub fn stop(&self) -> Result<(), String> {
        let mut state = self.state.lock().map_err(|e| e.to_string())?;
        state.is_playing = false;
        state.is_recording = false;
        state.position_samples = 0;
        Ok(())
    }

    /// Pause playback (maintain position)
    pub fn pause(&self) -> Result<(), String> {
        let mut state = self.state.lock().map_err(|e| e.to_string())?;
        state.is_playing = false;
        Ok(())
    }

    /// Toggle recording state
    pub fn toggle_record(&self) -> Result<bool, String> {
        let mut state = self.state.lock().map_err(|e| e.to_string())?;
        state.is_recording = !state.is_recording;
        Ok(state.is_recording)
    }

    /// Set tempo in BPM
    pub fn set_tempo(&self, bpm: f32) -> Result<(), String> {
        if bpm < 20.0 || bpm > 300.0 {
            return Err("Tempo must be between 20 and 300 BPM".to_string());
        }
        let mut state = self.state.lock().map_err(|e| e.to_string())?;
        state.tempo_bpm = bpm;
        Ok(())
    }

    /// Set playback position in samples
    pub fn set_position(&self, samples: u64) -> Result<(), String> {
        let mut state = self.state.lock().map_err(|e| e.to_string())?;
        state.position_samples = samples;
        Ok(())
    }

    /// Toggle loop mode
    pub fn toggle_loop(&self) -> Result<bool, String> {
        let mut state = self.state.lock().map_err(|e| e.to_string())?;
        state.loop_enabled = !state.loop_enabled;
        Ok(state.loop_enabled)
    }

    /// Set loop points
    pub fn set_loop_points(&self, start: u64, end: u64) -> Result<(), String> {
        if start >= end {
            return Err("Loop start must be before loop end".to_string());
        }
        let mut state = self.state.lock().map_err(|e| e.to_string())?;
        state.loop_start = start;
        state.loop_end = end;
        Ok(())
    }

    /// Get current state
    pub fn get_state(&self) -> Result<AudioEngineState, String> {
        let state = self.state.lock().map_err(|e| e.to_string())?;
        Ok(state.clone())
    }

    /// Advance position by given number of samples (called during playback)
    pub fn advance(&self, frames: u64) -> Result<(), String> {
        let mut state = self.state.lock().map_err(|e| e.to_string())?;
        if state.is_playing {
            state.position_samples += frames;

            // Handle loop
            if state.loop_enabled && state.position_samples >= state.loop_end {
                state.position_samples = state.loop_start;
            }
        }
        Ok(())
    }
}

impl Default for AudioEngine {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_play_stop() {
        let engine = AudioEngine::new();

        assert!(!engine.get_state().unwrap().is_playing);
        engine.play().unwrap();
        assert!(engine.get_state().unwrap().is_playing);
        engine.stop().unwrap();
        assert!(!engine.get_state().unwrap().is_playing);
        assert_eq!(engine.get_state().unwrap().position_samples, 0);
    }

    #[test]
    fn test_tempo() {
        let engine = AudioEngine::new();

        assert_eq!(engine.get_state().unwrap().tempo_bpm, 120.0);
        engine.set_tempo(140.0).unwrap();
        assert_eq!(engine.get_state().unwrap().tempo_bpm, 140.0);

        // Invalid tempo
        assert!(engine.set_tempo(10.0).is_err());
        assert!(engine.set_tempo(400.0).is_err());
    }

    #[test]
    fn test_loop() {
        let engine = AudioEngine::new();

        assert!(!engine.get_state().unwrap().loop_enabled);
        engine.toggle_loop().unwrap();
        assert!(engine.get_state().unwrap().loop_enabled);

        engine.set_loop_points(44100, 88200).unwrap();
        let state = engine.get_state().unwrap();
        assert_eq!(state.loop_start, 44100);
        assert_eq!(state.loop_end, 88200);
    }
}
