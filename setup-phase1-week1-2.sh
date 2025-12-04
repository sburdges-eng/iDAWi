#!/bin/bash
# Phase 1 Week 1-2 Quick Start Script
# This script sets up the complete audio I/O foundation for iDAWi Phase 1

set -e

# Change to the script's directory (repository root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "iDAWi Phase 1 Week 1-2 Setup"
echo "=========================================="

# Create directory structure
echo "Creating directory structure..."
mkdir -p penta-core/src/audio/{backends,tests}
mkdir -p penta-core/include/penta/audio
mkdir -p penta-core/tests/unit/audio

# Create headers
echo "Creating audio device interface..."

# AudioDevice.h
cat > penta-core/include/penta/audio/AudioDevice.h << 'EOF'
#pragma once

#include <cstdint>
#include <string>
#include <vector>
#include <memory>
#include <functional>
#include <optional>

namespace penta::audio {

/// Audio device information structure
struct DeviceInfo {
    uint32_t id;
    std::string name;
    std::string driver;
    uint32_t input_channels = 0;
    uint32_t output_channels = 0;
    std::vector<uint32_t> sample_rates;
    float latency_ms = 0.0f;
    float output_latency_ms = 0.0f;
    bool is_default = false;
    bool is_input = true;
    bool supports_exclusive = false;
};

/// Audio buffer callback
using AudioCallback = std::function<void(
    const float* const* inputs,
    float* const* outputs,
    uint32_t num_samples,
    double sample_time)>;

/// Error callback
using ErrorCallback = std::function<void(const std::string& error)>;

/// Platform-independent audio device interface
class AudioDevice {
public:
    virtual ~AudioDevice() = default;

    virtual std::vector<DeviceInfo> enumerateInputDevices() = 0;
    virtual std::vector<DeviceInfo> enumerateOutputDevices() = 0;
    virtual std::optional<DeviceInfo> getDefaultInputDevice() = 0;
    virtual std::optional<DeviceInfo> getDefaultOutputDevice() = 0;

    virtual bool selectInputDevice(uint32_t device_id) = 0;
    virtual bool selectOutputDevice(uint32_t device_id) = 0;

    virtual bool setSampleRate(uint32_t sample_rate) = 0;
    virtual uint32_t getSampleRate() const = 0;

    virtual bool setBufferSize(uint32_t samples) = 0;
    virtual uint32_t getBufferSize() const = 0;

    virtual float getInputLatencyMs() const = 0;
    virtual float getOutputLatencyMs() const = 0;
    virtual uint32_t getInputLatencySamples() const = 0;
    virtual uint32_t getOutputLatencySamples() const = 0;

    virtual bool start() = 0;
    virtual bool stop() = 0;
    virtual bool isRunning() const = 0;
    virtual bool isInitialized() const = 0;

    virtual void setAudioCallback(AudioCallback callback) = 0;
    virtual void setErrorCallback(ErrorCallback callback) = 0;

    virtual std::string getInputDeviceName() const = 0;
    virtual std::string getOutputDeviceName() const = 0;
    virtual uint32_t getInputChannels() const = 0;
    virtual uint32_t getOutputChannels() const = 0;

    virtual float getCpuLoad() const = 0;
    virtual bool isCpuOverloaded() const = 0;
};

/// Factory function
std::unique_ptr<AudioDevice> createAudioDevice();

#ifdef __APPLE__
std::unique_ptr<AudioDevice> createCoreAudioDevice();
#elif _WIN32
std::unique_ptr<AudioDevice> createWASAPIDevice();
#elif __linux__
std::unique_ptr<AudioDevice> createALSADevice();
#endif

}  // namespace penta::audio
EOF

echo "✓ AudioDevice.h created"

# Create platform stubs
echo "Creating platform-specific device headers..."

cat > penta-core/include/penta/audio/CoreAudioDevice.h << 'EOF'
#pragma once
#include "AudioDevice.h"
#include <memory>

namespace penta::audio {

class CoreAudioDevice : public AudioDevice {
public:
    CoreAudioDevice();
    ~CoreAudioDevice() override;

    std::vector<DeviceInfo> enumerateInputDevices() override;
    std::vector<DeviceInfo> enumerateOutputDevices() override;
    std::optional<DeviceInfo> getDefaultInputDevice() override;
    std::optional<DeviceInfo> getDefaultOutputDevice() override;

