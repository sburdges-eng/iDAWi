// Prevents additional console window on Windows in release
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod audio_engine;

use audio_engine::{AudioEngine, AudioEngineState};
use serde::{Deserialize, Serialize};
use std::process::{Command, Stdio};
use std::io::Write;
use std::sync::Mutex;
use tauri::State;

/// Application state managed by Tauri
struct AppState {
    audio_engine: Mutex<AudioEngine>,
}

/// Python bridge request format
#[derive(Serialize, Deserialize)]
struct PythonBridgeRequest {
    command: String,
    args: serde_json::Value,
}

/// Python bridge response format
#[derive(Serialize, Deserialize)]
struct PythonBridgeResponse {
    success: bool,
    data: Option<serde_json::Value>,
    error: Option<String>,
}

// ============================================================================
// Audio Engine Commands
// ============================================================================

#[tauri::command]
fn audio_play(state: State<AppState>) -> Result<(), String> {
    state.audio_engine.lock()
        .map_err(|e| e.to_string())?
        .play()
}

#[tauri::command]
fn audio_stop(state: State<AppState>) -> Result<(), String> {
    state.audio_engine.lock()
        .map_err(|e| e.to_string())?
        .stop()
}

#[tauri::command]
fn audio_pause(state: State<AppState>) -> Result<(), String> {
    state.audio_engine.lock()
        .map_err(|e| e.to_string())?
        .pause()
}

#[tauri::command]
fn audio_toggle_record(state: State<AppState>) -> Result<bool, String> {
    state.audio_engine.lock()
        .map_err(|e| e.to_string())?
        .toggle_record()
}

#[tauri::command]
fn audio_set_tempo(state: State<AppState>, bpm: f32) -> Result<(), String> {
    state.audio_engine.lock()
        .map_err(|e| e.to_string())?
        .set_tempo(bpm)
}

#[tauri::command]
fn audio_set_position(state: State<AppState>, samples: u64) -> Result<(), String> {
    state.audio_engine.lock()
        .map_err(|e| e.to_string())?
        .set_position(samples)
}

#[tauri::command]
fn audio_toggle_loop(state: State<AppState>) -> Result<bool, String> {
    state.audio_engine.lock()
        .map_err(|e| e.to_string())?
        .toggle_loop()
}

#[tauri::command]
fn audio_set_loop_points(state: State<AppState>, start: u64, end: u64) -> Result<(), String> {
    state.audio_engine.lock()
        .map_err(|e| e.to_string())?
        .set_loop_points(start, end)
}

#[tauri::command]
fn audio_get_state(state: State<AppState>) -> Result<AudioEngineState, String> {
    state.audio_engine.lock()
        .map_err(|e| e.to_string())?
        .get_state()
}

// ============================================================================
// Python Music Brain Commands
// ============================================================================

#[tauri::command]
async fn music_brain_command(
    command: String,
    args: serde_json::Value
) -> Result<PythonBridgeResponse, String> {
    let request = PythonBridgeRequest { command, args };
    let request_json = serde_json::to_string(&request)
        .map_err(|e| format!("Failed to serialize request: {}", e))?;

    // Try to call Python bridge script
    let result = Command::new("python3")
        .arg("music-brain/bridge.py")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn();

    match result {
        Ok(mut child) => {
            // Write request to stdin
            if let Some(mut stdin) = child.stdin.take() {
                let _ = stdin.write_all(request_json.as_bytes());
            }

            // Read response from stdout
            let output = child.wait_with_output()
                .map_err(|e| format!("Failed to read output: {}", e))?;

            if output.status.success() {
                let response: PythonBridgeResponse = serde_json::from_slice(&output.stdout)
                    .unwrap_or(PythonBridgeResponse {
                        success: false,
                        data: None,
                        error: Some("Failed to parse Python response".to_string()),
                    });
                Ok(response)
            } else {
                let stderr = String::from_utf8_lossy(&output.stderr);
                Ok(PythonBridgeResponse {
                    success: false,
                    data: None,
                    error: Some(format!("Python error: {}", stderr)),
                })
            }
        }
        Err(e) => {
            // Python not available, return fallback response
            Ok(PythonBridgeResponse {
                success: false,
                data: None,
                error: Some(format!("Python bridge not available: {}", e)),
            })
        }
    }
}

// ============================================================================
// Main Entry Point
// ============================================================================

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .manage(AppState {
            audio_engine: Mutex::new(AudioEngine::new()),
        })
        .invoke_handler(tauri::generate_handler![
            // Audio commands
            audio_play,
            audio_stop,
            audio_pause,
            audio_toggle_record,
            audio_set_tempo,
            audio_set_position,
            audio_toggle_loop,
            audio_set_loop_points,
            audio_get_state,
            // Python bridge
            music_brain_command,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
