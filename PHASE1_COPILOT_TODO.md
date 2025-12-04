# Phase 1: Real-Time Audio Engine - Copilot Agent TODO

## Overview

This document provides a complete, actionable task list for implementing Phase 1 of iDAWi - the Real-Time Audio Engine. Each task includes specific implementation details, file locations, dependencies, and acceptance criteria.

**Target Directory**: `/home/user/iDAWi/penta-core/`
**Language**: C++20
**Build System**: CMake
**Test Framework**: GoogleTest

---

## Prerequisites

Before starting, ensure:
- [ ] Phase 0 is complete (all core algorithms implemented)
- [ ] Build system working (`./build.sh` succeeds)
- [ ] Tests passing (`./test.sh` succeeds)

---

## Task Execution Order

Execute sections in this order due to dependencies:
1. **1.1 Audio I/O Foundation** (no dependencies)
2. **1.2 MIDI Engine** (no dependencies, can parallel with 1.1)
3. **1.3 Transport System** (depends on 1.1, 1.2)
4. **1.4 Mixer Engine** (depends on 1.1)
5. **1.5 Audio Processing Graph** (depends on 1.4)
6. **1.6 Built-in DSP Effects** (depends on 1.5)
7. **1.7 Audio Recording** (depends on 1.1, 1.3)

---

## 1.1 Audio I/O Foundation

### 1.1.1 Create Audio Backend Abstraction

**Files to create:**
```
penta-core/include/penta/audio/AudioBackend.h
penta-core/include/penta/audio/AudioDevice.h
penta-core/include/penta/audio/AudioBuffer.h
penta-core/src/audio/AudioBackend.cpp
penta-core/src/audio/AudioDevice.cpp
penta-core/src/audio/AudioBuffer.cpp
```

**AudioBackend.h interface:**
```cpp
namespace penta::audio {

struct AudioDeviceInfo {
    std::string id;
    std::string name;
    int maxInputChannels;
    int maxOutputChannels;
    std::vector<int> supportedSampleRates;
    std::vector<int> supportedBufferSizes;
    bool isDefault;
};

struct AudioStreamConfig {
    std::string deviceId;
    int sampleRate = 48000;          // 44100, 48000, 88200, 96000, 192000
    int bufferSize = 256;            // 64-4096
    int inputChannels = 2;
    int outputChannels = 2;
    enum class BitDepth { Int16, Int24, Float32 } bitDepth = BitDepth::Float32;
};

using AudioCallback = std::function<void(
    const float* const* inputBuffers,
    float* const* outputBuffers,
    int numFrames,
    int64_t sampleTime
)>;

class AudioBackend {
public:
    virtual ~AudioBackend() = default;

    // Device enumeration
    virtual std::vector<AudioDeviceInfo> getInputDevices() = 0;
    virtual std::vector<AudioDeviceInfo> getOutputDevices() = 0;
    virtual AudioDeviceInfo getDefaultInputDevice() = 0;
    virtual AudioDeviceInfo getDefaultOutputDevice() = 0;

    // Stream management
    virtual bool openStream(const AudioStreamConfig& config) = 0;
    virtual void closeStream() = 0;
    virtual bool startStream() = 0;
    virtual void stopStream() = 0;
    virtual bool isStreamRunning() const = 0;

    // Callback
    virtual void setCallback(AudioCallback callback) = 0;

    // Latency
    virtual double getInputLatency() const = 0;
    virtual double getOutputLatency() const = 0;

    // Error handling
    virtual std::string getLastError() const = 0;

    // Factory
    static std::unique_ptr<AudioBackend> create();
};

} // namespace penta::audio
```

**Acceptance Criteria:**
- [ ] Abstract interface compiles
- [ ] Factory method detects platform and returns appropriate backend
- [ ] Unit tests for AudioBuffer class

---

### 1.1.2 Implement Platform-Specific Backends

**macOS - CoreAudio:**
```
penta-core/src/audio/backends/CoreAudioBackend.h
penta-core/src/audio/backends/CoreAudioBackend.cpp
```

**Implementation notes:**
- Use `AudioObjectGetPropertyData` for device enumeration
- Use `AudioDeviceCreateIOProcID` for callback registration
- Handle `kAudioDevicePropertyBufferFrameSize` for buffer size
- Handle `kAudioDevicePropertyNominalSampleRate` for sample rate

**Windows - WASAPI:**
```
penta-core/src/audio/backends/WASAPIBackend.h
penta-core/src/audio/backends/WASAPIBackend.cpp
```

**Implementation notes:**
- Use `IMMDeviceEnumerator` for device enumeration
- Use `IAudioClient` in exclusive mode for low latency
- Handle `AUDCLNT_STREAMFLAGS_EVENTCALLBACK` for callback
- Support both shared and exclusive modes

**Linux - ALSA/PipeWire:**
```
penta-core/src/audio/backends/ALSABackend.h
penta-core/src/audio/backends/ALSABackend.cpp
penta-core/src/audio/backends/PipeWireBackend.h
penta-core/src/audio/backends/PipeWireBackend.cpp
```

**Implementation notes:**
- ALSA: Use `snd_pcm_open`, `snd_pcm_hw_params_set_*`
- PipeWire: Use `pw_stream_new`, `pw_stream_connect`
- Auto-detect PipeWire availability, fallback to ALSA

**Acceptance Criteria:**
- [ ] Each backend compiles on its target platform
- [ ] Device enumeration returns valid devices
- [ ] Audio callback fires at correct intervals
- [ ] Latency reporting is accurate within 1ms

---

### 1.1.3 Implement Sample Rate Conversion

**Files:**
```
penta-core/include/penta/audio/SampleRateConverter.h
penta-core/src/audio/SampleRateConverter.cpp
```

**Algorithm:** Windowed sinc interpolation (high quality) or linear (low latency mode)

```cpp
class SampleRateConverter {
public:
    enum class Quality { Low, Medium, High };

    SampleRateConverter(int sourceRate, int targetRate, Quality quality = Quality::High);

    // Process interleaved audio
    void process(const float* input, int inputFrames,
                 float* output, int& outputFrames);

    // Get required output buffer size
    int getRequiredOutputFrames(int inputFrames) const;

    // Reset internal state
    void reset();

private:
    int sourceRate_, targetRate_;
    double ratio_;
    std::vector<float> sincTable_;
    std::vector<float> history_;
};
```

**Acceptance Criteria:**
- [ ] Supports all standard rates: 44100, 48000, 88200, 96000, 192000
- [ ] THD+N < -100dB for high quality mode
- [ ] Latency < 64 samples for low quality mode
- [ ] Unit tests with swept sine verify no aliasing

---

### 1.1.4 Implement Audio Routing Matrix

**Files:**
```
penta-core/include/penta/audio/AudioRouter.h
penta-core/src/audio/AudioRouter.cpp
```

```cpp
class AudioRouter {
public:
    struct Route {
        int sourceChannel;
        int destChannel;
        float gain = 1.0f;
        bool muted = false;
    };

    void addRoute(const Route& route);
    void removeRoute(int sourceChannel, int destChannel);
    void setRouteGain(int sourceChannel, int destChannel, float gain);
    void clearAllRoutes();

    // RT-safe: process audio through routing matrix
    void process(const float* const* inputs, int numInputs,
                 float* const* outputs, int numOutputs,
                 int numFrames) noexcept;

private:
    std::vector<Route> routes_;
    std::mutex routeMutex_;  // Only for configuration changes
};
```

