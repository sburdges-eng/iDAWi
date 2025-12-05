#include "penta/midi/MIDIEngine.h"
#include "penta/midi/MIDIClock.h"

#include <algorithm>
#include <iostream>
#include <mutex>
#include <thread>

// RtMidi is a cross-platform MIDI library that wraps:
// - CoreMIDI on macOS
// - Windows Multimedia MIDI on Windows
// - ALSA on Linux
// If RtMidi is not available, we provide stub implementations
#if __has_include(<RtMidi.h>)
    #define PENTA_HAS_RTMIDI 1
    #include <RtMidi.h>
#else
    #define PENTA_HAS_RTMIDI 0
#endif

namespace penta::midi {

// =============================================================================
// MIDIEngine Implementation (PIMPL)
// =============================================================================

class MIDIEngineImpl {
public:
    MIDIEngineConfig config_;
    MIDIState state_;
    MIDIEngine::Statistics stats_;
    MIDIClockManager clockManager_;

    // Device lists
    std::vector<MIDIDeviceInfo> inputDevices_;
    std::vector<MIDIDeviceInfo> outputDevices_;

    // Lock-free buffers for RT-safe operation
    MIDIRingBuffer inputRing_;
    MIDIRingBuffer outputRing_;

    // Callbacks
    MIDIInputCallback inputCallback_;
    MIDITempoCallback tempoCallback_;
    MIDITransportCallback transportCallback_;
    MIDISongPositionCallback songPositionCallback_;

    // Mutex for device operations (non-RT)
    mutable std::mutex deviceMutex_;

    // State flags
    std::atomic<bool> initialized_{false};
    std::atomic<double> sampleRate_;

#if PENTA_HAS_RTMIDI
    // RtMidi instances
    std::vector<std::unique_ptr<RtMidiIn>> midiInputs_;
    std::vector<std::unique_ptr<RtMidiOut>> midiOutputs_;
    std::unique_ptr<RtMidiIn> virtualInput_;
    std::unique_ptr<RtMidiOut> virtualOutput_;
#endif

    explicit MIDIEngineImpl(const MIDIEngineConfig& config)
        : config_(config)
        , clockManager_(config.sampleRate)
        , sampleRate_(config.sampleRate)
    {
        clockManager_.setTempo(config.defaultTempo);

        switch (config.clockMode) {
            case MIDIClockMode::Internal:
                clockManager_.setMode(MIDIClockManager::Mode::Internal);
                break;
            case MIDIClockMode::External:
                clockManager_.setMode(MIDIClockManager::Mode::External);
                break;
            case MIDIClockMode::Auto:
                clockManager_.setMode(MIDIClockManager::Mode::Auto);
                break;
        }
    }

    ~MIDIEngineImpl() {
        shutdown();
    }

    // =========================================================================
    // Initialization
    // =========================================================================

    bool initialize() {
        if (initialized_.load()) {
            return true;
        }

#if PENTA_HAS_RTMIDI
        try {
            refreshDevices();
            initialized_ = true;
            return true;
        } catch (const RtMidiError& e) {
            std::cerr << "MIDI initialization failed: " << e.getMessage() << std::endl;
            return false;
        }
#else
        // Stub mode - always succeeds
        initialized_ = true;
        return true;
#endif
    }

    void shutdown() {
        if (!initialized_.load()) {
            return;
        }

#if PENTA_HAS_RTMIDI
        std::lock_guard<std::mutex> lock(deviceMutex_);

        // Close all inputs
        for (auto& input : midiInputs_) {
            if (input && input->isPortOpen()) {
                input->closePort();
            }
        }
        midiInputs_.clear();

        // Close all outputs
        for (auto& output : midiOutputs_) {
            if (output && output->isPortOpen()) {
                output->closePort();
            }
        }
        midiOutputs_.clear();

        // Close virtual ports
        if (virtualInput_) {
            virtualInput_->closePort();
            virtualInput_.reset();
        }
        if (virtualOutput_) {
            virtualOutput_->closePort();
            virtualOutput_.reset();
        }
#endif

        initialized_ = false;
    }