    bool selectInputDevice(uint32_t device_id) override;
    bool selectOutputDevice(uint32_t device_id) override;

    bool setSampleRate(uint32_t sample_rate) override;
    uint32_t getSampleRate() const override;

    bool setBufferSize(uint32_t samples) override;
    uint32_t getBufferSize() const override;

    float getInputLatencyMs() const override;
    float getOutputLatencyMs() const override;
    uint32_t getInputLatencySamples() const override;
    uint32_t getOutputLatencySamples() const override;

    bool start() override;
    bool stop() override;
    bool isRunning() const override;
    bool isInitialized() const override;

    void setAudioCallback(AudioCallback callback) override;
    void setErrorCallback(ErrorCallback callback) override;

    std::string getInputDeviceName() const override;
    std::string getOutputDeviceName() const override;
    uint32_t getInputChannels() const override;
    uint32_t getOutputChannels() const override;

    float getCpuLoad() const override;
    bool isCpuOverloaded() const override;

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

}  // namespace penta::audio
EOF

cat > penta-core/include/penta/audio/WASAPIDevice.h << 'EOF'
#pragma once
#include "AudioDevice.h"
#include <memory>

namespace penta::audio {

class WASAPIDevice : public AudioDevice {
public:
    WASAPIDevice();
    ~WASAPIDevice() override;

    std::vector<DeviceInfo> enumerateInputDevices() override;
    std::vector<DeviceInfo> enumerateOutputDevices() override;
    std::optional<DeviceInfo> getDefaultInputDevice() override;
    std::optional<DeviceInfo> getDefaultOutputDevice() override;

    bool selectInputDevice(uint32_t device_id) override;
    bool selectOutputDevice(uint32_t device_id) override;

    bool setSampleRate(uint32_t sample_rate) override;
    uint32_t getSampleRate() const override;

    bool setBufferSize(uint32_t samples) override;
    uint32_t getBufferSize() const override;

    float getInputLatencyMs() const override;
    float getOutputLatencyMs() const override;
    uint32_t getInputLatencySamples() const override;
    uint32_t getOutputLatencySamples() const override;

    bool start() override;
    bool stop() override;
    bool isRunning() const override;
    bool isInitialized() const override;

    void setAudioCallback(AudioCallback callback) override;
    void setErrorCallback(ErrorCallback callback) override;

    std::string getInputDeviceName() const override;
    std::string getOutputDeviceName() const override;
    uint32_t getInputChannels() const override;
    uint32_t getOutputChannels() const override;

    float getCpuLoad() const override;
    bool isCpuOverloaded() const override;

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

}  // namespace penta::audio
EOF

cat > penta-core/include/penta/audio/ALSADevice.h << 'EOF'
#pragma once
#include "AudioDevice.h"
#include <memory>

namespace penta::audio {

class ALSADevice : public AudioDevice {
public:
    ALSADevice();
    ~ALSADevice() override;

    std::vector<DeviceInfo> enumerateInputDevices() override;
    std::vector<DeviceInfo> enumerateOutputDevices() override;
    std::optional<DeviceInfo> getDefaultInputDevice() override;
    std::optional<DeviceInfo> getDefaultOutputDevice() override;

    bool selectInputDevice(uint32_t device_id) override;
    bool selectOutputDevice(uint32_t device_id) override;

    bool setSampleRate(uint32_t sample_rate) override;
    uint32_t getSampleRate() const override;

    bool setBufferSize(uint32_t samples) override;
    uint32_t getBufferSize() const override;

    float getInputLatencyMs() const override;
    float getOutputLatencyMs() const override;
    uint32_t getInputLatencySamples() const override;
    uint32_t getOutputLatencySamples() const override;

    bool start() override;
    bool stop() override;
    bool isRunning() const override;
    bool isInitialized() const override;

    void setAudioCallback(AudioCallback callback) override;
    void setErrorCallback(ErrorCallback callback) override;

    std::string getInputDeviceName() const override;
    std::string getOutputDeviceName() const override;
    uint32_t getInputChannels() const override;
    uint32_t getOutputChannels() const override;

