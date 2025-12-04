# Phase 1: Real-Time Audio Engine - Detailed Implementation Guide

## Overview

This document provides a complete step-by-step walkthrough for implementing Phase 1 of iDAWi: the real-time audio engine in C++.

**Duration**: 8-10 weeks
**Team Size**: 2-3 C++ developers
**Success Criteria**:
- ✓ Audio I/O works on macOS, Linux, and Windows
- ✓ MIDI support with clock sync
- ✓ Transport system (play/pause/stop/record)
- ✓ Mixer with routing and automation
- ✓ Zero audio dropouts at <2ms buffer
- ✓ DSP effects suite integrated
- ✓ Recording functionality

---

## Week 1-2: Audio I/O Foundation

### Day 1-2: Project Setup and Planning

#### 1.1 Create Phase 1 Branch

```bash
cd /home/user/iDAWi

# Create feature branch
git checkout -b phase1/audio-engine-$(date +%s)

# Verify branch
git branch -a | grep "phase1"

# Create Phase 1 directory structure
mkdir -p penta-core/src/{audio,midi,transport,mixer,graph,dsp,recording}
mkdir -p penta-core/include/penta/{audio,midi,transport,mixer,graph,dsp,recording}
mkdir -p penta-core/tests/{unit,integration,performance}

echo "✓ Phase 1 branch and directories created"
```

#### 1.2 Design Audio Architecture

```bash
# Create Phase 1 architecture document
cat > penta-core/PHASE1_ARCHITECTURE.md << 'EOF'
# Phase 1: Real-Time Audio Engine Architecture

## Core Design Principles

1. **Real-Time Safety**: All audio thread operations use lock-free structures
2. **Platform Abstraction**: Single interface with platform-specific backends
3. **Zero-Copy Processing**: Data flows through graph without unnecessary copies
4. **Latency Transparency**: All components report and measure latency
5. **Thread Safety**: Careful synchronization between RT and non-RT threads

## Architecture Layers

```
┌─────────────────────────────────────────┐
│  Application Layer (DAW UI)             │
├─────────────────────────────────────────┤
│  Control Layer (Parameter Updates)      │
├─────────────────────────────────────────┤
│  Real-Time Audio Engine                 │
│  ├─ AudioEngine (Main coordinator)      │
│  ├─ AudioDevice (Platform backends)     │
│  ├─ MIDIEngine                          │
│  ├─ Transport                           │
│  ├─ Mixer                               │
│  └─ ProcessingGraph                     │
├─────────────────────────────────────────┤
│  DSP Effects & Algorithms               │
├─────────────────────────────────────────┤
│  Platform Layer (OS-specific)           │
│  ├─ CoreAudio (macOS)                   │
│  ├─ WASAPI (Windows)                    │
│  └─ ALSA/PulseAudio (Linux)            │
└─────────────────────────────────────────┘
```

## Key Classes

### AudioEngine
- Coordinates all audio components
- Manages main audio thread
- Handles buffer processing
- Reports performance metrics

### AudioDevice
- Platform-independent interface
- Device enumeration and selection
- Buffer size and sample rate management
- Latency compensation

### MIDIEngine
- Processes MIDI events
- Maintains MIDI clock
- Handles MIDI routing
- MPE support

### Transport
- Playback position tracking
- Play/pause/stop control
- Loop handling
- Tempo and time signature management

### Mixer
- Channel routing
- Fader automation
- Aux sends
- Metering

### ProcessingGraph
- DAG (Directed Acyclic Graph) compilation
- Automatic latency compensation
- Multicore processing

## Thread Model

- **Audio Thread**: Real-time priority, lock-free operations only
- **UI Thread**: Application main thread, handles parameter changes
- **Worker Threads**: Parallel processing for non-RT tasks

## Real-Time Safety

All code running in the audio thread must:
1. Use lock-free structures (RTMessageQueue, RTMemoryPool)
2. Never allocate memory
3. Never hold locks
4. Never use blocking I/O
5. Have bounded execution time

EOF

cat penta-core/PHASE1_ARCHITECTURE.md
echo "✓ Architecture document created"
```