**Acceptance Criteria:**
- [ ] Arbitrary N-to-M channel routing
- [ ] RT-safe processing (no allocations)
- [ ] Gain changes apply without clicks (smoothing)
- [ ] Unit tests verify signal flow

---

### 1.1.5 Implement Audio Stream Monitor

**Files:**
```
penta-core/include/penta/audio/AudioStreamMonitor.h
penta-core/src/audio/AudioStreamMonitor.cpp
```

**Features:**
- Detect buffer underruns/overruns
- Track callback timing jitter
- Report CPU usage in audio thread
- Auto-recovery from stream errors

**Acceptance Criteria:**
- [ ] Detects underruns within 1 callback
- [ ] Reports accurate CPU percentage
- [ ] Auto-restarts stream on recoverable errors
- [ ] Logs errors without blocking audio thread

---

## 1.2 MIDI Engine

### 1.2.1 Create MIDI Backend Abstraction

**Files:**
```
penta-core/include/penta/midi/MIDIBackend.h
penta-core/include/penta/midi/MIDIMessage.h
penta-core/include/penta/midi/MIDIPort.h
penta-core/src/midi/MIDIBackend.cpp
penta-core/src/midi/MIDIMessage.cpp
```

**MIDIMessage.h:**
```cpp
namespace penta::midi {

struct MIDIMessage {
    enum class Type : uint8_t {
        NoteOff = 0x80,
        NoteOn = 0x90,
        PolyPressure = 0xA0,
        ControlChange = 0xB0,
        ProgramChange = 0xC0,
        ChannelPressure = 0xD0,
        PitchBend = 0xE0,
        SysEx = 0xF0,
        MTC = 0xF1,
        SongPosition = 0xF2,
        Clock = 0xF8,
        Start = 0xFA,
        Continue = 0xFB,
        Stop = 0xFC
    };

    Type type;
    uint8_t channel;      // 0-15
    uint8_t data1;        // Note number or CC number
    uint8_t data2;        // Velocity or CC value
    int64_t timestamp;    // Sample-accurate timestamp
    std::vector<uint8_t> sysex;  // For SysEx messages

    // Factory methods
    static MIDIMessage noteOn(uint8_t channel, uint8_t note, uint8_t velocity, int64_t time = 0);
    static MIDIMessage noteOff(uint8_t channel, uint8_t note, uint8_t velocity = 0, int64_t time = 0);
    static MIDIMessage cc(uint8_t channel, uint8_t controller, uint8_t value, int64_t time = 0);
    static MIDIMessage pitchBend(uint8_t channel, int16_t value, int64_t time = 0);

    // Parsing
    static MIDIMessage fromBytes(const uint8_t* data, size_t length, int64_t time = 0);
    std::vector<uint8_t> toBytes() const;
};

} // namespace penta::midi
```

**MIDIBackend.h:**
```cpp
namespace penta::midi {

struct MIDIPortInfo {
    std::string id;
    std::string name;
    bool isInput;
    bool isVirtual;
};

using MIDICallback = std::function<void(const MIDIMessage& message)>;

class MIDIBackend {
public:
    virtual ~MIDIBackend() = default;

    // Port enumeration
    virtual std::vector<MIDIPortInfo> getInputPorts() = 0;
    virtual std::vector<MIDIPortInfo> getOutputPorts() = 0;

    // Port management
    virtual bool openInputPort(const std::string& portId, MIDICallback callback) = 0;
    virtual bool openOutputPort(const std::string& portId) = 0;
    virtual void closeInputPort(const std::string& portId) = 0;
    virtual void closeOutputPort(const std::string& portId) = 0;

    // Virtual ports
    virtual bool createVirtualInputPort(const std::string& name, MIDICallback callback) = 0;
    virtual bool createVirtualOutputPort(const std::string& name) = 0;

    // Send
    virtual bool sendMessage(const std::string& portId, const MIDIMessage& message) = 0;

    // Factory
    static std::unique_ptr<MIDIBackend> create();
};

} // namespace penta::midi
```

**Acceptance Criteria:**
- [ ] MIDIMessage correctly parses/generates all message types
- [ ] Timestamps are sample-accurate
- [ ] Unit tests for message serialization

---

### 1.2.2 Implement Platform-Specific MIDI Backends

**macOS - CoreMIDI:**
```
penta-core/src/midi/backends/CoreMIDIBackend.h
penta-core/src/midi/backends/CoreMIDIBackend.cpp
```

**Windows - Windows MIDI API:**
```
penta-core/src/midi/backends/WindowsMIDIBackend.h
penta-core/src/midi/backends/WindowsMIDIBackend.cpp
```

**Linux - ALSA MIDI:**
```
penta-core/src/midi/backends/ALSAMIDIBackend.h
penta-core/src/midi/backends/ALSAMIDIBackend.cpp
```

**Acceptance Criteria:**
- [ ] All ports enumerate correctly
- [ ] Messages receive with < 1ms latency
- [ ] Virtual ports work for inter-app MIDI
- [ ] Hot-plug detection for USB MIDI devices

---

### 1.2.3 Implement MIDI Clock Sync

**Files:**
```
penta-core/include/penta/midi/MIDIClock.h
penta-core/src/midi/MIDIClock.cpp
```

```cpp
class MIDIClock {
public:
    enum class Mode { Internal, External, Auto };

    void setMode(Mode mode);
    void setTempo(double bpm);  // For internal mode

    // Called from audio thread
    void processBlock(int numSamples, int sampleRate);

    // Get current position
    double getCurrentBeat() const;
    double getCurrentTempo() const;
    bool isPlaying() const;

    // Generate MIDI clock messages (24 PPQ)
    std::vector<MIDIMessage> getClockMessages(int64_t startSample, int64_t endSample);

    // Receive external clock
    void receiveMIDIMessage(const MIDIMessage& message);

private:
    std::atomic<Mode> mode_{Mode::Internal};
    std::atomic<double> tempo_{120.0};
    std::atomic<double> currentBeat_{0.0};
    std::atomic<bool> playing_{false};

    // External clock tracking
    double lastClockTime_ = 0;
    double externalTempo_ = 120.0;
};
```

**Acceptance Criteria:**
- [ ] Internal clock jitter < 0.1ms
- [ ] External clock sync locks within 1 second
- [ ] Tempo detection accurate to 0.1 BPM
- [ ] Handles tempo changes smoothly

---

### 1.2.4 Implement MIDI Learn

**Files:**
```
penta-core/include/penta/midi/MIDILearn.h
penta-core/src/midi/MIDILearn.cpp
```

