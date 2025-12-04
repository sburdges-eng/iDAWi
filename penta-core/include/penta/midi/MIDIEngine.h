#pragma once

#include "penta/midi/MIDITypes.h"
#include "penta/midi/MIDIBuffer.h"
#include <atomic>
#include <cstdint>
#include <functional>
#include <memory>
#include <mutex>
#include <string>
#include <vector>

namespace penta::midi {

// =============================================================================
// Forward Declarations
// =============================================================================

class MIDIEngineImpl;

// =============================================================================
// Callback Types
// =============================================================================

// Called when MIDI input is received (from input thread)
using MIDIInputCallback = std::function<void(const MIDIEvent& event)>;

// Called when tempo is received from external MIDI clock
using MIDITempoCallback = std::function<void(double bpm)>;

// Called when transport commands are received (Start/Stop/Continue)
using MIDITransportCallback = std::function<void(MIDIEventType type)>;

// Called when song position changes
using MIDISongPositionCallback = std::function<void(uint32_t beats)>;

// =============================================================================
// MIDI Clock Synchronization Mode
// =============================================================================

enum class MIDIClockMode {
    Internal,       // Generate MIDI clock from internal tempo
    External,       // Sync to incoming MIDI clock
    Auto            // Auto-detect: use external if available
};

// =============================================================================
// MIDI Engine Configuration
// =============================================================================

struct MIDIEngineConfig {
    double sampleRate = 48000.0;
    size_t inputBufferSize = 4096;
    size_t outputBufferSize = 4096;
    bool enableSysEx = true;
    bool enableActiveSensing = false;
    bool enableTimeCode = false;
    MIDIClockMode clockMode = MIDIClockMode::Internal;
    double defaultTempo = 120.0;
};

// =============================================================================
// MIDI Engine Interface
// =============================================================================
// Central MIDI management class providing:
// - Device enumeration and management
// - RT-safe event buffering
// - MIDI clock synchronization
// - State tracking across all channels
//
// Thread Safety:
// - Device operations are protected by mutex (non-RT safe)
// - Event buffering uses lock-free structures (RT-safe)
// - Callbacks are invoked from input thread (not audio thread)
// =============================================================================

class MIDIEngine {
public:
    // =========================================================================
    // Construction / Destruction
    // =========================================================================

    MIDIEngine();
    explicit MIDIEngine(const MIDIEngineConfig& config);
    virtual ~MIDIEngine();

    // Non-copyable, non-movable
    MIDIEngine(const MIDIEngine&) = delete;
    MIDIEngine& operator=(const MIDIEngine&) = delete;

    // =========================================================================
    // Initialization
    // =========================================================================

    // Initialize the MIDI system (call once at startup)
    bool initialize();

    // Shutdown and release all resources
    void shutdown();

    // Check if engine is initialized
    bool isInitialized() const noexcept;

    // =========================================================================
    // Device Enumeration
    // =========================================================================

    // Refresh device list (call when devices might have changed)
    void refreshDevices();

    // Get all available input devices
    std::vector<MIDIDeviceInfo> getInputDevices() const;

    // Get all available output devices
    std::vector<MIDIDeviceInfo> getOutputDevices() const;

    // Get device info by ID
    bool getInputDeviceInfo(uint32_t deviceId, MIDIDeviceInfo& info) const;
    bool getOutputDeviceInfo(uint32_t deviceId, MIDIDeviceInfo& info) const;

    // =========================================================================
    // Device Control
    // =========================================================================

    // Open/close input devices
    bool openInputDevice(uint32_t deviceId);
    bool closeInputDevice(uint32_t deviceId);
    bool isInputDeviceOpen(uint32_t deviceId) const;

    // Open/close output devices
    bool openOutputDevice(uint32_t deviceId);
    bool closeOutputDevice(uint32_t deviceId);
    bool isOutputDeviceOpen(uint32_t deviceId) const;

    // Open all devices matching name pattern (returns count opened)
    size_t openInputDevicesByName(const std::string& namePattern);
    size_t openOutputDevicesByName(const std::string& namePattern);

    // Close all open devices
    void closeAllInputDevices();
    void closeAllOutputDevices();
    void closeAllDevices();

    // =========================================================================
    // Virtual Ports (for software interconnection)
    // =========================================================================

    // Create a virtual input port (other apps can send MIDI to us)
    bool createVirtualInput(const std::string& portName);

    // Create a virtual output port (other apps can receive our MIDI)
    bool createVirtualOutput(const std::string& portName);