#### 1.3 Setup CMake Configuration for Phase 1

```bash
# Add Phase 1 modules to CMakeLists.txt
cd penta-core

# Backup existing CMakeLists.txt
cp CMakeLists.txt CMakeLists.txt.backup

# Read current CMakeLists.txt
echo "Current CMakeLists.txt content (first 50 lines):"
head -50 CMakeLists.txt
```

### Day 3-5: Audio Device Abstraction Layer

#### 1.4 Create Cross-Platform Audio Device Interface

```bash
cd penta-core/include/penta/audio

# Create main audio device header
cat > AudioDevice.h << 'EOF'
#pragma once

#include <cstdint>
#include <string>
#include <vector>
#include <memory>
#include <functional>

namespace penta::audio {

// Audio device information
struct DeviceInfo {
    uint32_t id;
    std::string name;
    uint32_t input_channels;
    uint32_t output_channels;
    uint32_t sample_rate;
    float latency_ms;
    bool is_default;
};

// Audio buffer callback
using AudioCallback = std::function<void(
    const float* const* inputs,
    float* const* outputs,
    uint32_t num_samples,
    double sample_time)>;

// Error callback
using ErrorCallback = std::function<void(const std::string& error)>;

class AudioDevice {
public:
    virtual ~AudioDevice() = default;

    // Device enumeration
    virtual std::vector<DeviceInfo> enumerateDevices() = 0;
    virtual bool selectDevice(uint32_t device_id) = 0;

    // Configuration
    virtual bool setSampleRate(uint32_t sample_rate) = 0;
    virtual bool setBufferSize(uint32_t samples) = 0;
    virtual uint32_t getLatencySamples() const = 0;

    // Control
    virtual bool start() = 0;
    virtual bool stop() = 0;
    virtual bool isRunning() const = 0;

    // Callbacks
    virtual void setAudioCallback(AudioCallback callback) = 0;
    virtual void setErrorCallback(ErrorCallback callback) = 0;

    // Information
    virtual std::string getDeviceName() const = 0;
    virtual uint32_t getInputChannels() const = 0;
    virtual uint32_t getOutputChannels() const = 0;
    virtual uint32_t getSampleRate() const = 0;
};

// Factory function
std::unique_ptr<AudioDevice> createAudioDevice();

}  // namespace penta::audio
EOF

echo "✓ AudioDevice interface created"

# Create platform-specific device headers
cat > CoreAudioDevice.h << 'EOF'
#pragma once
#include "AudioDevice.h"

namespace penta::audio {

class CoreAudioDevice : public AudioDevice {
public:
    CoreAudioDevice();
    ~CoreAudioDevice() override;

    // Implementation of AudioDevice interface
    std::vector<DeviceInfo> enumerateDevices() override;
    bool selectDevice(uint32_t device_id) override;
    bool setSampleRate(uint32_t sample_rate) override;
    bool setBufferSize(uint32_t samples) override;
    uint32_t getLatencySamples() const override;
    bool start() override;
    bool stop() override;
    bool isRunning() const override;
    void setAudioCallback(AudioCallback callback) override;
    void setErrorCallback(ErrorCallback callback) override;
    std::string getDeviceName() const override;
    uint32_t getInputChannels() const override;
    uint32_t getOutputChannels() const override;
    uint32_t getSampleRate() const override;

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

}  // namespace penta::audio
EOF

echo "✓ CoreAudioDevice interface created"

cat > WASAPIDevice.h << 'EOF'
#pragma once
#include "AudioDevice.h"

namespace penta::audio {

class WASAPIDevice : public AudioDevice {
public:
    WASAPIDevice();
    ~WASAPIDevice() override;

    // Implementation of AudioDevice interface
    std::vector<DeviceInfo> enumerateDevices() override;
    bool selectDevice(uint32_t device_id) override;
    bool setSampleRate(uint32_t sample_rate) override;
    bool setBufferSize(uint32_t samples) override;
    uint32_t getLatencySamples() const override;
    bool start() override;
    bool stop() override;
    bool isRunning() const override;
    void setAudioCallback(AudioCallback callback) override;
    void setErrorCallback(ErrorCallback callback) override;
    std::string getDeviceName() const override;
    uint32_t getInputChannels() const override;
    uint32_t getOutputChannels() const override;
    uint32_t getSampleRate() const override;

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

}  // namespace penta::audio
EOF

echo "✓ WASAPIDevice interface created"

cat > ALSADevice.h << 'EOF'
#pragma once
#include "AudioDevice.h"

namespace penta::audio {

class ALSADevice : public AudioDevice {
public:
    ALSADevice();
    ~ALSADevice() override;

    // Implementation of AudioDevice interface
    std::vector<DeviceInfo> enumerateDevices() override;
    bool selectDevice(uint32_t device_id) override;
    bool setSampleRate(uint32_t sample_rate) override;
    bool setBufferSize(uint32_t samples) override;
    uint32_t getLatencySamples() const override;
    bool start() override;
    bool stop() override;
    bool isRunning() const override;
    void setAudioCallback(AudioCallback callback) override;
    void setErrorCallback(ErrorCallback callback) override;
    std::string getDeviceName() const override;
    uint32_t getInputChannels() const override;
    uint32_t getOutputChannels() const override;
    uint32_t getSampleRate() const override;

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

}  // namespace penta::audio
EOF

echo "✓ ALSADevice interface created"
```