```cpp
class MIDILearn {
public:
    struct Mapping {
        uint8_t channel;
        uint8_t controller;  // CC number or note number
        enum class Type { CC, Note, PitchBend } type;
        std::string parameterId;
        float minValue = 0.0f;
        float maxValue = 1.0f;
    };

    // Learning mode
    void startLearning(const std::string& parameterId);
    void stopLearning();
    bool isLearning() const;

    // Process incoming MIDI (captures during learn mode)
    void processMIDI(const MIDIMessage& message);

    // Mapping management
    void addMapping(const Mapping& mapping);
    void removeMapping(const std::string& parameterId);
    std::vector<Mapping> getMappings() const;

    // Get parameter value from MIDI
    std::optional<float> getParameterValue(const MIDIMessage& message) const;

    // Serialization
    void saveToJSON(const std::string& path) const;
    void loadFromJSON(const std::string& path);
};
```

**Acceptance Criteria:**
- [ ] Learns CC, notes, and pitch bend
- [ ] Mappings persist across sessions
- [ ] Multiple parameters can map to same CC (with different ranges)
- [ ] Thread-safe for use from MIDI callback

---

### 1.2.5 Implement MPE Support

**Files:**
```
penta-core/include/penta/midi/MPEZone.h
penta-core/src/midi/MPEZone.cpp
```

```cpp
class MPEZone {
public:
    struct Note {
        uint8_t channel;     // Member channel (2-16 or 1-15)
        uint8_t note;
        uint8_t velocity;
        float pressure;      // Channel pressure (0-1)
        float slide;         // CC74 (0-1)
        float pitchBend;     // Pitch bend (-1 to +1)
        bool active;
    };

    enum class Type { Lower, Upper };

    MPEZone(Type type, int numMemberChannels = 15);

    // Process MIDI and update note states
    void processMIDI(const MIDIMessage& message);

    // Get active notes with per-note expression
    std::vector<Note> getActiveNotes() const;

    // Zone configuration
    void setMasterChannel(uint8_t channel);  // 1 for lower, 16 for upper
    void setPitchBendRange(int semitones);   // Per-note bend range

private:
    Type type_;
    uint8_t masterChannel_;
    int numMemberChannels_;
    int pitchBendRange_ = 48;  // Semitones
    std::array<Note, 16> notes_;  // One per channel
};
```

**Acceptance Criteria:**
- [ ] Correctly tracks per-note expression
- [ ] Supports both lower and upper zones
- [ ] Handles zone configuration messages (RPN)
- [ ] Unit tests with Roli Seaboard message sequences

---

### 1.2.6 Implement MIDI 2.0 Support

**Files:**
```
penta-core/include/penta/midi/MIDI2.h
penta-core/src/midi/MIDI2.cpp
```

**Note:** MIDI 2.0 uses Universal MIDI Packets (UMP) with 32-bit resolution

```cpp
namespace penta::midi2 {

struct UniversalMIDIPacket {
    uint32_t words[4];  // Up to 128 bits

    enum class MessageType : uint8_t {
        Utility = 0x0,
        System = 0x1,
        MIDI1ChannelVoice = 0x2,
        Data64 = 0x3,
        MIDI2ChannelVoice = 0x4,
        Data128 = 0x5
    };

    MessageType getType() const;
    uint8_t getGroup() const;

    // MIDI 2.0 high-resolution values
    uint32_t getVelocity32() const;      // 32-bit velocity
    uint32_t getController32() const;     // 32-bit CC value
    int32_t getPitchBend32() const;       // 32-bit pitch bend

    // Convert to/from MIDI 1.0
    static UniversalMIDIPacket fromMIDI1(const MIDIMessage& msg);
    MIDIMessage toMIDI1() const;
};

} // namespace penta::midi2
```

**Acceptance Criteria:**
- [ ] Parses/generates UMP messages
- [ ] Bidirectional conversion with MIDI 1.0
- [ ] Preserves high-resolution data when possible
- [ ] Unit tests for all message types

---

### 1.2.7 Implement MIDI File I/O

**Files:**
```
penta-core/include/penta/midi/MIDIFile.h
penta-core/src/midi/MIDIFile.cpp
```

```cpp
class MIDIFile {
public:
    struct Track {
        std::string name;
        std::vector<MIDIMessage> events;  // Sorted by timestamp
    };

    // File operations
    bool load(const std::string& path);
    bool save(const std::string& path) const;

    // Track management
    void addTrack(const Track& track);
    Track& getTrack(int index);
    int getTrackCount() const;

    // Timing
    int getTicksPerQuarterNote() const;
    void setTicksPerQuarterNote(int tpqn);

    // Convert between ticks and samples
    int64_t ticksToSamples(int64_t ticks, double tempo, int sampleRate) const;
    int64_t samplesToTicks(int64_t samples, double tempo, int sampleRate) const;

    // Get all events merged and sorted
    std::vector<MIDIMessage> getMergedEvents() const;

private:
    int format_ = 1;  // SMF format (0, 1, or 2)
    int ticksPerQuarterNote_ = 480;
    std::vector<Track> tracks_;
};
```

**Acceptance Criteria:**
- [ ] Reads SMF format 0, 1, and 2
- [ ] Preserves timing accuracy (no drift)
- [ ] Handles running status correctly
- [ ] Unit tests with various MIDI files

---

## 1.3 Transport System

### 1.3.1 Create Transport Controller

**Files:**
```
penta-core/include/penta/transport/Transport.h
penta-core/src/transport/Transport.cpp
```

```cpp
namespace penta::transport {

class Transport {
public:
    enum class State { Stopped, Playing, Recording, Paused };

    // Basic controls
    void play();
    void pause();
    void stop();
    void record();

    // Position
    void setPositionSamples(int64_t samples);
    void setPositionBeats(double beats);
    void setPositionSeconds(double seconds);
    int64_t getPositionSamples() const;
    double getPositionBeats() const;
    double getPositionSeconds() const;

    // Tempo and time signature
    void setTempo(double bpm);
    void setTimeSignature(int numerator, int denominator);
    double getTempo() const;
    std::pair<int, int> getTimeSignature() const;

    // Looping
    void setLoopEnabled(bool enabled);
    void setLoopRange(int64_t startSample, int64_t endSample);
    bool isLooping() const;

    // Called from audio thread
    void processBlock(int numSamples) noexcept;

    // State
    State getState() const;

    // Callbacks
    using StateCallback = std::function<void(State)>;
    void setStateCallback(StateCallback callback);

private:
    std::atomic<State> state_{State::Stopped};
    std::atomic<int64_t> positionSamples_{0};
    std::atomic<double> tempo_{120.0};
    // ... tempo automation, time sig changes, etc.
};

} // namespace penta::transport
```

**Acceptance Criteria:**
- [ ] State transitions are atomic and glitch-free
- [ ] Loop points sample-accurate (no gaps/overlaps)
- [ ] Tempo changes apply correctly mid-playback
- [ ] Unit tests for all state transitions

---

### 1.3.2 Implement Timeline with Tempo Map

**Files:**
```
penta-core/include/penta/transport/TempoMap.h
penta-core/src/transport/TempoMap.cpp
```