    // =========================================================================
    // Device Enumeration
    // =========================================================================

    void refreshDevices() {
        std::lock_guard<std::mutex> lock(deviceMutex_);

        inputDevices_.clear();
        outputDevices_.clear();

#if PENTA_HAS_RTMIDI
        try {
            // Enumerate inputs
            RtMidiIn tempIn;
            unsigned int numInputs = tempIn.getPortCount();

            for (unsigned int i = 0; i < numInputs; ++i) {
                MIDIDeviceInfo info;
                info.id = i;
                info.name = tempIn.getPortName(i);
                info.isInput = true;
                info.isOutput = false;
                info.isVirtual = false;
                info.isOpen = isInputOpen(i);
                inputDevices_.push_back(info);
            }

            // Enumerate outputs
            RtMidiOut tempOut;
            unsigned int numOutputs = tempOut.getPortCount();

            for (unsigned int i = 0; i < numOutputs; ++i) {
                MIDIDeviceInfo info;
                info.id = i;
                info.name = tempOut.getPortName(i);
                info.isInput = false;
                info.isOutput = true;
                info.isVirtual = false;
                info.isOpen = isOutputOpen(i);
                outputDevices_.push_back(info);
            }
        } catch (const RtMidiError& e) {
            std::cerr << "Device enumeration failed: " << e.getMessage() << std::endl;
        }
#else
        // Stub: Create fake devices for testing
        inputDevices_.push_back(MIDIDeviceInfo(0, "Virtual Input 1", true, false, true));
        inputDevices_.push_back(MIDIDeviceInfo(1, "Virtual Input 2", true, false, true));
        outputDevices_.push_back(MIDIDeviceInfo(0, "Virtual Output 1", false, true, true));
        outputDevices_.push_back(MIDIDeviceInfo(1, "Virtual Output 2", false, true, true));
#endif
    }

    bool isInputOpen(uint32_t deviceId) const {
#if PENTA_HAS_RTMIDI
        for (const auto& input : midiInputs_) {
            // Check if this input is open on the specified port
            if (input && input->isPortOpen()) {
                // RtMidi doesn't provide a way to query port ID, track externally
                return true;  // Simplified check
            }
        }
#endif
        (void)deviceId;
        return false;
    }

    bool isOutputOpen(uint32_t deviceId) const {
#if PENTA_HAS_RTMIDI
        for (const auto& output : midiOutputs_) {
            if (output && output->isPortOpen()) {
                return true;
            }
        }
#endif
        (void)deviceId;
        return false;
    }

    // =========================================================================
    // Device Control
    // =========================================================================

    bool openInputDevice(uint32_t deviceId) {
#if PENTA_HAS_RTMIDI
        std::lock_guard<std::mutex> lock(deviceMutex_);

        try {
            auto input = std::make_unique<RtMidiIn>();

            if (deviceId >= input->getPortCount()) {
                return false;
            }

            // Set callback for incoming MIDI
            input->setCallback(&MIDIEngineImpl::rtMidiCallback, this);

            // Open the port
            input->openPort(deviceId);

            // Configure message filtering
            input->ignoreTypes(!config_.enableSysEx,
                              !config_.enableTimeCode,
                              !config_.enableActiveSensing);

            midiInputs_.push_back(std::move(input));

            // Update device list
            for (auto& dev : inputDevices_) {
                if (dev.id == deviceId) {
                    dev.isOpen = true;
                    break;
                }
            }

            return true;
        } catch (const RtMidiError& e) {
            std::cerr << "Failed to open input " << deviceId << ": "
                      << e.getMessage() << std::endl;
            return false;
        }
#else
        (void)deviceId;
        return true;  // Stub always succeeds
#endif
    }