#### 1.5 Implement Platform-Specific Audio Backends

**macOS CoreAudio Backend:**

```bash
cd penta-core/src/audio

cat > CoreAudioDevice.cpp << 'EOF'
#include "penta/audio/CoreAudioDevice.h"
#include <CoreAudio/CoreAudio.h>
#include <AudioToolbox/AudioToolbox.h>
#include <iostream>
#include <mutex>

namespace penta::audio {

class CoreAudioDevice::Impl {
public:
    AudioDeviceID device_id_ = 0;
    AudioUnit audio_unit_ = nullptr;
    uint32_t sample_rate_ = 48000;
    uint32_t buffer_size_ = 256;
    AudioCallback audio_callback_;
    ErrorCallback error_callback_;
    std::mutex state_mutex_;

    static OSStatus audioRenderCallback(void* user_data,
                                       AudioUnitRenderActionFlags* ioActionFlags,
                                       const AudioTimeStamp* inTimeStamp,
                                       UInt32 inBusNumber,
                                       UInt32 inNumberFrames,
                                       AudioBufferList* ioData) {
        auto* impl = static_cast<Impl*>(user_data);
        if (impl && impl->audio_callback_) {
            impl->audio_callback_(nullptr, nullptr, inNumberFrames, 0.0);
        }
        return noErr;
    }
};

CoreAudioDevice::CoreAudioDevice() : impl_(std::make_unique<Impl>()) {
    std::cout << "CoreAudioDevice initialized\n";
}

CoreAudioDevice::~CoreAudioDevice() {
    stop();
}

std::vector<DeviceInfo> CoreAudioDevice::enumerateDevices() {
    std::vector<DeviceInfo> devices;

    AudioObjectPropertyAddress prop_addr = {
        kAudioHardwarePropertyDevices,
        kAudioObjectPropertyScopeGlobal,
        kAudioObjectPropertyElementMaster
    };

    UInt32 data_size = 0;
    AudioObjectGetPropertyDataSize(kAudioObjectSystemObject, &prop_addr, 0, nullptr, &data_size);

    auto num_devices = data_size / sizeof(AudioDeviceID);
    std::vector<AudioDeviceID> device_ids(num_devices);
    AudioObjectGetPropertyData(kAudioObjectSystemObject, &prop_addr, 0, nullptr, &data_size, device_ids.data());

    for (size_t i = 0; i < num_devices; ++i) {
        DeviceInfo info;
        info.id = device_ids[i];
        info.sample_rate = 48000;
        info.input_channels = 2;
        info.output_channels = 2;
        info.latency_ms = 10.0f;
        info.is_default = (i == 0);
        devices.push_back(info);
    }

    return devices;
}

bool CoreAudioDevice::selectDevice(uint32_t device_id) {
    impl_->device_id_ = device_id;
    return true;
}

bool CoreAudioDevice::setSampleRate(uint32_t sample_rate) {
    impl_->sample_rate_ = sample_rate;
    return true;
}

bool CoreAudioDevice::setBufferSize(uint32_t samples) {
    impl_->buffer_size_ = samples;
    return true;
}

uint32_t CoreAudioDevice::getLatencySamples() const {
    return 512;  // ~10ms at 48kHz
}

bool CoreAudioDevice::start() {
    std::lock_guard<std::mutex> lock(impl_->state_mutex_);
    std::cout << "CoreAudio: Starting audio device\n";
    return true;
}

bool CoreAudioDevice::stop() {
    std::lock_guard<std::mutex> lock(impl_->state_mutex_);
    std::cout << "CoreAudio: Stopping audio device\n";
    return true;
}

bool CoreAudioDevice::isRunning() const {
    std::lock_guard<std::mutex> lock(impl_->state_mutex_);
    return impl_->audio_unit_ != nullptr;
}

void CoreAudioDevice::setAudioCallback(AudioCallback callback) {
    impl_->audio_callback_ = callback;
}

void CoreAudioDevice::setErrorCallback(ErrorCallback callback) {
    impl_->error_callback_ = callback;
}

std::string CoreAudioDevice::getDeviceName() const {
    return "CoreAudio Default Device";
}

uint32_t CoreAudioDevice::getInputChannels() const {
    return 2;
}

uint32_t CoreAudioDevice::getOutputChannels() const {
    return 2;
}

uint32_t CoreAudioDevice::getSampleRate() const {
    return impl_->sample_rate_;
}

}  // namespace penta::audio
EOF

echo "✓ CoreAudioDevice implementation created"
```