```cpp
class TempoMap {
public:
    struct TempoEvent {
        int64_t positionSamples;
        double bpm;
        int timeSignatureNum = 4;
        int timeSignatureDenom = 4;
    };

    // Add/remove tempo changes
    void addTempoChange(int64_t positionSamples, double bpm);
    void addTimeSignatureChange(int64_t positionSamples, int num, int denom);
    void removeTempoChange(int64_t positionSamples);

    // Conversion utilities
    double samplesToBeats(int64_t samples, int sampleRate) const;
    int64_t beatsToSamples(double beats, int sampleRate) const;
    double samplesToSeconds(int64_t samples, int sampleRate) const;
    int64_t secondsToSamples(double seconds, int sampleRate) const;

    // Get tempo at position
    double getTempoAtSample(int64_t sample) const;
    std::pair<int, int> getTimeSignatureAtSample(int64_t sample) const;

    // Get bar/beat position
    struct BarBeatPosition {
        int bar;
        int beat;
        double tick;  // Fractional beat
    };
    BarBeatPosition getBarBeatPosition(int64_t samples, int sampleRate) const;

private:
    std::vector<TempoEvent> events_;  // Sorted by position
};
```

**Acceptance Criteria:**
- [ ] Accurate conversion at any tempo
- [ ] Handles tempo ramps (future: linear interpolation)
- [ ] Time signature affects bar counting
- [ ] Unit tests with complex tempo maps

---

### 1.3.3 Implement Metronome

**Files:**
```
penta-core/include/penta/transport/Metronome.h
penta-core/src/transport/Metronome.cpp
```

```cpp
class Metronome {
public:
    struct Config {
        bool enabled = false;
        float volume = 0.8f;
        int countInBars = 1;
        bool accentDownbeat = true;
        std::string downbeatSample;  // Path to audio file
        std::string beatSample;
    };

    void setConfig(const Config& config);

    // Load custom sounds
    void loadSounds(const std::string& downbeatPath, const std::string& beatPath);
    void useBuiltInSounds();  // Generate sine click

    // Called from audio thread - generates click into buffer
    void processBlock(float* buffer, int numFrames,
                      int64_t startSample, const TempoMap& tempoMap,
                      int sampleRate) noexcept;

    // Count-in
    void startCountIn();
    bool isCountingIn() const;
    int getCountInBeatsRemaining() const;

private:
    Config config_;
    std::vector<float> downbeatSample_;
    std::vector<float> beatSample_;
    int samplePlayhead_ = 0;
};
```

**Acceptance Criteria:**
- [ ] Click precisely on beat (within 1 sample)
- [ ] Supports custom sounds (WAV files)
- [ ] Count-in works before recording
- [ ] Volume adjustable without clicking

---

### 1.3.4 Implement Marker System

**Files:**
```
penta-core/include/penta/transport/MarkerManager.h
penta-core/src/transport/MarkerManager.cpp
```

```cpp
class MarkerManager {
public:
    struct Marker {
        std::string id;
        std::string name;
        int64_t positionSamples;
        std::string color;  // Hex color
        enum class Type { Generic, LoopStart, LoopEnd, PunchIn, PunchOut } type;
    };

    // CRUD operations
    std::string addMarker(const Marker& marker);  // Returns ID
    void updateMarker(const std::string& id, const Marker& marker);
    void removeMarker(const std::string& id);

    // Query
    std::vector<Marker> getAllMarkers() const;
    std::optional<Marker> getMarkerById(const std::string& id) const;
    std::optional<Marker> getMarkerAtPosition(int64_t samples, int64_t tolerance = 0) const;
    std::optional<Marker> getNextMarker(int64_t currentPosition) const;
    std::optional<Marker> getPreviousMarker(int64_t currentPosition) const;

    // Navigation
    int64_t jumpToMarker(const std::string& id) const;
    int64_t jumpToNextMarker(int64_t currentPosition) const;
    int64_t jumpToPreviousMarker(int64_t currentPosition) const;

    // Serialization
    void saveToJSON(const std::string& path) const;
    void loadFromJSON(const std::string& path);
};
```

**Acceptance Criteria:**
- [ ] Markers persist in project
- [ ] Navigation functions work correctly
- [ ] Markers can be renamed/colored
- [ ] JSON serialization works

---

### 1.3.5 Implement Undo/Redo System

**Files:**
```
penta-core/include/penta/core/UndoManager.h
penta-core/src/core/UndoManager.cpp
```

```cpp
class UndoManager {
public:
    class Command {
    public:
        virtual ~Command() = default;
        virtual void execute() = 0;
        virtual void undo() = 0;
        virtual std::string getDescription() const = 0;
    };

    // Execute and record command
    void executeCommand(std::unique_ptr<Command> command);

    // Undo/redo
    bool canUndo() const;
    bool canRedo() const;
    void undo();
    void redo();

    // History
    std::vector<std::string> getUndoHistory() const;
    std::vector<std::string> getRedoHistory() const;

    // Transaction grouping
    void beginTransaction(const std::string& name);
    void endTransaction();
    void cancelTransaction();

    // Limits
    void setMaxHistorySize(int size);
    void clearHistory();

private:
    std::vector<std::unique_ptr<Command>> undoStack_;
    std::vector<std::unique_ptr<Command>> redoStack_;
    std::vector<std::unique_ptr<Command>> currentTransaction_;
    int maxHistorySize_ = 100;
};
```

**Acceptance Criteria:**
- [ ] All edit operations are undoable
- [ ] Transactions group multiple operations
- [ ] History limit prevents memory bloat
- [ ] Thread-safe for UI access

---

## 1.4 Mixer Engine

### 1.4.1 Create Channel Strip

**Files:**
```
penta-core/include/penta/mixer/ChannelStrip.h
penta-core/src/mixer/ChannelStrip.cpp
```

```cpp
class ChannelStrip {
public:
    struct Config {
        std::string name;
        int inputChannels = 2;
        int outputChannels = 2;
        enum class Type { Audio, Aux, Bus, Master } type = Type::Audio;
    };

    ChannelStrip(const Config& config);

    // Gain staging
    void setInputGain(float dB);
    void setFader(float dB);         // -inf to +12dB
    void setPan(float pan);          // -1 (L) to +1 (R)

    // Solo/mute
    void setSolo(bool solo);
    void setMute(bool mute);
    void setSoloSafe(bool safe);     // Immune to solo

    // Insert slots (pre-fader)
    void insertPlugin(int slot, std::shared_ptr<AudioProcessor> plugin);
    void removePlugin(int slot);
    void setInsertBypass(int slot, bool bypass);

    // Sends (post-fader by default)
    struct Send {
        std::string destBusId;
        float gain = 0.0f;  // dB
        bool preFader = false;
    };
    void addSend(const Send& send);
    void setSendGain(int index, float dB);
    void setSendPreFader(int index, bool pre);

    // Metering
    float getPeakLevel(int channel) const;  // dB
    float getRMSLevel(int channel) const;   // dB
    void resetPeakHold();

    // Processing (called from audio thread)
    void processBlock(const float* const* inputs, float* const* outputs,
                      int numFrames) noexcept;

private:
    Config config_;
    std::atomic<float> inputGain_{1.0f};
    std::atomic<float> fader_{1.0f};
    std::atomic<float> pan_{0.0f};
    std::atomic<bool> solo_{false};
    std::atomic<bool> mute_{false};
    std::vector<std::shared_ptr<AudioProcessor>> inserts_;
    std::vector<Send> sends_;

    // Metering
    std::array<std::atomic<float>, 2> peakLevels_;
    std::array<std::atomic<float>, 2> rmsLevels_;
};
```