    bool closeInputDevice(uint32_t deviceId) {
#if PENTA_HAS_RTMIDI
        std::lock_guard<std::mutex> lock(deviceMutex_);

        // Find and close the device
        // Note: RtMidi doesn't track port IDs, so we close by index
        if (deviceId < midiInputs_.size() && midiInputs_[deviceId]) {
            midiInputs_[deviceId]->closePort();
            midiInputs_.erase(midiInputs_.begin() + deviceId);

            for (auto& dev : inputDevices_) {
                if (dev.id == deviceId) {
                    dev.isOpen = false;
                    break;
                }
            }
            return true;
        }
#endif
        (void)deviceId;
        return false;
    }

    bool openOutputDevice(uint32_t deviceId) {
#if PENTA_HAS_RTMIDI
        std::lock_guard<std::mutex> lock(deviceMutex_);

        try {
            auto output = std::make_unique<RtMidiOut>();

            if (deviceId >= output->getPortCount()) {
                return false;
            }

            output->openPort(deviceId);
            midiOutputs_.push_back(std::move(output));

            for (auto& dev : outputDevices_) {
                if (dev.id == deviceId) {
                    dev.isOpen = true;
                    break;
                }
            }

            return true;
        } catch (const RtMidiError& e) {
            std::cerr << "Failed to open output " << deviceId << ": "
                      << e.getMessage() << std::endl;
            return false;
        }
#else
        (void)deviceId;
        return true;
#endif
    }

    bool closeOutputDevice(uint32_t deviceId) {
#if PENTA_HAS_RTMIDI
        std::lock_guard<std::mutex> lock(deviceMutex_);

        if (deviceId < midiOutputs_.size() && midiOutputs_[deviceId]) {
            midiOutputs_[deviceId]->closePort();
            midiOutputs_.erase(midiOutputs_.begin() + deviceId);

            for (auto& dev : outputDevices_) {
                if (dev.id == deviceId) {
                    dev.isOpen = false;
                    break;
                }
            }
            return true;
        }
#endif
        (void)deviceId;
        return false;
    }

    // =========================================================================
    // Virtual Ports
    // =========================================================================

    bool createVirtualInput(const std::string& portName) {
#if PENTA_HAS_RTMIDI
        std::lock_guard<std::mutex> lock(deviceMutex_);

        try {
            virtualInput_ = std::make_unique<RtMidiIn>();
            virtualInput_->setCallback(&MIDIEngineImpl::rtMidiCallback, this);
            virtualInput_->openVirtualPort(portName);
            return true;
        } catch (const RtMidiError& e) {
            std::cerr << "Failed to create virtual input: "
                      << e.getMessage() << std::endl;
            return false;
        }
#else
        (void)portName;
        return true;
#endif
    }

    bool createVirtualOutput(const std::string& portName) {
#if PENTA_HAS_RTMIDI
        std::lock_guard<std::mutex> lock(deviceMutex_);

        try {
            virtualOutput_ = std::make_unique<RtMidiOut>();
            virtualOutput_->openVirtualPort(portName);
            return true;
        } catch (const RtMidiError& e) {
            std::cerr << "Failed to create virtual output: "
                      << e.getMessage() << std::endl;
            return false;
        }
#else
        (void)portName;
        return true;
#endif
    }

    // =========================================================================
    // MIDI Input Callback (called from RtMidi thread)
    // =========================================================================

#if PENTA_HAS_RTMIDI
    static void rtMidiCallback(double timestamp, std::vector<unsigned char>* message,
                               void* userData) {
        auto* impl = static_cast<MIDIEngineImpl*>(userData);
        if (!impl || !message || message->empty()) {
            return;
        }

        // Convert RtMidi message to MIDIEvent
        MIDIEvent event;
        event.timestamp = static_cast<uint64_t>(timestamp * 1000000);  // to microseconds
        event.status = (*message)[0];
        event.data1 = message->size() > 1 ? (*message)[1] : 0;
        event.data2 = message->size() > 2 ? (*message)[2] : 0;
        event.channel = event.status & 0x0F;

        impl->processIncomingEvent(event);
    }
#endif