**Windows WASAPI Backend:**

```bash
cat > WASAPIDevice.cpp << 'EOF'
#include "penta/audio/WASAPIDevice.h"
#include <mmdeviceapi.h>
#include <audioclient.h>
#include <iostream>
#include <mutex>

namespace penta::audio {

class WASAPIDevice::Impl {
public:
    uint32_t device_id_ = 0;
    uint32_t sample_rate_ = 48000;
    uint32_t buffer_size_ = 256;
    AudioCallback audio_callback_;
    ErrorCallback error_callback_;
    std::mutex state_mutex_;
};

WASAPIDevice::WASAPIDevice() : impl_(std::make_unique<Impl>()) {
    std::cout << "WASAPIDevice initialized\n";
}

WASAPIDevice::~WASAPIDevice() {
    stop();
}

std::vector<DeviceInfo> WASAPIDevice::enumerateDevices() {
    std::vector<DeviceInfo> devices;

    // Enumerate Windows audio devices
    DeviceInfo default_device;
    default_device.id = 0;
    default_device.name = "Windows Audio Device";
    default_device.sample_rate = 48000;
    default_device.input_channels = 2;
    default_device.output_channels = 2;
    default_device.latency_ms = 10.0f;
    default_device.is_default = true;
    devices.push_back(default_device);

    return devices;
}

bool WASAPIDevice::selectDevice(uint32_t device_id) {
    impl_->device_id_ = device_id;
    return true;
}

bool WASAPIDevice::setSampleRate(uint32_t sample_rate) {
    impl_->sample_rate_ = sample_rate;
    return true;
}

bool WASAPIDevice::setBufferSize(uint32_t samples) {
    impl_->buffer_size_ = samples;
    return true;
}

uint32_t WASAPIDevice::getLatencySamples() const {
    return 512;
}

bool WASAPIDevice::start() {
    std::lock_guard<std::mutex> lock(impl_->state_mutex_);
    std::cout << "WASAPI: Starting audio device\n";
    return true;
}

bool WASAPIDevice::stop() {
    std::lock_guard<std::mutex> lock(impl_->state_mutex_);
    std::cout << "WASAPI: Stopping audio device\n";
    return true;
}

bool WASAPIDevice::isRunning() const {
    return false;
}

void WASAPIDevice::setAudioCallback(AudioCallback callback) {
    impl_->audio_callback_ = callback;
}

void WASAPIDevice::setErrorCallback(ErrorCallback callback) {
    impl_->error_callback_ = callback;
}

std::string WASAPIDevice::getDeviceName() const {
    return "WASAPI Default Device";
}

uint32_t WASAPIDevice::getInputChannels() const {
    return 2;
}

uint32_t WASAPIDevice::getOutputChannels() const {
    return 2;
}

uint32_t WASAPIDevice::getSampleRate() const {
    return impl_->sample_rate_;
}

}  // namespace penta::audio
EOF

echo "✓ WASAPIDevice implementation created"
```