**Acceptance Criteria:**
- [ ] Correct gain staging (input -> inserts -> fader -> pan -> output)
- [ ] Solo/mute work correctly with solo-safe
- [ ] Metering accurate and thread-safe
- [ ] Unit tests for signal flow

---

### 1.4.2 Implement Pan Laws

**Files:**
```
penta-core/include/penta/mixer/PanLaw.h
penta-core/src/mixer/PanLaw.cpp
```

```cpp
namespace penta::mixer {

enum class PanLaw {
    Linear,           // L/R sum to 1.0
    EqualPower,       // Constant power (-3dB center)
    Minus3dB,         // -3dB at center
    Minus4_5dB,       // -4.5dB at center
    Minus6dB          // -6dB at center
};

struct PanCoefficients {
    float left;
    float right;
};

PanCoefficients calculatePan(float pan, PanLaw law);

// Stereo balance (different from pan)
PanCoefficients calculateBalance(float balance);

} // namespace penta::mixer
```

**Pan law formulas:**
- Linear: `L = (1-pan)/2, R = (1+pan)/2`
- Equal power: `L = cos(pan*pi/4), R = sin(pan*pi/4)`
- -3dB: `L = sqrt((1-pan)/2), R = sqrt((1+pan)/2)`
- -4.5dB: `L = pow((1-pan)/2, 0.75), R = pow((1+pan)/2, 0.75)`
- -6dB: `L = (1-pan)/2, R = (1+pan)/2` (same as linear)

**Acceptance Criteria:**
- [ ] All pan laws compute correct coefficients
- [ ] Unit tests verify sum/power at center
- [ ] Balance differs from pan (only attenuates)

---

### 1.4.3 Implement Mixer Graph

**Files:**
```
penta-core/include/penta/mixer/Mixer.h
penta-core/src/mixer/Mixer.cpp
```

```cpp
class Mixer {
public:
    // Channel management
    std::string addChannel(const ChannelStrip::Config& config);
    void removeChannel(const std::string& id);
    ChannelStrip* getChannel(const std::string& id);

    // Routing
    void setChannelOutput(const std::string& channelId, const std::string& busId);
    void createBus(const std::string& name);
    void createAux(const std::string& name);

    // Master
    ChannelStrip* getMaster();

    // VCA groups
    void createVCAGroup(const std::string& name);
    void addChannelToVCA(const std::string& channelId, const std::string& vcaId);
    void setVCAFader(const std::string& vcaId, float dB);

    // Solo management
    void clearAllSolos();
    bool isAnySoloed() const;

    // Processing
    void processBlock(int numFrames) noexcept;

    // Get all channels for UI
    std::vector<std::string> getChannelIds() const;

private:
    std::unordered_map<std::string, std::unique_ptr<ChannelStrip>> channels_;
    std::unique_ptr<ChannelStrip> master_;
    std::vector<std::string> processingOrder_;  // Topologically sorted

    void rebuildProcessingOrder();
};
```

**Acceptance Criteria:**
- [ ] Channels route correctly to buses/master
- [ ] VCA affects linked channel faders
- [ ] Processing order respects dependencies
- [ ] No feedback possible in routing

---

### 1.4.4 Implement Automation System

**Files:**
```
penta-core/include/penta/automation/AutomationLane.h
penta-core/include/penta/automation/AutomationManager.h
penta-core/src/automation/AutomationLane.cpp
penta-core/src/automation/AutomationManager.cpp
```

```cpp
class AutomationLane {
public:
    struct Point {
        int64_t timeSamples;
        float value;        // 0-1 normalized
        enum class Curve { Linear, Smooth, Step } curve = Curve::Linear;
    };

    AutomationLane(const std::string& parameterId);

    // Point manipulation
    void addPoint(const Point& point);
    void removePoint(int64_t timeSamples);
    void movePoint(int64_t fromTime, int64_t toTime, float value);

    // Read value at time (with interpolation)
    float getValueAtTime(int64_t timeSamples) const;

    // Read/write modes
    enum class Mode { Off, Read, Write, Touch, Latch };
    void setMode(Mode mode);
    Mode getMode() const;

    // Recording automation
    void beginRecording(int64_t startTime);
    void recordValue(int64_t time, float value);
    void endRecording();

    // Get all points for display
    std::vector<Point> getPoints() const;

private:
    std::string parameterId_;
    std::vector<Point> points_;  // Sorted by time
    std::atomic<Mode> mode_{Mode::Read};
};

class AutomationManager {
public:
    // Create lane for parameter
    AutomationLane* getOrCreateLane(const std::string& parameterId);

    // Process automation (called from audio thread)
    void processBlock(int64_t startSample, int numSamples);

    // Arm parameter for recording
    void armParameter(const std::string& parameterId);
    void disarmParameter(const std::string& parameterId);

private:
    std::unordered_map<std::string, std::unique_ptr<AutomationLane>> lanes_;
};
```

**Acceptance Criteria:**
- [ ] All modes work correctly (Read, Write, Touch, Latch)
- [ ] Touch mode: only writes while actively moving
- [ ] Latch mode: continues writing after release
- [ ] Smooth interpolation between points
- [ ] Sample-accurate automation

---

## 1.5 Audio Processing Graph

### 1.5.1 Create Processing Node Abstraction

**Files:**
```
penta-core/include/penta/graph/AudioProcessor.h
penta-core/include/penta/graph/ProcessorNode.h
penta-core/src/graph/AudioProcessor.cpp
penta-core/src/graph/ProcessorNode.cpp
```

```cpp
class AudioProcessor {
public:
    virtual ~AudioProcessor() = default;

    // Configuration
    virtual void prepareToPlay(int sampleRate, int maxBlockSize) = 0;
    virtual void releaseResources() = 0;

    // Processing
    virtual void processBlock(const float* const* inputs, float* const* outputs,
                              int numInputChannels, int numOutputChannels,
                              int numFrames) noexcept = 0;

    // Latency
    virtual int getLatencySamples() const { return 0; }

    // Parameters
    virtual int getNumParameters() const { return 0; }
    virtual float getParameter(int index) const { return 0; }
    virtual void setParameter(int index, float value) {}
    virtual std::string getParameterName(int index) const { return ""; }

    // Bypass
    void setBypass(bool bypass) { bypassed_ = bypass; }
    bool isBypassed() const { return bypassed_; }

    // Tail (reverb, delay tails)
    virtual int getTailLengthSamples() const { return 0; }

protected:
    bool bypassed_ = false;
    int sampleRate_ = 44100;
    int maxBlockSize_ = 512;
};

class ProcessorNode {
public:
    ProcessorNode(std::unique_ptr<AudioProcessor> processor);

    // Connections
    void connectInput(int inputChannel, ProcessorNode* source, int sourceChannel);
    void disconnectInput(int inputChannel);

    // Get processor
    AudioProcessor* getProcessor() { return processor_.get(); }

    // For graph sorting
    std::vector<ProcessorNode*> getInputNodes() const;
    int getLatency() const;

private:
    std::unique_ptr<AudioProcessor> processor_;
    struct Connection {
        ProcessorNode* source;
        int sourceChannel;
    };
    std::vector<Connection> inputs_;
};
```