    void processIncomingEvent(const MIDIEvent& event) {
        // Update statistics
        ++stats_.eventsReceived;
        stats_.lastEventTimestamp = event.timestamp;

        // Update state
        state_.processEvent(event);

        // Handle clock messages
        switch (event.getType()) {
            case MIDIEventType::TimingClock:
                clockManager_.receiveTick();
                ++stats_.clockTicksReceived;
                if (tempoCallback_) {
                    tempoCallback_(clockManager_.getTempo());
                }
                break;

            case MIDIEventType::Start:
                clockManager_.receiveStart();
                if (transportCallback_) {
                    transportCallback_(MIDIEventType::Start);
                }
                break;

            case MIDIEventType::Stop:
                clockManager_.receiveStop();
                if (transportCallback_) {
                    transportCallback_(MIDIEventType::Stop);
                }
                break;

            case MIDIEventType::Continue:
                clockManager_.receiveContinue();
                if (transportCallback_) {
                    transportCallback_(MIDIEventType::Continue);
                }
                break;

            case MIDIEventType::SongPosition:
                if (songPositionCallback_) {
                    uint32_t beats = (event.data2 << 7) | event.data1;
                    songPositionCallback_(beats);
                }
                break;

            default:
                break;
        }

        // Push to ring buffer for audio thread
        if (!inputRing_.push(event)) {
            ++stats_.eventsDropped;
        }

        // Call user callback
        if (inputCallback_) {
            inputCallback_(event);
        }
    }

    // =========================================================================
    // MIDI Output
    // =========================================================================

    bool sendEvent(const MIDIEvent& event) noexcept {
#if PENTA_HAS_RTMIDI
        // Build message
        std::vector<unsigned char> message;
        message.push_back(event.status);

        // Determine message length based on type
        MIDIEventType type = event.getType();

        switch (type) {
            case MIDIEventType::ProgramChange:
            case MIDIEventType::ChannelPressure:
                message.push_back(event.data1);
                break;

            case MIDIEventType::TimingClock:
            case MIDIEventType::Start:
            case MIDIEventType::Continue:
            case MIDIEventType::Stop:
            case MIDIEventType::ActiveSensing:
            case MIDIEventType::SystemReset:
                // No data bytes
                break;

            default:
                message.push_back(event.data1);
                message.push_back(event.data2);
                break;
        }

        // Send to all open outputs
        bool sent = false;
        {
            std::lock_guard<std::mutex> lock(deviceMutex_);

            for (auto& output : midiOutputs_) {
                if (output && output->isPortOpen()) {
                    try {
                        output->sendMessage(&message);
                        sent = true;
                    } catch (...) {
                        // Ignore send errors
                    }
                }
            }

            if (virtualOutput_ && virtualOutput_->isPortOpen()) {
                try {
                    virtualOutput_->sendMessage(&message);
                    sent = true;
                } catch (...) {
                    // Ignore
                }
            }
        }

        if (sent) {
            ++stats_.eventsSent;
        }

        return sent;
#else
        (void)event;
        ++stats_.eventsSent;
        return true;
#endif
    }

    void sendClockTick() noexcept {
        sendEvent(MIDIEvent::timingClock());
        ++stats_.clockTicksSent;
    }