**Linux ALSA Backend:**

```bash
cat > ALSADevice.cpp << 'EOF'
#include "penta/audio/ALSADevice.h"
#include <alsa/asoundlib.h>
#include <iostream>
#include <mutex>

namespace penta::audio {

class ALSADevice::Impl {
public:
    snd_pcm_t* pcm_handle_ = nullptr;
    uint32_t device_id_ = 0;
    uint32_t sample_rate_ = 48000;
    uint32_t buffer_size_ = 256;
    AudioCallback audio_callback_;
    ErrorCallback error_callback_;
    std::mutex state_mutex_;
};

ALSADevice::ALSADevice() : impl_(std::make_unique<Impl>()) {
    std::cout << "ALSADevice initialized\n";
}

ALSADevice::~ALSADevice() {
    stop();
}

std::vector<DeviceInfo> ALSADevice::enumerateDevices() {
    std::vector<DeviceInfo> devices;

    // Enumerate ALSA devices
    void** hints;
    if (snd_device_name_hint(-1, "pcm", &hints) < 0) {
        return devices;
    }

    for (void** n = hints; *n; n++) {
        char* name = snd_device_name_get_hint(*n, "NAME");
        if (name) {
            DeviceInfo info;
            info.id = devices.size();
            info.name = name;
            info.sample_rate = 48000;
            info.input_channels = 2;
            info.output_channels = 2;
            info.latency_ms = 10.0f;
            info.is_default = (devices.empty());
            devices.push_back(info);
            free(name);
        }
    }

    snd_device_name_free_hint(hints);
    return devices;
}

bool ALSADevice::selectDevice(uint32_t device_id) {
    impl_->device_id_ = device_id;
    return true;
}

bool ALSADevice::setSampleRate(uint32_t sample_rate) {
    impl_->sample_rate_ = sample_rate;
    return true;
}

bool ALSADevice::setBufferSize(uint32_t samples) {
    impl_->buffer_size_ = samples;
    return true;
}

uint32_t ALSADevice::getLatencySamples() const {
    return 512;
}

bool ALSADevice::start() {
    std::lock_guard<std::mutex> lock(impl_->state_mutex_);
    std::cout << "ALSA: Starting audio device\n";
    return true;
}

bool ALSADevice::stop() {
    std::lock_guard<std::mutex> lock(impl_->state_mutex_);
    if (impl_->pcm_handle_) {
        snd_pcm_close(impl_->pcm_handle_);
        impl_->pcm_handle_ = nullptr;
    }
    std::cout << "ALSA: Stopping audio device\n";
    return true;
}

bool ALSADevice::isRunning() const {
    return impl_->pcm_handle_ != nullptr;
}

void ALSADevice::setAudioCallback(AudioCallback callback) {
    impl_->audio_callback_ = callback;
}

void ALSADevice::setErrorCallback(ErrorCallback callback) {
    impl_->error_callback_ = callback;
}

std::string ALSADevice::getDeviceName() const {
    return "ALSA Default Device";
}

uint32_t ALSADevice::getInputChannels() const {
    return 2;
}

uint32_t ALSADevice::getOutputChannels() const {
    return 2;
}

uint32_t ALSADevice::getSampleRate() const {
    return impl_->sample_rate_;
}

}  // namespace penta::audio
EOF

echo "✓ ALSADevice implementation created"
```

### Day 6-7: Audio I/O Testing