**Acceptance Criteria:**
- [ ] Clean interface for all processor types
- [ ] Bypass works without glitches
- [ ] Latency correctly reported
- [ ] Connections form valid graph

---

### 1.5.2 Implement Audio Graph with DAG

**Files:**
```
penta-core/include/penta/graph/AudioGraph.h
penta-core/src/graph/AudioGraph.cpp
```

```cpp
class AudioGraph {
public:
    // Node management
    std::string addNode(std::unique_ptr<AudioProcessor> processor);
    void removeNode(const std::string& nodeId);
    ProcessorNode* getNode(const std::string& nodeId);

    // Connections
    bool connect(const std::string& sourceId, int sourceChannel,
                 const std::string& destId, int destChannel);
    void disconnect(const std::string& sourceId, int sourceChannel,
                    const std::string& destId, int destChannel);

    // Input/output nodes
    void setInputNode(const std::string& nodeId);
    void setOutputNode(const std::string& nodeId);

    // Compilation
    bool compile();  // Topological sort, latency calculation
    bool isValid() const;  // No cycles
    std::string getLastError() const;

    // Processing
    void processBlock(const float* const* inputs, float* const* outputs,
                      int numInputChannels, int numOutputChannels,
                      int numFrames) noexcept;

    // Latency
    int getTotalLatency() const;

    // Get processing order for debugging
    std::vector<std::string> getProcessingOrder() const;

private:
    std::unordered_map<std::string, std::unique_ptr<ProcessorNode>> nodes_;
    std::vector<ProcessorNode*> processingOrder_;
    std::string inputNodeId_;
    std::string outputNodeId_;
    int totalLatency_ = 0;

    bool detectCycle() const;
    void calculateLatencies();
    void topologicalSort();
};
```

**Acceptance Criteria:**
- [ ] Topological sort produces correct order
- [ ] Cycle detection prevents invalid graphs
- [ ] Latency compensation automatic
- [ ] Graph recompiles without audio glitch

---

### 1.5.3 Implement Parallel Processing

**Files:**
```
penta-core/include/penta/graph/ParallelProcessor.h
penta-core/src/graph/ParallelProcessor.cpp
```

```cpp
class ParallelProcessor {
public:
    ParallelProcessor(int numThreads = 0);  // 0 = auto-detect

    // Process graph with parallelism
    void processGraph(AudioGraph& graph,
                      const float* const* inputs, float* const* outputs,
                      int numInputChannels, int numOutputChannels,
                      int numFrames);

    // Statistics
    double getCPUUsage() const;
    int getActiveThreads() const;

private:
    std::vector<std::thread> workers_;
    std::atomic<bool> running_{true};

    // Lock-free work queue
    struct WorkItem {
        ProcessorNode* node;
        std::atomic<int> dependenciesRemaining;
    };
    std::vector<WorkItem> workQueue_;
};
```

**Implementation notes:**
- Use thread pool with lock-free work stealing
- Dependencies tracked with atomic counters
- SIMD-aligned buffers for each worker
- CPU affinity for consistent performance

**Acceptance Criteria:**
- [ ] Correctly parallelizes independent branches
- [ ] No race conditions or deadlocks
- [ ] Scales with CPU cores
- [ ] Maintains deterministic output

---

### 1.5.4 Implement SIMD DSP Utilities

**Files:**
```
penta-core/include/penta/dsp/SIMD.h
penta-core/src/dsp/SIMD.cpp
```

```cpp
namespace penta::dsp {

// Detect available SIMD
enum class SIMDLevel { None, SSE2, AVX, AVX2, AVX512, NEON };
SIMDLevel detectSIMD();

// Optimized operations
void add(float* dest, const float* src, int count);
void multiply(float* dest, const float* src, int count);
void multiplyAdd(float* dest, const float* src1, const float* src2, int count);
void scale(float* dest, float scalar, int count);
void copy(float* dest, const float* src, int count);
void clear(float* dest, int count);

// Find peak
float findPeak(const float* src, int count);
float findRMS(const float* src, int count);

// Interleave/deinterleave
void interleave(float* dest, const float* const* src, int numChannels, int numFrames);
void deinterleave(float* const* dest, const float* src, int numChannels, int numFrames);

// Apply gain with smoothing
void applyGain(float* dest, const float* src, float startGain, float endGain, int count);

} // namespace penta::dsp
```

**Acceptance Criteria:**
- [ ] Auto-detects best SIMD level
- [ ] Fallback to scalar for unsupported
- [ ] 4x+ speedup over naive loops
- [ ] Unit tests verify correctness

---

## 1.6 Built-in DSP Effects

### 1.6.1 Implement EQ

**Files:**
```
penta-core/include/penta/effects/EQ.h
penta-core/src/effects/EQ.cpp
```

**Band types:**
- Low shelf, high shelf
- Low pass, high pass
- Peak/parametric
- Notch
- Band pass

```cpp
class ParametricEQ : public AudioProcessor {
public:
    static constexpr int MaxBands = 8;

    struct Band {
        enum class Type { LowShelf, HighShelf, Peak, LowPass, HighPass, Notch, BandPass };
        Type type = Type::Peak;
        float frequency = 1000.0f;  // Hz
        float gain = 0.0f;          // dB
        float q = 0.707f;           // Q factor
        bool enabled = true;
    };

    void setBand(int index, const Band& band);
    Band getBand(int index) const;

    // From AudioProcessor
    void prepareToPlay(int sampleRate, int maxBlockSize) override;
    void processBlock(...) noexcept override;

private:
    std::array<Band, MaxBands> bands_;
    // Biquad coefficients for each band
    struct BiquadCoeffs { float b0, b1, b2, a1, a2; };
    std::array<BiquadCoeffs, MaxBands> coeffs_;
    // State for each band/channel
    std::array<std::array<float, 4>, MaxBands * 2> state_;

    void calculateCoefficients(int bandIndex);
};
```

**Acceptance Criteria:**
- [ ] All filter types implemented
- [ ] Smooth parameter changes (no zippering)
- [ ] CPU efficient (< 1% per band)
- [ ] Unit tests verify frequency response

---

### 1.6.2 Implement Compressor

**Files:**
```
penta-core/include/penta/effects/Compressor.h
penta-core/src/effects/Compressor.cpp
```

```cpp
class Compressor : public AudioProcessor {
public:
    // Parameters
    void setThreshold(float dB);      // -60 to 0 dB
    void setRatio(float ratio);       // 1:1 to inf:1
    void setAttack(float ms);         // 0.1 to 100 ms
    void setRelease(float ms);        // 10 to 1000 ms
    void setKnee(float dB);           // 0 to 12 dB (soft knee width)
    void setMakeupGain(float dB);     // 0 to 24 dB

    // Sidechain
    void setSidechainEnabled(bool enabled);
    void setSidechainHighPass(float freq);

    // Metering
    float getGainReduction() const;   // Current GR in dB

    void processBlock(...) noexcept override;

private:
    std::atomic<float> threshold_{-20.0f};
    std::atomic<float> ratio_{4.0f};
    std::atomic<float> attackMs_{10.0f};
    std::atomic<float> releaseMs_{100.0f};
    std::atomic<float> kneeDb_{6.0f};
    std::atomic<float> makeupGain_{0.0f};

    float envelope_ = 0.0f;
    float attackCoeff_ = 0.0f;
    float releaseCoeff_ = 0.0f;
};
```

