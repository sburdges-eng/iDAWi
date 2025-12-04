#pragma once

#include <atomic>
#include <cstdint>
#include <functional>
#include <memory>

namespace penta::transport {

// =============================================================================
// Transport Constants
// =============================================================================

constexpr double kDefaultTempo = 120.0;
constexpr double kMinTempo = 20.0;
constexpr double kMaxTempo = 999.0;
constexpr uint32_t kDefaultPPQ = 960;  // Pulses per quarter note (high resolution)
constexpr uint32_t kMidiPPQ = 24;      // MIDI clock PPQ

// =============================================================================
// Transport State
// =============================================================================

enum class TransportState : uint8_t {
    Stopped,    // Not playing, position can be anywhere
    Playing,    // Playing forward
    Recording,  // Playing and recording
    Paused      // Paused at current position (can resume)
};

// =============================================================================
// Time Signature
// =============================================================================

struct TimeSignature {
    uint8_t numerator = 4;      // Beats per bar (1-32)
    uint8_t denominator = 4;    // Beat unit (1, 2, 4, 8, 16, 32)

    constexpr TimeSignature() = default;
    constexpr TimeSignature(uint8_t num, uint8_t denom)
        : numerator(num), denominator(denom) {}

    // Get beat duration relative to quarter note
    constexpr double getBeatDuration() const noexcept {
        return 4.0 / static_cast<double>(denominator);
    }

    // Get bar duration in quarter notes
    constexpr double getBarDurationInQuarterNotes() const noexcept {
        return static_cast<double>(numerator) * getBeatDuration();
    }
};

// =============================================================================
// Loop Region
// =============================================================================

struct LoopRegion {
    uint64_t startSample = 0;
    uint64_t endSample = 0;
    bool enabled = false;

    constexpr bool isValid() const noexcept {
        return endSample > startSample;
    }

    constexpr uint64_t length() const noexcept {
        return endSample > startSample ? endSample - startSample : 0;
    }

    constexpr bool contains(uint64_t sample) const noexcept {
        return sample >= startSample && sample < endSample;
    }
};

// =============================================================================
// Transport Position
// =============================================================================
// High-precision position tracking in multiple time formats.
// All values are derived from the master sample position.
// =============================================================================

struct TransportPosition {
    // Master position (samples since start)
    uint64_t samples = 0;

    // Musical time (derived from samples + tempo)
    double quarterNotes = 0.0;      // Total quarter notes from start
    double beats = 0.0;             // Beats within current bar (0-based)
    uint32_t bars = 0;              // Bar number (0-based)

    // Wall clock time
    double seconds = 0.0;           // Total seconds from start

    // MIDI time
    uint32_t midiTicks = 0;         // 24 PPQ MIDI ticks

    // PPQ ticks (high resolution)
    uint64_t ppqTicks = 0;          // High-resolution ticks (960 PPQ default)

    // Tempo at this position
    double tempo = 120.0;

    // Time signature at this position
    TimeSignature timeSignature{4, 4};
};

// =============================================================================
// Callback Types
// =============================================================================

// Called when transport state changes
using TransportStateCallback = std::function<void(TransportState newState)>;

// Called when position changes (seek, loop, etc.)
using TransportPositionCallback = std::function<void(const TransportPosition& pos)>;

// Called when tempo changes
using TransportTempoCallback = std::function<void(double newTempo)>;

// Called when time signature changes
using TransportTimeSignatureCallback = std::function<void(const TimeSignature& ts)>;

// Called when loop region changes
using TransportLoopCallback = std::function<void(const LoopRegion& loop)>;

// =============================================================================
// Transport Configuration
// =============================================================================

struct TransportConfig {
    double sampleRate = 48000.0;
    double initialTempo = 120.0;
    TimeSignature initialTimeSignature{4, 4};
    uint32_t ppq = kDefaultPPQ;
    bool enableLooping = false;
    uint64_t loopStart = 0;
    uint64_t loopEnd = 0;
};

// =============================================================================
// Transport Interface
// =============================================================================
// Sample-accurate transport control with atomic state management.
// Designed for real-time audio processing with lock-free operation.
//
// Thread Safety:
// - All state queries are RT-safe (atomic reads)
// - All state changes are RT-safe (atomic writes)
// - Callbacks are NOT invoked from audio thread
//
// Usage Pattern:
// 1. Call advance() from audio thread each buffer
// 2. Query position/state as needed (RT-safe)
// 3. Control (play/pause/stop/seek) can be called from any thread
// =============================================================================

class Transport {
public:
    // =========================================================================
    // Construction / Destruction
    // =========================================================================

    Transport();
    explicit Transport(const TransportConfig& config);
    virtual ~Transport();

    // Non-copyable but movable
    Transport(const Transport&) = delete;
    Transport& operator=(const Transport&) = delete;
    Transport(Transport&&) noexcept;
    Transport& operator=(Transport&&) noexcept;

    // =========================================================================
    // Transport Control (thread-safe)
    // =========================================================================

    // Start playback from current position
    bool play() noexcept;

    // Pause at current position (resume with play())
    bool pause() noexcept;

    // Stop and optionally reset to start
    bool stop(bool resetPosition = true) noexcept;