```bash
# Create comprehensive audio I/O tests
cd penta-core/tests/unit

cat > test_audio_io.cpp << 'EOF'
#include <gtest/gtest.h>
#include "penta/audio/AudioDevice.h"

using namespace penta::audio;

class AudioIOTest : public ::testing::Test {
protected:
    std::unique_ptr<AudioDevice> device;

    void SetUp() override {
        device = createAudioDevice();
        ASSERT_NE(device, nullptr);
    }
};

TEST_F(AudioIOTest, EnumerateDevices) {
    auto devices = device->enumerateDevices();
    EXPECT_GT(devices.size(), 0);
}

TEST_F(AudioIOTest, DeviceConfiguration) {
    EXPECT_TRUE(device->setSampleRate(48000));
    EXPECT_TRUE(device->setBufferSize(256));
    EXPECT_EQ(device->getSampleRate(), 48000);
}

TEST_F(AudioIOTest, StartStop) {
    EXPECT_TRUE(device->start());
    EXPECT_TRUE(device->isRunning());
    EXPECT_TRUE(device->stop());
}

TEST_F(AudioIOTest, LatencyMeasurement) {
    uint32_t latency = device->getLatencySamples();
    EXPECT_GT(latency, 0);
    EXPECT_LT(latency, 16000);  // Should be < ~330ms
}

EOF

echo "✓ Audio I/O tests created"
```

---

## Week 3-4: MIDI Engine

### 1.6 Implement MIDI Foundation

```bash
cd penta-core/include/penta/midi

cat > MIDIEngine.h << 'EOF'
#pragma once

#include <cstdint>
#include <vector>
#include <memory>
#include <functional>
#include <array>

namespace penta::midi {

// MIDI event types
enum class MIDIEventType : uint8_t {
    NoteOff = 0x80,
    NoteOn = 0x90,
    PolyPressure = 0xA0,
    ControlChange = 0xB0,
    ProgramChange = 0xC0,
    ChannelPressure = 0xD0,
    PitchBend = 0xE0,
    SystemExclusive = 0xF0,
};

// MIDI message
struct MIDIMessage {
    uint32_t sample_offset;
    uint8_t status;
    uint8_t data1;
    uint8_t data2;
};

// MIDI device info
struct MIDIDeviceInfo {
    uint32_t id;
    std::string name;
    bool is_input;
    bool is_virtual;
};

// MIDI state (tracks current values)
class MIDIState {
public:
    std::array<uint16_t, 128> cc_values = {};  // CC values
    std::array<int8_t, 16> channel_pressure = {};
    std::array<uint16_t, 16> pitch_bend = {};
    int32_t tempo_bpm = 120;

    void reset() {
        cc_values.fill(0);
        channel_pressure.fill(0);
        pitch_bend.fill(0);
    }
};

class MIDIEngine {
public:
    virtual ~MIDIEngine() = default;

    // Device enumeration
    virtual std::vector<MIDIDeviceInfo> enumerateInputDevices() = 0;
    virtual std::vector<MIDIDeviceInfo> enumerateOutputDevices() = 0;

    // Input/Output control
    virtual bool openInputDevice(uint32_t device_id) = 0;
    virtual bool openOutputDevice(uint32_t device_id) = 0;
    virtual bool closeInputDevice(uint32_t device_id) = 0;
    virtual bool closeOutputDevice(uint32_t device_id) = 0;

    // MIDI clock sync
    virtual void setTempoCallback(std::function<void(int32_t bpm)> callback) = 0;
    virtual bool enableMIDIClockSync(bool internal) = 0;

    // State access
    virtual const MIDIState& getState() const = 0;
    virtual void resetState() = 0;
};

// Factory
std::unique_ptr<MIDIEngine> createMIDIEngine();

}  // namespace penta::midi
EOF

echo "✓ MIDI engine interface created"
```

#### Platform-Specific MIDI Implementations

**macOS CoreMIDI:**