    float getCpuLoad() const override;
    bool isCpuOverloaded() const override;

private:
    class Impl;
    std::unique_ptr<Impl> impl_;
};

}  // namespace penta::audio
EOF

echo "✓ Platform-specific headers created"

# Create stub implementations
echo "Creating implementation files..."

cat > penta-core/src/audio/AudioDeviceFactory.cpp << 'EOF'
#include "penta/audio/AudioDevice.h"

#ifdef __APPLE__
#include "penta/audio/CoreAudioDevice.h"
#elif _WIN32
#include "penta/audio/WASAPIDevice.h"
#elif __linux__
#include "penta/audio/ALSADevice.h"
#endif

namespace penta::audio {

std::unique_ptr<AudioDevice> createAudioDevice() {
#ifdef __APPLE__
    return createCoreAudioDevice();
#elif _WIN32
    return createWASAPIDevice();
#elif __linux__
    return createALSADevice();
#else
    return nullptr;
#endif
}

}  // namespace penta::audio
EOF

cat > penta-core/src/audio/backends/CoreAudioDevice.cpp << 'EOF'
#include "penta/audio/CoreAudioDevice.h"
#include <iostream>
#include <mutex>

#ifdef __APPLE__
#include <CoreAudio/CoreAudio.h>
#include <AudioUnit/AudioUnit.h>
#endif

namespace penta::audio {

class CoreAudioDevice::Impl {
public:
    uint32_t sample_rate_ = 48000;
    uint32_t buffer_size_ = 256;
    AudioCallback audio_callback_;
    ErrorCallback error_callback_;
    std::mutex state_mutex_;
    bool running_ = false;
    float cpu_load_ = 0.0f;
};

CoreAudioDevice::CoreAudioDevice()
    : impl_(std::make_unique<Impl>()) {
    std::cout << "[CoreAudio] Device initialized\n";
}

CoreAudioDevice::~CoreAudioDevice() {
    stop();
}

std::vector<DeviceInfo> CoreAudioDevice::enumerateInputDevices() {
    std::vector<DeviceInfo> devices;
    DeviceInfo info;
    info.id = 0;
    info.name = "CoreAudio Default Input";
    info.driver = "CoreAudio";
    info.is_input = true;
    info.is_default = true;
    info.input_channels = 2;
    info.sample_rates = {44100, 48000, 96000};
    info.latency_ms = 10.0f;
    devices.push_back(info);
    return devices;
}

std::vector<DeviceInfo> CoreAudioDevice::enumerateOutputDevices() {
    std::vector<DeviceInfo> devices;
    DeviceInfo info;
    info.id = 0;
    info.name = "CoreAudio Default Output";
    info.driver = "CoreAudio";
    info.is_input = false;
    info.is_default = true;
    info.output_channels = 2;
    info.sample_rates = {44100, 48000, 96000};
    info.output_latency_ms = 10.0f;
    devices.push_back(info);
    return devices;
}

std::optional<DeviceInfo> CoreAudioDevice::getDefaultInputDevice() {
    auto devices = enumerateInputDevices();
    return devices.empty() ? std::optional<DeviceInfo>() : devices[0];
}

std::optional<DeviceInfo> CoreAudioDevice::getDefaultOutputDevice() {
    auto devices = enumerateOutputDevices();
    return devices.empty() ? std::optional<DeviceInfo>() : devices[0];
}

bool CoreAudioDevice::selectInputDevice(uint32_t device_id) {
    std::lock_guard<std::mutex> lock(impl_->state_mutex_);
    return true;
}

bool CoreAudioDevice::selectOutputDevice(uint32_t device_id) {
    std::lock_guard<std::mutex> lock(impl_->state_mutex_);
    return true;
}

bool CoreAudioDevice::setSampleRate(uint32_t sample_rate) {
    std::lock_guard<std::mutex> lock(impl_->state_mutex_);
    impl_->sample_rate_ = sample_rate;
    return true;
}

uint32_t CoreAudioDevice::getSampleRate() const {
    return impl_->sample_rate_;
}

bool CoreAudioDevice::setBufferSize(uint32_t samples) {
    std::lock_guard<std::mutex> lock(impl_->state_mutex_);
    impl_->buffer_size_ = samples;
    return true;
}

uint32_t CoreAudioDevice::getBufferSize() const {
    return impl_->buffer_size_;
}

float CoreAudioDevice::getInputLatencyMs() const {
    return (impl_->buffer_size_ * 1000.0f) / impl_->sample_rate_;
}

float CoreAudioDevice::getOutputLatencyMs() const {
    return (impl_->buffer_size_ * 1000.0f) / impl_->sample_rate_;
}

uint32_t CoreAudioDevice::getInputLatencySamples() const {
    return impl_->buffer_size_;
}

uint32_t CoreAudioDevice::getOutputLatencySamples() const {
    return impl_->buffer_size_;
}

bool CoreAudioDevice::start() {
    std::lock_guard<std::mutex> lock(impl_->state_mutex_);
    if (impl_->running_) return true;
    impl_->running_ = true;
    std::cout << "[CoreAudio] Started\n";
    return true;
}

bool CoreAudioDevice::stop() {
    std::lock_guard<std::mutex> lock(impl_->state_mutex_);
    if (!impl_->running_) return true;
    impl_->running_ = false;
    std::cout << "[CoreAudio] Stopped\n";
    return true;
}

bool CoreAudioDevice::isRunning() const {
    return impl_->running_;
}

bool CoreAudioDevice::isInitialized() const {
    return true;
}

void CoreAudioDevice::setAudioCallback(AudioCallback callback) {
    impl_->audio_callback_ = callback;
}

void CoreAudioDevice::setErrorCallback(ErrorCallback callback) {
    impl_->error_callback_ = callback;
}

std::string CoreAudioDevice::getInputDeviceName() const {
    return "CoreAudio Default Input";
}

std::string CoreAudioDevice::getOutputDeviceName() const {
    return "CoreAudio Default Output";
}

uint32_t CoreAudioDevice::getInputChannels() const {
    return 2;
}

uint32_t CoreAudioDevice::getOutputChannels() const {
    return 2;
}

float CoreAudioDevice::getCpuLoad() const {
    return impl_->cpu_load_;
}

bool CoreAudioDevice::isCpuOverloaded() const {
    return impl_->cpu_load_ > 0.95f;
}

std::unique_ptr<AudioDevice> createCoreAudioDevice() {
    return std::make_unique<CoreAudioDevice>();
}

}  // namespace penta::audio
EOF

cat > penta-core/src/audio/backends/WASAPIDevice.cpp << 'EOF'
#include "penta/audio/WASAPIDevice.h"
#include <iostream>
#include <mutex>

namespace penta::audio {

class WASAPIDevice::Impl {
public:
    uint32_t sample_rate_ = 48000;
    uint32_t buffer_size_ = 256;
    AudioCallback audio_callback_;
    ErrorCallback error_callback_;
    std::mutex state_mutex_;
    bool running_ = false;
    float cpu_load_ = 0.0f;
};

WASAPIDevice::WASAPIDevice()
    : impl_(std::make_unique<Impl>()) {
    std::cout << "[WASAPI] Device initialized\n";
}

WASAPIDevice::~WASAPIDevice() {
    stop();
}

std::vector<DeviceInfo> WASAPIDevice::enumerateInputDevices() {
    std::vector<DeviceInfo> devices;
    DeviceInfo info;
    info.id = 0;
    info.name = "WASAPI Default Input";
    info.driver = "WASAPI";
    info.is_input = true;
    info.is_default = true;
    info.input_channels = 2;
    info.sample_rates = {44100, 48000, 96000, 192000};
    info.latency_ms = 15.0f;
    devices.push_back(info);
    return devices;
}

std::vector<DeviceInfo> WASAPIDevice::enumerateOutputDevices() {
    std::vector<DeviceInfo> devices;
    DeviceInfo info;
    info.id = 0;
    info.name = "WASAPI Default Output";
    info.driver = "WASAPI";
    info.is_input = false;
    info.is_default = true;
    info.output_channels = 2;
    info.sample_rates = {44100, 48000, 96000, 192000};
    info.output_latency_ms = 15.0f;
    devices.push_back(info);
    return devices;
}

std::optional<DeviceInfo> WASAPIDevice::getDefaultInputDevice() {
    auto devices = enumerateInputDevices();
    return devices.empty() ? std::optional<DeviceInfo>() : devices[0];
}

std::optional<DeviceInfo> WASAPIDevice::getDefaultOutputDevice() {
    auto devices = enumerateOutputDevices();
    return devices.empty() ? std::optional<DeviceInfo>() : devices[0];
}

bool WASAPIDevice::selectInputDevice(uint32_t device_id) {
    std::lock_guard<std::mutex> lock(impl_->state_mutex_);
    return true;
}

bool WASAPIDevice::selectOutputDevice(uint32_t device_id) {
    std::lock_guard<std::mutex> lock(impl_->state_mutex_);
    return true;
}

bool WASAPIDevice::setSampleRate(uint32_t sample_rate) {
    std::lock_guard<std::mutex> lock(impl_->state_mutex_);
    impl_->sample_rate_ = sample_rate;
    return true;
}

uint32_t WASAPIDevice::getSampleRate() const {
    return impl_->sample_rate_;
}

bool WASAPIDevice::setBufferSize(uint32_t samples) {
    std::lock_guard<std::mutex> lock(impl_->state_mutex_);
    impl_->buffer_size_ = samples;
    return true;
}

uint32_t WASAPIDevice::getBufferSize() const {
    return impl_->buffer_size_;
}

float WASAPIDevice::getInputLatencyMs() const {
    return (impl_->buffer_size_ * 1000.0f) / impl_->sample_rate_;
}

float WASAPIDevice::getOutputLatencyMs() const {
    return (impl_->buffer_size_ * 1000.0f) / impl_->sample_rate_;
}

uint32_t WASAPIDevice::getInputLatencySamples() const {
    return impl_->buffer_size_;
}

uint32_t WASAPIDevice::getOutputLatencySamples() const {
    return impl_->buffer_size_;
}

bool WASAPIDevice::start() {
    std::lock_guard<std::mutex> lock(impl_->state_mutex_);
    if (impl_->running_) return true;
    impl_->running_ = true;
    std::cout << "[WASAPI] Started\n";
    return true;
}

bool WASAPIDevice::stop() {
    std::lock_guard<std::mutex> lock(impl_->state_mutex_);
    if (!impl_->running_) return true;
    impl_->running_ = false;
    std::cout << "[WASAPI] Stopped\n";
    return true;
}

bool WASAPIDevice::isRunning() const {
    return impl_->running_;
}

bool WASAPIDevice::isInitialized() const {
    return true;
}

void WASAPIDevice::setAudioCallback(AudioCallback callback) {
    impl_->audio_callback_ = callback;
}

void WASAPIDevice::setErrorCallback(ErrorCallback callback) {
    impl_->error_callback_ = callback;
}

std::string WASAPIDevice::getInputDeviceName() const {
    return "WASAPI Default Input";
}

std::string WASAPIDevice::getOutputDeviceName() const {
    return "WASAPI Default Output";
}

uint32_t WASAPIDevice::getInputChannels() const {
    return 2;
}

uint32_t WASAPIDevice::getOutputChannels() const {
    return 2;
}

float WASAPIDevice::getCpuLoad() const {
    return impl_->cpu_load_;
}

bool WASAPIDevice::isCpuOverloaded() const {
    return impl_->cpu_load_ > 0.95f;
}

std::unique_ptr<AudioDevice> createWASAPIDevice() {
    return std::make_unique<WASAPIDevice>();
}

}  // namespace penta::audio
EOF

cat > penta-core/src/audio/backends/ALSADevice.cpp << 'EOF'
#include "penta/audio/ALSADevice.h"
#include <iostream>
#include <mutex>

namespace penta::audio {

class ALSADevice::Impl {
public:
    uint32_t sample_rate_ = 48000;
    uint32_t buffer_size_ = 256;
    AudioCallback audio_callback_;
    ErrorCallback error_callback_;
    std::mutex state_mutex_;
    bool running_ = false;
    float cpu_load_ = 0.0f;
};

ALSADevice::ALSADevice()
    : impl_(std::make_unique<Impl>()) {
    std::cout << "[ALSA] Device initialized\n";
}

ALSADevice::~ALSADevice() {
    stop();
}

std::vector<DeviceInfo> ALSADevice::enumerateInputDevices() {
    std::vector<DeviceInfo> devices;
    DeviceInfo info;
    info.id = 0;
    info.name = "ALSA Default Input";
    info.driver = "ALSA";
    info.is_input = true;
    info.is_default = true;
    info.input_channels = 2;
    info.sample_rates = {44100, 48000, 96000};
    info.latency_ms = 20.0f;
    devices.push_back(info);
    return devices;
}

std::vector<DeviceInfo> ALSADevice::enumerateOutputDevices() {
    std::vector<DeviceInfo> devices;
    DeviceInfo info;
    info.id = 0;
    info.name = "ALSA Default Output";
    info.driver = "ALSA";
    info.is_input = false;
    info.is_default = true;
    info.output_channels = 2;
    info.sample_rates = {44100, 48000, 96000};
    info.output_latency_ms = 20.0f;
    devices.push_back(info);
    return devices;
}

std::optional<DeviceInfo> ALSADevice::getDefaultInputDevice() {
    auto devices = enumerateInputDevices();
    return devices.empty() ? std::optional<DeviceInfo>() : devices[0];
}

std::optional<DeviceInfo> ALSADevice::getDefaultOutputDevice() {
    auto devices = enumerateOutputDevices();
    return devices.empty() ? std::optional<DeviceInfo>() : devices[0];
}

bool ALSADevice::selectInputDevice(uint32_t device_id) {
    std::lock_guard<std::mutex> lock(impl_->state_mutex_);
    return true;
}

bool ALSADevice::selectOutputDevice(uint32_t device_id) {
    std::lock_guard<std::mutex> lock(impl_->state_mutex_);
    return true;
}

bool ALSADevice::setSampleRate(uint32_t sample_rate) {
    std::lock_guard<std::mutex> lock(impl_->state_mutex_);
    impl_->sample_rate_ = sample_rate;
    return true;
}

uint32_t ALSADevice::getSampleRate() const {
    return impl_->sample_rate_;
}

bool ALSADevice::setBufferSize(uint32_t samples) {
    std::lock_guard<std::mutex> lock(impl_->state_mutex_);
    impl_->buffer_size_ = samples;
    return true;
}

uint32_t ALSADevice::getBufferSize() const {
    return impl_->buffer_size_;
}

float ALSADevice::getInputLatencyMs() const {
    return (impl_->buffer_size_ * 1000.0f) / impl_->sample_rate_;
}

float ALSADevice::getOutputLatencyMs() const {
    return (impl_->buffer_size_ * 1000.0f) / impl_->sample_rate_;
}

uint32_t ALSADevice::getInputLatencySamples() const {
    return impl_->buffer_size_;
}

uint32_t ALSADevice::getOutputLatencySamples() const {
    return impl_->buffer_size_;
}

bool ALSADevice::start() {
    std::lock_guard<std::mutex> lock(impl_->state_mutex_);
    if (impl_->running_) return true;
    impl_->running_ = true;
    std::cout << "[ALSA] Started\n";
    return true;
}

bool ALSADevice::stop() {
    std::lock_guard<std::mutex> lock(impl_->state_mutex_);
    if (!impl_->running_) return true;
    impl_->running_ = false;
    std::cout << "[ALSA] Stopped\n";
    return true;
}

bool ALSADevice::isRunning() const {
    return impl_->running_;
}

bool ALSADevice::isInitialized() const {
    return true;
}

void ALSADevice::setAudioCallback(AudioCallback callback) {
    impl_->audio_callback_ = callback;
}

void ALSADevice::setErrorCallback(ErrorCallback callback) {
    impl_->error_callback_ = callback;
}

std::string ALSADevice::getInputDeviceName() const {
    return "ALSA Default Input";
}

std::string ALSADevice::getOutputDeviceName() const {
    return "ALSA Default Output";
}

uint32_t ALSADevice::getInputChannels() const {
    return 2;
}

uint32_t ALSADevice::getOutputChannels() const {
    return 2;
}

float ALSADevice::getCpuLoad() const {
    return impl_->cpu_load_;
}

bool ALSADevice::isCpuOverloaded() const {
    return impl_->cpu_load_ > 0.95f;
}

std::unique_ptr<AudioDevice> createALSADevice() {
    return std::make_unique<ALSADevice>();
}

}  // namespace penta::audio
EOF

echo "✓ Implementation files created"

echo ""
echo "✅ Phase 1 Week 1-2 Setup Complete!"
echo ""
echo "Files created:"
echo "  - penta-core/include/penta/audio/AudioDevice.h"
echo "  - penta-core/include/penta/audio/CoreAudioDevice.h"
echo "  - penta-core/include/penta/audio/WASAPIDevice.h"
echo "  - penta-core/include/penta/audio/ALSADevice.h"
echo "  - penta-core/src/audio/AudioDeviceFactory.cpp"
echo "  - penta-core/src/audio/backends/CoreAudioDevice.cpp"
echo "  - penta-core/src/audio/backends/WASAPIDevice.cpp"
echo "  - penta-core/src/audio/backends/ALSADevice.cpp"
echo ""
echo "Next steps:"
echo "  1. cd \"$SCRIPT_DIR\""
echo "  2. ./build.sh"
echo "  3. ./test.sh"
echo ""