    // Close virtual ports
    bool closeVirtualInput();
    bool closeVirtualOutput();

    // =========================================================================
    // MIDI Input (RT-safe operations)
    // =========================================================================

    // Drain incoming MIDI to buffer (call from audio thread)
    // Returns number of events drained
    size_t drainInputToBuffer(MIDIBuffer& buffer) noexcept;

    // Check if there are pending input events
    bool hasInputEvents() const noexcept;

    // Get approximate pending event count
    size_t pendingInputCount() const noexcept;

    // =========================================================================
    // MIDI Output (RT-safe operations)
    // =========================================================================

    // Send a single MIDI event immediately (RT-safe)
    bool sendEvent(const MIDIEvent& event) noexcept;

    // Send all events from buffer (RT-safe)
    size_t sendBuffer(const MIDIBuffer& buffer) noexcept;

    // Queue event for sending (batched send on flush)
    bool queueEvent(const MIDIEvent& event) noexcept;

    // Send all queued events
    size_t flushOutput() noexcept;

    // Convenience send methods
    bool sendNoteOn(uint8_t channel, uint8_t note, uint8_t velocity) noexcept;
    bool sendNoteOff(uint8_t channel, uint8_t note, uint8_t velocity = 0) noexcept;
    bool sendControlChange(uint8_t channel, uint8_t controller, uint8_t value) noexcept;
    bool sendProgramChange(uint8_t channel, uint8_t program) noexcept;
    bool sendPitchBend(uint8_t channel, int16_t value) noexcept;

    // All notes off (channel 0-15, or 255 for all channels)
    void sendAllNotesOff(uint8_t channel = 255) noexcept;

    // Reset all controllers on channel
    void sendResetAllControllers(uint8_t channel = 255) noexcept;

    // =========================================================================
    // MIDI Clock Synchronization
    // =========================================================================

    // Set clock mode
    void setClockMode(MIDIClockMode mode);
    MIDIClockMode getClockMode() const noexcept;

    // Set internal tempo (when in Internal mode)
    void setTempo(double bpm);
    double getTempo() const noexcept;

    // Get tempo from external clock (when in External mode)
    double getExternalTempo() const noexcept;

    // Check if receiving external clock
    bool isReceivingExternalClock() const noexcept;

    // Send MIDI clock messages (call from audio thread at sample rate)
    // ppq = pulses per quarter note (standard is 24)
    void processClockOutput(uint32_t numSamples, double sampleRate);

    // Send transport commands
    void sendStart();
    void sendStop();
    void sendContinue();
    void sendSongPosition(uint32_t beats);

    // =========================================================================
    // Callbacks
    // =========================================================================

    // Set callback for incoming MIDI events
    void setInputCallback(MIDIInputCallback callback);

    // Set callback for tempo changes from external clock
    void setTempoCallback(MIDITempoCallback callback);

    // Set callback for transport commands (Start/Stop/Continue)
    void setTransportCallback(MIDITransportCallback callback);

    // Set callback for song position changes
    void setSongPositionCallback(MIDISongPositionCallback callback);

    // =========================================================================
    // State Access
    // =========================================================================

    // Get current MIDI state (channel values, notes, etc.)
    const MIDIState& getState() const noexcept;

    // Reset all state to defaults
    void resetState() noexcept;

    // =========================================================================
    // Configuration
    // =========================================================================

    // Update sample rate (call when audio engine sample rate changes)
    void setSampleRate(double sampleRate);
    double getSampleRate() const noexcept;

    // Get configuration
    const MIDIEngineConfig& getConfig() const noexcept;

    // =========================================================================
    // Statistics / Diagnostics
    // =========================================================================

    struct Statistics {
        std::atomic<uint64_t> eventsReceived{0};
        std::atomic<uint64_t> eventsSent{0};
        std::atomic<uint64_t> eventsDropped{0};
        std::atomic<uint64_t> clockTicksReceived{0};
        std::atomic<uint64_t> clockTicksSent{0};
        std::atomic<uint64_t> lastEventTimestamp{0};
    };

    const Statistics& getStatistics() const noexcept;
    void resetStatistics() noexcept;

private:
    std::unique_ptr<MIDIEngineImpl> impl_;
};

// =============================================================================
// Factory Function
// =============================================================================

std::unique_ptr<MIDIEngine> createMIDIEngine();
std::unique_ptr<MIDIEngine> createMIDIEngine(const MIDIEngineConfig& config);

}  // namespace penta::midi