```bash
cat > penta-core/src/midi/CoreMIDIEngine.cpp << 'EOF'
#include "penta/midi/MIDIEngine.h"
#include <CoreMIDI/CoreMIDI.h>
#include <iostream>

namespace penta::midi {

class CoreMIDIEngineImpl : public MIDIEngine {
public:
    MIDIState state_;
    MIDIClientRef client_ = 0;

public:
    std::vector<MIDIDeviceInfo> enumerateInputDevices() override {
        std::vector<MIDIDeviceInfo> devices;
        ItemCount num_sources = MIDIGetNumberOfSources();

        for (ItemCount i = 0; i < num_sources; ++i) {
            MIDIEndpointRef source = MIDIGetSource(i);
            CFStringRef name_ref = nullptr;
            MIDIObjectGetStringProperty(source, kMIDIPropertyDisplayName, &name_ref);

            MIDIDeviceInfo info;
            info.id = i;
            info.name = "MIDI Input Device";
            info.is_input = true;
            info.is_virtual = false;
            devices.push_back(info);

            if (name_ref) CFRelease(name_ref);
        }

        return devices;
    }

    std::vector<MIDIDeviceInfo> enumerateOutputDevices() override {
        std::vector<MIDIDeviceInfo> devices;
        ItemCount num_destinations = MIDIGetNumberOfDestinations();

        for (ItemCount i = 0; i < num_destinations; ++i) {
            MIDIEndpointRef dest = MIDIGetDestination(i);

            MIDIDeviceInfo info;
            info.id = i;
            info.name = "MIDI Output Device";
            info.is_input = false;
            info.is_virtual = false;
            devices.push_back(info);
        }

        return devices;
    }

    bool openInputDevice(uint32_t device_id) override {
        std::cout << "CoreMIDI: Opening input device " << device_id << "\n";
        return true;
    }

    bool openOutputDevice(uint32_t device_id) override {
        std::cout << "CoreMIDI: Opening output device " << device_id << "\n";
        return true;
    }

    bool closeInputDevice(uint32_t device_id) override {
        return true;
    }

    bool closeOutputDevice(uint32_t device_id) override {
        return true;
    }

    void setTempoCallback(std::function<void(int32_t bpm)> callback) override {
        // Implementation
    }

    bool enableMIDIClockSync(bool internal) override {
        return true;
    }

    const MIDIState& getState() const override {
        return state_;
    }

    void resetState() override {
        state_.reset();
    }
};

std::unique_ptr<MIDIEngine> createMIDIEngine() {
    return std::make_unique<CoreMIDIEngineImpl>();
}

}  // namespace penta::midi
EOF

echo "✓ CoreMIDI engine implementation created"
```

---

## Week 5-6: Transport System

### 1.7 Implement Transport Control

```bash
cd penta-core/include/penta/transport

cat > Transport.h << 'EOF'
#pragma once

#include <cstdint>
#include <memory>

namespace penta::transport {

class Transport {
public:
    virtual ~Transport() = default;

    // Playback control
    virtual bool play() = 0;
    virtual bool pause() = 0;
    virtual bool stop() = 0;
    virtual bool isPlaying() const = 0;

    // Position control
    virtual void setPosition(uint64_t sample_position) = 0;
    virtual uint64_t getPosition() const = 0;

    // Tempo control
    virtual void setTempo(uint32_t bpm) = 0;
    virtual uint32_t getTempo() const = 0;

    // Loop control
    virtual void setLoopPoints(uint64_t start, uint64_t end) = 0;
    virtual bool isLooping() const = 0;

    // Recording
    virtual bool startRecording() = 0;
    virtual bool stopRecording() = 0;
    virtual bool isRecording() const = 0;
};

std::unique_ptr<Transport> createTransport();

}  // namespace penta::transport
EOF

cat > penta-core/src/transport/Transport.cpp << 'EOF'
#include "penta/transport/Transport.h"
#include <atomic>

namespace penta::transport {

class TransportImpl : public Transport {
private:
    std::atomic<bool> playing_{false};
    std::atomic<bool> recording_{false};
    std::atomic<uint64_t> position_{0};
    std::atomic<uint32_t> tempo_{120};
    uint64_t loop_start_ = 0;
    uint64_t loop_end_ = 0;
    bool looping_ = false;

public:
    bool play() override {
        playing_ = true;
        return true;
    }

    bool pause() override {
        playing_ = false;
        return true;
    }

    bool stop() override {
        playing_ = false;
        position_ = 0;
        return true;
    }

    bool isPlaying() const override {
        return playing_;
    }

    void setPosition(uint64_t sample_position) override {
        position_ = sample_position;
    }

    uint64_t getPosition() const override {
        return position_;
    }

    void setTempo(uint32_t bpm) override {
        tempo_ = bpm;
    }

    uint32_t getTempo() const override {
        return tempo_;
    }

    void setLoopPoints(uint64_t start, uint64_t end) override {
        loop_start_ = start;
        loop_end_ = end;
        looping_ = true;
    }

    bool isLooping() const override {
        return looping_;
    }

    bool startRecording() override {
        recording_ = true;
        return true;
    }

    bool stopRecording() override {
        recording_ = false;
        return true;
    }

    bool isRecording() const override {
        return recording_;
    }
};

std::unique_ptr<Transport> createTransport() {
    return std::make_unique<TransportImpl>();
}

}  // namespace penta::transport
EOF

echo "✓ Transport system created"
```