    // Toggle between play and pause
    bool togglePlayPause() noexcept;

    // Start recording (also starts playback if stopped)
    bool record() noexcept;

    // Stop recording (continues playback if was recording)
    bool stopRecording() noexcept;

    // =========================================================================
    // State Queries (RT-safe)
    // =========================================================================

    TransportState getState() const noexcept;
    bool isPlaying() const noexcept;
    bool isPaused() const noexcept;
    bool isStopped() const noexcept;
    bool isRecording() const noexcept;

    // =========================================================================
    // Position Control (thread-safe)
    // =========================================================================

    // Set position in samples
    void setPosition(uint64_t samplePosition) noexcept;

    // Set position in seconds
    void setPositionSeconds(double seconds) noexcept;

    // Set position in quarter notes
    void setPositionQuarterNotes(double quarterNotes) noexcept;

    // Set position in bars/beats (0-based)
    void setPositionBarsBeats(uint32_t bars, double beats) noexcept;

    // Move position relative to current
    void movePosition(int64_t sampleDelta) noexcept;
    void movePositionBeats(double beatDelta) noexcept;

    // Jump to start (position 0)
    void rewind() noexcept;

    // =========================================================================
    // Position Queries (RT-safe)
    // =========================================================================

    // Get current position in samples
    uint64_t getPosition() const noexcept;

    // Get current position in seconds
    double getPositionSeconds() const noexcept;

    // Get current position in quarter notes
    double getPositionQuarterNotes() const noexcept;

    // Get full position info (updated during advance())
    TransportPosition getTransportPosition() const noexcept;

    // =========================================================================
    // Tempo Control (thread-safe)
    // =========================================================================

    // Set tempo in BPM (clamped to valid range)
    void setTempo(double bpm) noexcept;

    // Get current tempo
    double getTempo() const noexcept;

    // Tap tempo - call multiple times to set tempo from tap timing
    void tapTempo() noexcept;

    // Reset tap tempo state
    void resetTapTempo() noexcept;

    // =========================================================================
    // Time Signature (thread-safe)
    // =========================================================================

    void setTimeSignature(const TimeSignature& ts) noexcept;
    void setTimeSignature(uint8_t numerator, uint8_t denominator) noexcept;
    TimeSignature getTimeSignature() const noexcept;

    // =========================================================================
    // Loop Control (thread-safe)
    // =========================================================================

    // Enable/disable looping
    void setLoopEnabled(bool enabled) noexcept;
    bool isLoopEnabled() const noexcept;

    // Set loop points in samples
    void setLoopPoints(uint64_t startSample, uint64_t endSample) noexcept;

    // Set loop points in seconds
    void setLoopPointsSeconds(double startSeconds, double endSeconds) noexcept;

    // Set loop points in quarter notes
    void setLoopPointsQuarterNotes(double startQN, double endQN) noexcept;

    // Set loop points in bars (inclusive start, exclusive end)
    void setLoopBars(uint32_t startBar, uint32_t endBar) noexcept;

    // Get current loop region
    LoopRegion getLoopRegion() const noexcept;

    // =========================================================================
    // Audio Processing (call from audio thread)
    // =========================================================================

    // Advance transport by numSamples
    // Returns true if position wrapped due to loop
    bool advance(uint32_t numSamples) noexcept;

    // Get sample position within current buffer (for sample-accurate events)
    uint32_t getSampleOffsetForQuarterNote(double quarterNote) const noexcept;

    // Check if a quarter note position falls within current buffer
    bool isQuarterNoteInCurrentBuffer(double quarterNote,
                                      uint32_t bufferSize) const noexcept;

    // =========================================================================
    // Configuration
    // =========================================================================

    void setSampleRate(double sampleRate) noexcept;
    double getSampleRate() const noexcept;

    void setPPQ(uint32_t ppq) noexcept;
    uint32_t getPPQ() const noexcept;

    // =========================================================================
    // Callbacks (set from non-RT thread)
    // =========================================================================

    void setStateCallback(TransportStateCallback callback);
    void setPositionCallback(TransportPositionCallback callback);
    void setTempoCallback(TransportTempoCallback callback);
    void setTimeSignatureCallback(TransportTimeSignatureCallback callback);
    void setLoopCallback(TransportLoopCallback callback);

    // =========================================================================
    // Conversion Utilities (RT-safe)
    // =========================================================================

    // Convert between time units
    uint64_t secondsToSamples(double seconds) const noexcept;
    double samplesToSeconds(uint64_t samples) const noexcept;
    uint64_t quarterNotesToSamples(double quarterNotes) const noexcept;
    double samplesToQuarterNotes(uint64_t samples) const noexcept;
    uint64_t beatsToSamples(double beats) const noexcept;
    double samplesToBeats(uint64_t samples) const noexcept;

    // Bar/beat conversion
    uint64_t barsBeatsToSamples(uint32_t bars, double beats) const noexcept;
    void samplesToBarsBeats(uint64_t samples, uint32_t& bars,
                            double& beats) const noexcept;

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

// =============================================================================
// Factory Function
// =============================================================================

std::unique_ptr<Transport> createTransport();
std::unique_ptr<Transport> createTransport(const TransportConfig& config);

}  // namespace penta::transport