**Acceptance Criteria:**
- [ ] Smooth gain reduction (no pumping artifacts)
- [ ] Soft knee works correctly
- [ ] Sidechain HPF filters kick
- [ ] Accurate GR metering

---

### 1.6.3 Implement Delay

**Files:**
```
penta-core/include/penta/effects/Delay.h
penta-core/src/effects/Delay.cpp
```

```cpp
class Delay : public AudioProcessor {
public:
    void setDelayTime(float ms);         // 0 to 2000 ms
    void setDelayTimeSync(float beats);  // For tempo sync
    void setFeedback(float amount);      // 0 to 1 (< 1 for stability)
    void setMix(float wet);              // 0 to 1
    void setPingPong(bool enabled);
    void setHighCut(float freq);         // Feedback filter
    void setLowCut(float freq);

    void setTempoSync(bool enabled, double bpm);

    int getLatencySamples() const override;
    int getTailLengthSamples() const override;

    void processBlock(...) noexcept override;

private:
    std::vector<float> delayBuffer_;
    int writePos_ = 0;
    float delayTimeSamples_ = 0;
    // Filters for feedback path
    float highCutState_ = 0;
    float lowCutState_ = 0;
};
```

**Acceptance Criteria:**
- [ ] Smooth delay time changes (interpolation)
- [ ] Ping-pong creates stereo effect
- [ ] Feedback filters darken repeats
- [ ] Tempo sync accurate to grid

---

### 1.6.4 Implement Reverb

**Files:**
```
penta-core/include/penta/effects/Reverb.h
penta-core/src/effects/Reverb.cpp
```

**Algorithm:** Freeverb (Schroeder-Moorer) or FDN (Feedback Delay Network)

```cpp
class Reverb : public AudioProcessor {
public:
    void setRoomSize(float size);      // 0 to 1
    void setDamping(float damp);       // 0 to 1
    void setPreDelay(float ms);        // 0 to 100 ms
    void setDecay(float seconds);      // 0.1 to 10 s
    void setMix(float wet);            // 0 to 1
    void setWidth(float width);        // 0 to 1
    void setHighCut(float freq);
    void setLowCut(float freq);

    // Convolution mode (for IR loading)
    void loadImpulseResponse(const std::string& path);
    void setConvolutionEnabled(bool enabled);

    int getTailLengthSamples() const override;

    void processBlock(...) noexcept override;

private:
    // Freeverb components
    std::array<float, 8> combDelays_;
    std::array<float, 4> allpassDelays_;
    // or FDN matrix
    // or convolution FFT buffers
};
```

**Acceptance Criteria:**
- [ ] Natural decay without metallic ringing
- [ ] Pre-delay works correctly
- [ ] Convolution mode with IR files
- [ ] Tail continues after input stops

---

### 1.6.5 Implement Additional Effects

Create similar implementations for:

**Modulation:**
```
penta-core/include/penta/effects/Chorus.h
penta-core/include/penta/effects/Flanger.h
penta-core/include/penta/effects/Phaser.h
```

**Distortion:**
```
penta-core/include/penta/effects/Saturator.h
penta-core/include/penta/effects/Bitcrusher.h
penta-core/include/penta/effects/Waveshaper.h
```

**Utility:**
```
penta-core/include/penta/effects/Gain.h
penta-core/include/penta/effects/StereoWidener.h
penta-core/include/penta/effects/Limiter.h
```

**Analysis:**
```
penta-core/include/penta/effects/SpectrumAnalyzer.h
penta-core/include/penta/effects/LoudnessMeter.h
```

**Acceptance Criteria for all:**
- [ ] Each effect has unit tests
- [ ] Parameters smoothed (no zipper noise)
- [ ] CPU usage reasonable (< 5% each)
- [ ] Bypass works without glitches

---

## 1.7 Audio Recording

### 1.7.1 Implement Recording Engine

**Files:**
```
penta-core/include/penta/recording/RecordingEngine.h
penta-core/src/recording/RecordingEngine.cpp
```

```cpp
class RecordingEngine {
public:
    struct RecordingConfig {
        std::string outputPath;
        int sampleRate;
        int bitDepth;           // 16, 24, 32
        int numChannels;
        bool createBackup;      // Safety track
        std::string format;     // "wav", "aiff", "flac"
    };

    // Recording lifecycle
    bool prepareRecording(const RecordingConfig& config);
    void startRecording(int64_t startSample);
    void stopRecording();
    bool isRecording() const;

    // Called from audio thread
    void writeBlock(const float* const* data, int numChannels, int numFrames) noexcept;

    // Punch recording
    void setPunchIn(int64_t sample);
    void setPunchOut(int64_t sample);
    void clearPunch();

    // Monitoring
    float getRecordingLevel(int channel) const;
    bool isClipping(int channel) const;
    int64_t getRecordedSamples() const;

    // File management
    std::string getRecordedFilePath() const;

private:
    RecordingConfig config_;
    std::unique_ptr<AudioFileWriter> writer_;
    std::unique_ptr<AudioFileWriter> backupWriter_;

    // Lock-free buffer for audio thread -> disk thread
    std::unique_ptr<RTMessageQueue> recordBuffer_;
    std::thread diskThread_;
    std::atomic<bool> recording_{false};
};
```

**Acceptance Criteria:**
- [ ] No dropouts during recording
- [ ] Punch in/out sample-accurate
- [ ] Backup track writes simultaneously
- [ ] Clipping detection accurate

---

### 1.7.2 Implement Take Lanes

**Files:**
```
penta-core/include/penta/recording/TakeLane.h
penta-core/src/recording/TakeLane.cpp
```

```cpp
class TakeLane {
public:
    struct Take {
        std::string id;
        std::string audioFilePath;
        int64_t startSample;
        int64_t lengthSamples;
        bool muted = false;
        float gain = 1.0f;
    };

    // Take management
    std::string addTake(const Take& take);
    void removeTake(const std::string& id);
    void muteTake(const std::string& id, bool muted);

    // Comping (selecting best parts)
    struct CompRegion {
        std::string takeId;
        int64_t startSample;
        int64_t endSample;
    };
    void setCompRegion(const CompRegion& region);
    void clearCompRegions();
    std::vector<CompRegion> getCompRegions() const;

    // Render comp to single audio region
    void flattenComp(const std::string& outputPath);

    // Playback
    void readBlock(float* output, int64_t startSample, int numFrames) const;

private:
    std::vector<Take> takes_;
    std::vector<CompRegion> compRegions_;
};
```

**Acceptance Criteria:**
- [ ] Multiple takes stack correctly
- [ ] Comping allows region selection
- [ ] Flatten produces gapless audio
- [ ] Crossfades at comp boundaries

---

### 1.7.3 Implement Loop Recording

**Files:**
```
penta-core/include/penta/recording/LoopRecorder.h
penta-core/src/recording/LoopRecorder.cpp
```