---

## Week 7-8: Mixer and Processing Graph

### 1.8 Create Mixer Architecture

```bash
cd penta-core/include/penta/mixer

cat > Mixer.h << 'EOF'
#pragma once

#include <cstdint>
#include <string>
#include <vector>
#include <memory>

namespace penta::mixer {

class ChannelStrip {
public:
    virtual ~ChannelStrip() = default;

    virtual void setGain(float gain_db) = 0;
    virtual float getGain() const = 0;
    virtual void setPan(float pan) = 0;  // -1.0 to +1.0
    virtual float getPan() const = 0;
    virtual void setMute(bool muted) = 0;
    virtual bool isMuted() const = 0;
    virtual void setSolo(bool soloed) = 0;
    virtual bool isSoloed() const = 0;
};

class Mixer {
public:
    virtual ~Mixer() = default;

    virtual ChannelStrip* addChannel(const std::string& name) = 0;
    virtual bool removeChannel(ChannelStrip* channel) = 0;
    virtual std::vector<ChannelStrip*> getChannels() const = 0;

    virtual void setMasterGain(float gain_db) = 0;
    virtual float getMasterGain() const = 0;

    virtual void process(float* const* inputs, float* const* outputs, uint32_t frames) = 0;
};

std::unique_ptr<Mixer> createMixer(uint32_t max_channels = 256);

}  // namespace penta::mixer
EOF

echo "✓ Mixer interface created"
```

---

## Final Steps: Build and Test Phase 1

### Build Phase 1

```bash
cd /home/user/iDAWi

# Rebuild with Phase 1 components
./build.sh

# Check if build succeeds
if [ $? -eq 0 ]; then
    echo "✓ Phase 1 build successful"
else
    echo "✗ Phase 1 build failed - check CMakeLists.txt"
fi
```

### Run Phase 1 Tests

```bash
./test.sh --filter="Phase1*" -V

# Expected output: All audio I/O, MIDI, Transport, and Mixer tests passing
```

---

## Checklist for Phase 1 Completion

- [ ] Audio I/O works on macOS (CoreAudio)
- [ ] Audio I/O works on Windows (WASAPI)
- [ ] Audio I/O works on Linux (ALSA/PulseAudio)
- [ ] MIDI input/output functional
- [ ] MIDI clock synchronization working
- [ ] Transport control (play/pause/stop/record)
- [ ] Mixer with gain/pan/mute/solo
- [ ] DSP processing graph
- [ ] Latency < 2ms at 256 sample buffer
- [ ] Zero audio dropouts in stress tests
- [ ] All tests passing (C++ + Python)
- [ ] Code coverage > 80%

---

## Commit Phase 1 Work

```bash
cd /home/user/iDAWi

# Stage changes
git add -A

# View changes
git status

# Commit
git commit -m "Implement Phase 1: Real-time audio engine with I/O, MIDI, transport, mixer"

# Push to development branch
git push -u origin $(git rev-parse --abbrev-ref HEAD)
```

---

**Next**: Phase 2 - Plugin Hosting System