    void processClockOutput(uint32_t numSamples) {
        std::array<uint32_t, 256> tickOffsets;
        size_t numTicks = clockManager_.generateTicks(numSamples, tickOffsets.begin());

        for (size_t i = 0; i < numTicks; ++i) {
            MIDIEvent clockEvent = MIDIEvent::timingClock(tickOffsets[i]);
            sendEvent(clockEvent);
            ++stats_.clockTicksSent;
        }
    }
};

// =============================================================================
// MIDIEngine Public Interface Implementation
// =============================================================================

MIDIEngine::MIDIEngine()
    : impl_(std::make_unique<MIDIEngineImpl>(MIDIEngineConfig{}))
{
}

MIDIEngine::MIDIEngine(const MIDIEngineConfig& config)
    : impl_(std::make_unique<MIDIEngineImpl>(config))
{
}

MIDIEngine::~MIDIEngine() = default;

bool MIDIEngine::initialize() {
    return impl_->initialize();
}

void MIDIEngine::shutdown() {
    impl_->shutdown();
}

bool MIDIEngine::isInitialized() const noexcept {
    return impl_->initialized_.load();
}

void MIDIEngine::refreshDevices() {
    impl_->refreshDevices();
}

std::vector<MIDIDeviceInfo> MIDIEngine::getInputDevices() const {
    std::lock_guard<std::mutex> lock(impl_->deviceMutex_);
    return impl_->inputDevices_;
}

std::vector<MIDIDeviceInfo> MIDIEngine::getOutputDevices() const {
    std::lock_guard<std::mutex> lock(impl_->deviceMutex_);
    return impl_->outputDevices_;
}

bool MIDIEngine::getInputDeviceInfo(uint32_t deviceId, MIDIDeviceInfo& info) const {
    std::lock_guard<std::mutex> lock(impl_->deviceMutex_);
    for (const auto& dev : impl_->inputDevices_) {
        if (dev.id == deviceId) {
            info = dev;
            return true;
        }
    }
    return false;
}

bool MIDIEngine::getOutputDeviceInfo(uint32_t deviceId, MIDIDeviceInfo& info) const {
    std::lock_guard<std::mutex> lock(impl_->deviceMutex_);
    for (const auto& dev : impl_->outputDevices_) {
        if (dev.id == deviceId) {
            info = dev;
            return true;
        }
    }
    return false;
}

bool MIDIEngine::openInputDevice(uint32_t deviceId) {
    return impl_->openInputDevice(deviceId);
}

bool MIDIEngine::closeInputDevice(uint32_t deviceId) {
    return impl_->closeInputDevice(deviceId);
}

bool MIDIEngine::isInputDeviceOpen(uint32_t deviceId) const {
    return impl_->isInputOpen(deviceId);
}

bool MIDIEngine::openOutputDevice(uint32_t deviceId) {
    return impl_->openOutputDevice(deviceId);
}

bool MIDIEngine::closeOutputDevice(uint32_t deviceId) {
    return impl_->closeOutputDevice(deviceId);
}

bool MIDIEngine::isOutputDeviceOpen(uint32_t deviceId) const {
    return impl_->isOutputOpen(deviceId);
}

size_t MIDIEngine::openInputDevicesByName(const std::string& namePattern) {
    std::lock_guard<std::mutex> lock(impl_->deviceMutex_);
    size_t count = 0;
    for (const auto& dev : impl_->inputDevices_) {
        if (dev.name.find(namePattern) != std::string::npos) {
            if (impl_->openInputDevice(dev.id)) {
                ++count;
            }
        }
    }
    return count;
}

size_t MIDIEngine::openOutputDevicesByName(const std::string& namePattern) {
    std::lock_guard<std::mutex> lock(impl_->deviceMutex_);
    size_t count = 0;
    for (const auto& dev : impl_->outputDevices_) {
        if (dev.name.find(namePattern) != std::string::npos) {
            if (impl_->openOutputDevice(dev.id)) {
                ++count;
            }
        }
    }
    return count;
}

void MIDIEngine::closeAllInputDevices() {
    std::lock_guard<std::mutex> lock(impl_->deviceMutex_);
    for (size_t i = impl_->inputDevices_.size(); i > 0; --i) {
        impl_->closeInputDevice(static_cast<uint32_t>(i - 1));
    }
}

void MIDIEngine::closeAllOutputDevices() {
    std::lock_guard<std::mutex> lock(impl_->deviceMutex_);
    for (size_t i = impl_->outputDevices_.size(); i > 0; --i) {
        impl_->closeOutputDevice(static_cast<uint32_t>(i - 1));
    }
}

void MIDIEngine::closeAllDevices() {
    closeAllInputDevices();
    closeAllOutputDevices();
}

bool MIDIEngine::createVirtualInput(const std::string& portName) {
    return impl_->createVirtualInput(portName);
}

bool MIDIEngine::createVirtualOutput(const std::string& portName) {
    return impl_->createVirtualOutput(portName);
}

bool MIDIEngine::closeVirtualInput() {
#if PENTA_HAS_RTMIDI
    if (impl_->virtualInput_) {
        impl_->virtualInput_->closePort();
        impl_->virtualInput_.reset();
        return true;
    }
#endif
    return false;
}

bool MIDIEngine::closeVirtualOutput() {
#if PENTA_HAS_RTMIDI
    if (impl_->virtualOutput_) {
        impl_->virtualOutput_->closePort();
        impl_->virtualOutput_.reset();
        return true;
    }
#endif
    return false;
}

size_t MIDIEngine::drainInputToBuffer(MIDIBuffer& buffer) noexcept {
    return impl_->inputRing_.drainTo(buffer);
}

bool MIDIEngine::hasInputEvents() const noexcept {
    return !impl_->inputRing_.isEmpty();
}

size_t MIDIEngine::pendingInputCount() const noexcept {
    return impl_->inputRing_.size();
}

bool MIDIEngine::sendEvent(const MIDIEvent& event) noexcept {
    return impl_->sendEvent(event);
}

size_t MIDIEngine::sendBuffer(const MIDIBuffer& buffer) noexcept {
    size_t sent = 0;
    for (const auto& event : buffer) {
        if (impl_->sendEvent(event)) {
            ++sent;
        }
    }
    return sent;
}

bool MIDIEngine::queueEvent(const MIDIEvent& event) noexcept {
    return impl_->outputRing_.push(event);
}

size_t MIDIEngine::flushOutput() noexcept {
    size_t sent = 0;
    MIDIEvent event;
    while (impl_->outputRing_.pop(event)) {
        if (impl_->sendEvent(event)) {
            ++sent;
        }
    }
    return sent;
}

bool MIDIEngine::sendNoteOn(uint8_t channel, uint8_t note, uint8_t velocity) noexcept {
    return sendEvent(MIDIEvent::noteOn(channel, note, velocity));
}

bool MIDIEngine::sendNoteOff(uint8_t channel, uint8_t note, uint8_t velocity) noexcept {
    return sendEvent(MIDIEvent::noteOff(channel, note, velocity));
}

bool MIDIEngine::sendControlChange(uint8_t channel, uint8_t controller, uint8_t value) noexcept {
    return sendEvent(MIDIEvent::controlChange(channel, controller, value));
}

bool MIDIEngine::sendProgramChange(uint8_t channel, uint8_t program) noexcept {
    return sendEvent(MIDIEvent::programChange(channel, program));
}

bool MIDIEngine::sendPitchBend(uint8_t channel, int16_t value) noexcept {
    return sendEvent(MIDIEvent::pitchBend(channel, value));
}

void MIDIEngine::sendAllNotesOff(uint8_t channel) noexcept {
    if (channel == 255) {
        for (uint8_t ch = 0; ch < 16; ++ch) {
            sendControlChange(ch, CC::AllNotesOff, 0);
        }
    } else {
        sendControlChange(channel & 0x0F, CC::AllNotesOff, 0);
    }
}

void MIDIEngine::sendResetAllControllers(uint8_t channel) noexcept {
    if (channel == 255) {
        for (uint8_t ch = 0; ch < 16; ++ch) {
            sendControlChange(ch, CC::ResetAllControllers, 0);
        }
    } else {
        sendControlChange(channel & 0x0F, CC::ResetAllControllers, 0);
    }
}

void MIDIEngine::setClockMode(MIDIClockMode mode) {
    switch (mode) {
        case MIDIClockMode::Internal:
            impl_->clockManager_.setMode(MIDIClockManager::Mode::Internal);
            break;
        case MIDIClockMode::External:
            impl_->clockManager_.setMode(MIDIClockManager::Mode::External);
            break;
        case MIDIClockMode::Auto:
            impl_->clockManager_.setMode(MIDIClockManager::Mode::Auto);
            break;
    }
}

MIDIClockMode MIDIEngine::getClockMode() const noexcept {
    switch (impl_->clockManager_.getMode()) {
        case MIDIClockManager::Mode::Internal:
            return MIDIClockMode::Internal;
        case MIDIClockManager::Mode::External:
            return MIDIClockMode::External;
        case MIDIClockManager::Mode::Auto:
            return MIDIClockMode::Auto;
    }
    return MIDIClockMode::Internal;
}

void MIDIEngine::setTempo(double bpm) {
    impl_->clockManager_.setTempo(bpm);
}

double MIDIEngine::getTempo() const noexcept {
    return impl_->clockManager_.getTempo();
}

double MIDIEngine::getExternalTempo() const noexcept {
    return impl_->clockManager_.getReceiver().getTempo();
}

bool MIDIEngine::isReceivingExternalClock() const noexcept {
    return impl_->clockManager_.isReceivingExternalClock();
}

void MIDIEngine::processClockOutput(uint32_t numSamples, double sampleRate) {
    impl_->clockManager_.setSampleRate(sampleRate);
    impl_->processClockOutput(numSamples);
}

void MIDIEngine::sendStart() {
    impl_->sendEvent(MIDIEvent::start());
    impl_->clockManager_.getGenerator().start();
}

void MIDIEngine::sendStop() {
    impl_->sendEvent(MIDIEvent::stop());
    impl_->clockManager_.getGenerator().stop();
}

void MIDIEngine::sendContinue() {
    impl_->sendEvent(MIDIEvent::continuePlay());
    impl_->clockManager_.getGenerator().continuePlay();
}

void MIDIEngine::sendSongPosition(uint32_t beats) {
    MIDIEvent event;
    event.status = static_cast<uint8_t>(MIDIEventType::SongPosition);
    event.data1 = beats & 0x7F;
    event.data2 = (beats >> 7) & 0x7F;
    impl_->sendEvent(event);
}

void MIDIEngine::setInputCallback(MIDIInputCallback callback) {
    impl_->inputCallback_ = std::move(callback);
}

void MIDIEngine::setTempoCallback(MIDITempoCallback callback) {
    impl_->tempoCallback_ = std::move(callback);
}

void MIDIEngine::setTransportCallback(MIDITransportCallback callback) {
    impl_->transportCallback_ = std::move(callback);
}

void MIDIEngine::setSongPositionCallback(MIDISongPositionCallback callback) {
    impl_->songPositionCallback_ = std::move(callback);
}

const MIDIState& MIDIEngine::getState() const noexcept {
    return impl_->state_;
}

void MIDIEngine::resetState() noexcept {
    impl_->state_.reset();
}

void MIDIEngine::setSampleRate(double sampleRate) {
    impl_->sampleRate_ = sampleRate;
    impl_->clockManager_.setSampleRate(sampleRate);
}

double MIDIEngine::getSampleRate() const noexcept {
    return impl_->sampleRate_;
}

const MIDIEngineConfig& MIDIEngine::getConfig() const noexcept {
    return impl_->config_;
}

const MIDIEngine::Statistics& MIDIEngine::getStatistics() const noexcept {
    return impl_->stats_;
}

void MIDIEngine::resetStatistics() noexcept {
    impl_->stats_.eventsReceived = 0;
    impl_->stats_.eventsSent = 0;
    impl_->stats_.eventsDropped = 0;
    impl_->stats_.clockTicksReceived = 0;
    impl_->stats_.clockTicksSent = 0;
    impl_->stats_.lastEventTimestamp = 0;
}

// =============================================================================
// Factory Functions
// =============================================================================

std::unique_ptr<MIDIEngine> createMIDIEngine() {
    return std::make_unique<MIDIEngine>();
}

std::unique_ptr<MIDIEngine> createMIDIEngine(const MIDIEngineConfig& config) {
    return std::make_unique<MIDIEngine>(config);
}

}  // namespace penta::midi