```cpp
class LoopRecorder {
public:
    enum class Mode {
        Replace,        // Each pass replaces previous
        Overdub,        // Each pass adds layer
        CreateTakes     // Each pass creates new take
    };

    void setMode(Mode mode);
    void setLoopRange(int64_t startSample, int64_t endSample);

    // Recording
    void startLoopRecording();
    void stopLoopRecording();

    // Called when loop wraps
    void onLoopWrap(int64_t sample);

    // Get recorded layers
    int getLayerCount() const;
    std::vector<std::string> getLayerPaths() const;

private:
    Mode mode_ = Mode::CreateTakes;
    int64_t loopStart_ = 0;
    int64_t loopEnd_ = 0;
    int currentLayer_ = 0;
};
```

**Acceptance Criteria:**
- [ ] Loop boundary seamless
- [ ] Overdub layers blend correctly
- [ ] CreateTakes mode generates take lanes
- [ ] No clicks at loop points

---

## Testing Requirements

### Unit Tests

Create tests in `penta-core/tests/`:

```
tests/audio/AudioBackendTest.cpp
tests/audio/SampleRateConverterTest.cpp
tests/midi/MIDIMessageTest.cpp
tests/midi/MIDIClockTest.cpp
tests/transport/TransportTest.cpp
tests/transport/TempoMapTest.cpp
tests/mixer/ChannelStripTest.cpp
tests/mixer/PanLawTest.cpp
tests/graph/AudioGraphTest.cpp
tests/effects/EQTest.cpp
tests/effects/CompressorTest.cpp
tests/recording/RecordingEngineTest.cpp
```

### Integration Tests

```
tests/integration/AudioPipelineTest.cpp
tests/integration/MIDIToAudioTest.cpp
tests/integration/RecordPlaybackTest.cpp
```

### Performance Tests

```
tests/performance/AudioCallbackBenchmark.cpp
tests/performance/GraphProcessingBenchmark.cpp
tests/performance/SIMDBenchmark.cpp
```

---

## CMake Updates

Add to `penta-core/CMakeLists.txt`:

```cmake
# Audio sources
set(AUDIO_SOURCES
    src/audio/AudioBackend.cpp
    src/audio/AudioDevice.cpp
    src/audio/AudioBuffer.cpp
    src/audio/SampleRateConverter.cpp
    src/audio/AudioRouter.cpp
    src/audio/AudioStreamMonitor.cpp
)

# Platform-specific backends
if(APPLE)
    list(APPEND AUDIO_SOURCES src/audio/backends/CoreAudioBackend.cpp)
    find_library(COREAUDIO_LIBRARY CoreAudio)
    find_library(AUDIOUNIT_LIBRARY AudioUnit)
elseif(WIN32)
    list(APPEND AUDIO_SOURCES src/audio/backends/WASAPIBackend.cpp)
elseif(UNIX)
    list(APPEND AUDIO_SOURCES
        src/audio/backends/ALSABackend.cpp
        src/audio/backends/PipeWireBackend.cpp
    )
    find_package(ALSA REQUIRED)
    find_package(PipeWire)
endif()

# MIDI sources
set(MIDI_SOURCES
    src/midi/MIDIBackend.cpp
    src/midi/MIDIMessage.cpp
    src/midi/MIDIClock.cpp
    src/midi/MIDILearn.cpp
    src/midi/MPEZone.cpp
    src/midi/MIDI2.cpp
    src/midi/MIDIFile.cpp
)

# Transport sources
set(TRANSPORT_SOURCES
    src/transport/Transport.cpp
    src/transport/TempoMap.cpp
    src/transport/Metronome.cpp
    src/transport/MarkerManager.cpp
)

# Mixer sources
set(MIXER_SOURCES
    src/mixer/ChannelStrip.cpp
    src/mixer/PanLaw.cpp
    src/mixer/Mixer.cpp
)

# Graph sources
set(GRAPH_SOURCES
    src/graph/AudioProcessor.cpp
    src/graph/ProcessorNode.cpp
    src/graph/AudioGraph.cpp
    src/graph/ParallelProcessor.cpp
)

# Effects sources
set(EFFECTS_SOURCES
    src/effects/EQ.cpp
    src/effects/Compressor.cpp
    src/effects/Delay.cpp
    src/effects/Reverb.cpp
    src/effects/Chorus.cpp
    src/effects/Limiter.cpp
    # ... etc
)

# Recording sources
set(RECORDING_SOURCES
    src/recording/RecordingEngine.cpp
    src/recording/TakeLane.cpp
    src/recording/LoopRecorder.cpp
)

# DSP utilities
set(DSP_SOURCES
    src/dsp/SIMD.cpp
)
```

---

## Completion Checklist

### 1.1 Audio I/O Foundation
- [ ] AudioBackend abstraction
- [ ] CoreAudio backend (macOS)
- [ ] WASAPI backend (Windows)
- [ ] ALSA/PipeWire backend (Linux)
- [ ] Sample rate conversion
- [ ] Audio routing matrix
- [ ] Stream monitoring
- [ ] Unit tests passing

### 1.2 MIDI Engine
- [ ] MIDIBackend abstraction
- [ ] CoreMIDI backend (macOS)
- [ ] Windows MIDI backend
- [ ] ALSA MIDI backend (Linux)
- [ ] MIDI clock sync
- [ ] MIDI learn
- [ ] MPE support
- [ ] MIDI 2.0 support
- [ ] MIDI file I/O
- [ ] Unit tests passing

### 1.3 Transport System
- [ ] Transport controller
- [ ] Tempo map
- [ ] Metronome
- [ ] Marker system
- [ ] Undo/redo system
- [ ] Unit tests passing

### 1.4 Mixer Engine
- [ ] Channel strip
- [ ] Pan laws
- [ ] Mixer graph
- [ ] Automation system
- [ ] Unit tests passing

### 1.5 Audio Processing Graph
- [ ] AudioProcessor abstraction
- [ ] Audio graph (DAG)
- [ ] Parallel processing
- [ ] SIMD utilities
- [ ] Unit tests passing

### 1.6 Built-in DSP Effects
- [ ] Parametric EQ
- [ ] Compressor
- [ ] Delay
- [ ] Reverb
- [ ] Modulation effects
- [ ] Distortion effects
- [ ] Utility effects
- [ ] Analysis tools
- [ ] Unit tests passing

### 1.7 Audio Recording
- [ ] Recording engine
- [ ] Take lanes
- [ ] Loop recording
- [ ] Unit tests passing

### Final Verification
- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] Performance benchmarks meet targets
- [ ] No memory leaks (Valgrind clean)
- [ ] Documentation updated

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Audio callback latency | < 5ms at 256 samples |
| CPU usage (empty project) | < 1% |
| CPU usage (10 tracks, EQ+Comp each) | < 20% |
| Memory usage (empty project) | < 100MB |
| Build time (clean) | < 5 minutes |
| Test coverage | > 80% |
| MIDI latency | < 1ms |
| Automation accuracy | Sample-accurate |

---

*This TODO provides complete specifications for implementing Phase 1 of iDAWi. Execute tasks in order, write tests for each component, and verify acceptance criteria before moving to the next task.*
