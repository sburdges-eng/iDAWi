#include "penta/transport/Transport.h"

#include <algorithm>
#include <chrono>
#include <cmath>
#include <mutex>

namespace penta::transport {

// =============================================================================
// Transport Implementation (PIMPL)
// =============================================================================

class Transport::Impl {
public:
    // =========================================================================
    // Configuration (immutable after construction)
    // =========================================================================

    TransportConfig config_;
    std::atomic<double> sampleRate_;
    std::atomic<uint32_t> ppq_;

    // =========================================================================
    // Transport State (atomic for lock-free RT access)
    // =========================================================================

    std::atomic<TransportState> state_{TransportState::Stopped};
    std::atomic<uint64_t> position_{0};           // Current sample position
    std::atomic<double> tempo_{kDefaultTempo};    // BPM
    std::atomic<double> positionQuarterNotes_{0}; // Cached QN position

    // Time signature (atomic struct members)
    std::atomic<uint8_t> timeSignatureNumerator_{4};
    std::atomic<uint8_t> timeSignatureDenominator_{4};

    // Loop region (atomic for thread safety)
    std::atomic<bool> loopEnabled_{false};
    std::atomic<uint64_t> loopStart_{0};
    std::atomic<uint64_t> loopEnd_{0};

    // Recording state
    std::atomic<bool> recording_{false};

    // =========================================================================
    // Cached Position Data (updated on advance)
    // =========================================================================

    TransportPosition cachedPosition_;
    mutable std::mutex positionMutex_;  // For full position struct access

    // =========================================================================
    // Tap Tempo State
    // =========================================================================

    static constexpr size_t kTapHistorySize = 4;
    static constexpr int64_t kTapTimeoutMs = 2000;

    std::array<std::chrono::steady_clock::time_point, kTapHistorySize> tapHistory_;
    size_t tapIndex_{0};
    size_t tapCount_{0};
    std::chrono::steady_clock::time_point lastTapTime_;
    std::mutex tapMutex_;

    // =========================================================================
    // Callbacks
    // =========================================================================

    TransportStateCallback stateCallback_;
    TransportPositionCallback positionCallback_;
    TransportTempoCallback tempoCallback_;
    TransportTimeSignatureCallback timeSignatureCallback_;
    TransportLoopCallback loopCallback_;
    std::mutex callbackMutex_;

    // =========================================================================
    // Construction
    // =========================================================================

    explicit Impl(const TransportConfig& config)
        : config_(config)
        , sampleRate_(config.sampleRate)
        , ppq_(config.ppq)
        , tempo_(config.initialTempo)
        , timeSignatureNumerator_(config.initialTimeSignature.numerator)
        , timeSignatureDenominator_(config.initialTimeSignature.denominator)
        , loopEnabled_(config.enableLooping)
        , loopStart_(config.loopStart)
        , loopEnd_(config.loopEnd)
    {
        updateCachedPosition();
    }

    // =========================================================================
    // State Management
    // =========================================================================

    bool play() noexcept {
        TransportState expected = state_.load(std::memory_order_acquire);

        // Can play from Stopped, Paused, or already Playing
        if (expected == TransportState::Recording) {
            return true;  // Already playing (recording)
        }

        TransportState newState = recording_.load() ?
            TransportState::Recording : TransportState::Playing;

        if (state_.compare_exchange_strong(expected, newState,
                                           std::memory_order_release,
                                           std::memory_order_relaxed)) {
            invokeStateCallback(newState);
            return true;
        }

        // Retry once if state changed
        if (expected != TransportState::Playing &&
            expected != TransportState::Recording) {
            state_.store(newState, std::memory_order_release);
            invokeStateCallback(newState);
        }

        return true;
    }

    bool pause() noexcept {
        TransportState current = state_.load(std::memory_order_acquire);

        if (current == TransportState::Stopped ||
            current == TransportState::Paused) {
            return true;  // Already paused/stopped
        }

        // Stop recording if active
        if (current == TransportState::Recording) {
            recording_ = false;
        }

        state_.store(TransportState::Paused, std::memory_order_release);
        invokeStateCallback(TransportState::Paused);
        return true;
    }

    bool stop(bool resetPosition) noexcept {
        TransportState current = state_.load(std::memory_order_acquire);

        if (current == TransportState::Stopped && !resetPosition) {
            return true;
        }

        recording_ = false;
        state_.store(TransportState::Stopped, std::memory_order_release);

        if (resetPosition) {
            position_.store(0, std::memory_order_release);
            positionQuarterNotes_.store(0.0, std::memory_order_release);
            updateCachedPosition();
            invokePositionCallback();
        }

        invokeStateCallback(TransportState::Stopped);
        return true;
    }

    bool record() noexcept {
        recording_ = true;
        TransportState current = state_.load(std::memory_order_acquire);

        if (current == TransportState::Playing ||
            current == TransportState::Recording) {
            state_.store(TransportState::Recording, std::memory_order_release);
            invokeStateCallback(TransportState::Recording);
            return true;
        }

        // Start playback with recording
        return play();
    }

    bool stopRecording() noexcept {
        recording_ = false;
        TransportState current = state_.load(std::memory_order_acquire);

        if (current == TransportState::Recording) {
            state_.store(TransportState::Playing, std::memory_order_release);
            invokeStateCallback(TransportState::Playing);
        }
        return true;
    }

    // =========================================================================
    // Position Management
    // =========================================================================

    void setPosition(uint64_t samplePosition) noexcept {
        position_.store(samplePosition, std::memory_order_release);
        updatePositionFromSamples(samplePosition);
        updateCachedPosition();
        invokePositionCallback();
    }

    void updatePositionFromSamples(uint64_t samples) noexcept {
        double sr = sampleRate_.load(std::memory_order_acquire);
        double bpm = tempo_.load(std::memory_order_acquire);

        if (sr > 0 && bpm > 0) {
            // quarterNotes = samples * (bpm / 60) / sampleRate
            double qn = static_cast<double>(samples) * bpm / (60.0 * sr);
            positionQuarterNotes_.store(qn, std::memory_order_release);
        }
    }

    void updateCachedPosition() {
        std::lock_guard<std::mutex> lock(positionMutex_);

        uint64_t samples = position_.load(std::memory_order_acquire);
        double sr = sampleRate_.load(std::memory_order_acquire);
        double bpm = tempo_.load(std::memory_order_acquire);
        uint32_t currentPpq = ppq_.load(std::memory_order_acquire);
        uint8_t tsNum = timeSignatureNumerator_.load(std::memory_order_acquire);
        uint8_t tsDenom = timeSignatureDenominator_.load(std::memory_order_acquire);

        cachedPosition_.samples = samples;
        cachedPosition_.tempo = bpm;
        cachedPosition_.timeSignature = TimeSignature{tsNum, tsDenom};

        if (sr > 0) {
            cachedPosition_.seconds = static_cast<double>(samples) / sr;
        }

        if (sr > 0 && bpm > 0) {
            // Calculate quarter notes
            double qn = static_cast<double>(samples) * bpm / (60.0 * sr);
            cachedPosition_.quarterNotes = qn;

            // Calculate PPQ ticks
            cachedPosition_.ppqTicks = static_cast<uint64_t>(qn * currentPpq);

            // Calculate MIDI ticks (24 PPQ)
            cachedPosition_.midiTicks = static_cast<uint32_t>(qn * kMidiPPQ);

            // Calculate bars and beats
            double beatDuration = 4.0 / tsDenom;  // In quarter notes
            double beatsPerBar = tsNum;
            double barDurationQN = beatsPerBar * beatDuration;

            if (barDurationQN > 0) {
                cachedPosition_.bars = static_cast<uint32_t>(qn / barDurationQN);
                double remainingQN = std::fmod(qn, barDurationQN);
                cachedPosition_.beats = remainingQN / beatDuration;
            }
        }
    }

    // =========================================================================
    // Audio Processing
    // =========================================================================

    bool advance(uint32_t numSamples) noexcept {
        TransportState current = state_.load(std::memory_order_acquire);

        if (current != TransportState::Playing &&
            current != TransportState::Recording) {
            return false;  // Not playing
        }

        uint64_t currentPos = position_.load(std::memory_order_acquire);
        uint64_t newPos = currentPos + numSamples;
        bool wrapped = false;

        // Handle looping
        if (loopEnabled_.load(std::memory_order_acquire)) {
            uint64_t loopEndPos = loopEnd_.load(std::memory_order_acquire);
            uint64_t loopStartPos = loopStart_.load(std::memory_order_acquire);

            if (loopEndPos > loopStartPos && newPos >= loopEndPos) {
                // Calculate exact wrap position
                uint64_t loopLength = loopEndPos - loopStartPos;
                uint64_t overshoot = newPos - loopEndPos;
                newPos = loopStartPos + (overshoot % loopLength);
                wrapped = true;
            }
        }

        position_.store(newPos, std::memory_order_release);
        updatePositionFromSamples(newPos);

        // Update cached position less frequently (every N calls or on wrap)
        // For now, update every time for accuracy
        updateCachedPosition();

        return wrapped;
    }

    // =========================================================================
    // Tap Tempo
    // =========================================================================

    void tapTempo() noexcept {
        std::lock_guard<std::mutex> lock(tapMutex_);

        auto now = std::chrono::steady_clock::now();
        auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(
            now - lastTapTime_).count();

        // Reset if too long since last tap
        if (elapsed > kTapTimeoutMs) {
            tapCount_ = 0;
            tapIndex_ = 0;
        }

        lastTapTime_ = now;
        tapHistory_[tapIndex_] = now;
        tapIndex_ = (tapIndex_ + 1) % kTapHistorySize;

        if (tapCount_ < kTapHistorySize) {
            ++tapCount_;
        }

        // Need at least 2 taps to calculate tempo
        if (tapCount_ < 2) {
            return;
        }

        // Calculate average interval
        int64_t totalInterval = 0;
        size_t intervals = 0;

        for (size_t i = 1; i < tapCount_; ++i) {
            size_t prevIdx = (tapIndex_ + kTapHistorySize - i - 1) % kTapHistorySize;
            size_t currIdx = (tapIndex_ + kTapHistorySize - i) % kTapHistorySize;

            auto interval = std::chrono::duration_cast<std::chrono::milliseconds>(
                tapHistory_[currIdx] - tapHistory_[prevIdx]).count();

            if (interval > 0 && interval < kTapTimeoutMs) {
                totalInterval += interval;
                ++intervals;
            }
        }

        if (intervals > 0) {
            double avgIntervalMs = static_cast<double>(totalInterval) / intervals;
            double newTempo = 60000.0 / avgIntervalMs;

            // Clamp to valid range
            newTempo = std::clamp(newTempo, kMinTempo, kMaxTempo);

            tempo_.store(newTempo, std::memory_order_release);
            invokeTempoCallback(newTempo);
        }
    }

    void resetTapTempo() noexcept {
        std::lock_guard<std::mutex> lock(tapMutex_);
        tapCount_ = 0;
        tapIndex_ = 0;
    }

    // =========================================================================
    // Conversion Utilities
    // =========================================================================

    uint64_t secondsToSamples(double seconds) const noexcept {
        double sr = sampleRate_.load(std::memory_order_acquire);
        return static_cast<uint64_t>(seconds * sr);
    }

    double samplesToSeconds(uint64_t samples) const noexcept {
        double sr = sampleRate_.load(std::memory_order_acquire);
        return sr > 0 ? static_cast<double>(samples) / sr : 0.0;
    }

    uint64_t quarterNotesToSamples(double quarterNotes) const noexcept {
        double sr = sampleRate_.load(std::memory_order_acquire);
        double bpm = tempo_.load(std::memory_order_acquire);

        if (bpm <= 0) return 0;

        // samples = quarterNotes * 60 * sampleRate / bpm
        return static_cast<uint64_t>(quarterNotes * 60.0 * sr / bpm);
    }

    double samplesToQuarterNotes(uint64_t samples) const noexcept {
        double sr = sampleRate_.load(std::memory_order_acquire);
        double bpm = tempo_.load(std::memory_order_acquire);

        if (sr <= 0 || bpm <= 0) return 0.0;

        return static_cast<double>(samples) * bpm / (60.0 * sr);
    }

    uint64_t barsBeatsToSamples(uint32_t bars, double beats) const noexcept {
        uint8_t tsNum = timeSignatureNumerator_.load(std::memory_order_acquire);
        uint8_t tsDenom = timeSignatureDenominator_.load(std::memory_order_acquire);

        double beatDuration = 4.0 / tsDenom;  // In quarter notes
        double barDurationQN = tsNum * beatDuration;
        double totalQN = bars * barDurationQN + beats * beatDuration;

        return quarterNotesToSamples(totalQN);
    }

    void samplesToBarsBeats(uint64_t samples, uint32_t& bars, double& beats) const noexcept {
        double qn = samplesToQuarterNotes(samples);

        uint8_t tsNum = timeSignatureNumerator_.load(std::memory_order_acquire);
        uint8_t tsDenom = timeSignatureDenominator_.load(std::memory_order_acquire);

        double beatDuration = 4.0 / tsDenom;
        double barDurationQN = tsNum * beatDuration;

        if (barDurationQN > 0) {
            bars = static_cast<uint32_t>(qn / barDurationQN);
            double remainingQN = std::fmod(qn, barDurationQN);
            beats = remainingQN / beatDuration;
        } else {
            bars = 0;
            beats = 0;
        }
    }

    // =========================================================================
    // Callback Invocation (non-RT thread)
    // =========================================================================

    void invokeStateCallback(TransportState newState) {
        std::lock_guard<std::mutex> lock(callbackMutex_);
        if (stateCallback_) {
            stateCallback_(newState);
        }
    }

    void invokePositionCallback() {
        std::lock_guard<std::mutex> lock(callbackMutex_);
        if (positionCallback_) {
            std::lock_guard<std::mutex> posLock(positionMutex_);
            positionCallback_(cachedPosition_);
        }
    }

    void invokeTempoCallback(double newTempo) {
        std::lock_guard<std::mutex> lock(callbackMutex_);
        if (tempoCallback_) {
            tempoCallback_(newTempo);
        }
    }

    void invokeTimeSignatureCallback(const TimeSignature& ts) {
        std::lock_guard<std::mutex> lock(callbackMutex_);
        if (timeSignatureCallback_) {
            timeSignatureCallback_(ts);
        }
    }

    void invokeLoopCallback(const LoopRegion& loop) {
        std::lock_guard<std::mutex> lock(callbackMutex_);
        if (loopCallback_) {
            loopCallback_(loop);
        }
    }
};

// =============================================================================
// Transport Public Interface Implementation
// =============================================================================

Transport::Transport()
    : impl_(std::make_unique<Impl>(TransportConfig{}))
{
}

Transport::Transport(const TransportConfig& config)
    : impl_(std::make_unique<Impl>(config))
{
}

Transport::~Transport() = default;

Transport::Transport(Transport&&) noexcept = default;
Transport& Transport::operator=(Transport&&) noexcept = default;

// =========================================================================
// Transport Control
// =========================================================================

bool Transport::play() noexcept {
    return impl_->play();
}

bool Transport::pause() noexcept {
    return impl_->pause();
}

bool Transport::stop(bool resetPosition) noexcept {
    return impl_->stop(resetPosition);
}

bool Transport::togglePlayPause() noexcept {
    TransportState current = impl_->state_.load(std::memory_order_acquire);
    if (current == TransportState::Playing ||
        current == TransportState::Recording) {
        return impl_->pause();
    }
    return impl_->play();
}

bool Transport::record() noexcept {
    return impl_->record();
}

bool Transport::stopRecording() noexcept {
    return impl_->stopRecording();
}

// =========================================================================
// State Queries
// =========================================================================

TransportState Transport::getState() const noexcept {
    return impl_->state_.load(std::memory_order_acquire);
}

bool Transport::isPlaying() const noexcept {
    TransportState state = impl_->state_.load(std::memory_order_acquire);
    return state == TransportState::Playing ||
           state == TransportState::Recording;
}

bool Transport::isPaused() const noexcept {
    return impl_->state_.load(std::memory_order_acquire) == TransportState::Paused;
}

bool Transport::isStopped() const noexcept {
    return impl_->state_.load(std::memory_order_acquire) == TransportState::Stopped;
}

bool Transport::isRecording() const noexcept {
    return impl_->state_.load(std::memory_order_acquire) == TransportState::Recording;
}

// =========================================================================
// Position Control
// =========================================================================

void Transport::setPosition(uint64_t samplePosition) noexcept {
    impl_->setPosition(samplePosition);
}

void Transport::setPositionSeconds(double seconds) noexcept {
    impl_->setPosition(impl_->secondsToSamples(seconds));
}

void Transport::setPositionQuarterNotes(double quarterNotes) noexcept {
    impl_->setPosition(impl_->quarterNotesToSamples(quarterNotes));
}

void Transport::setPositionBarsBeats(uint32_t bars, double beats) noexcept {
    impl_->setPosition(impl_->barsBeatsToSamples(bars, beats));
}

void Transport::movePosition(int64_t sampleDelta) noexcept {
    uint64_t current = impl_->position_.load(std::memory_order_acquire);
    int64_t newPos = static_cast<int64_t>(current) + sampleDelta;
    impl_->setPosition(newPos < 0 ? 0 : static_cast<uint64_t>(newPos));
}

void Transport::movePositionBeats(double beatDelta) noexcept {
    uint8_t tsDenom = impl_->timeSignatureDenominator_.load(std::memory_order_acquire);
    double beatDurationQN = 4.0 / tsDenom;
    double qnDelta = beatDelta * beatDurationQN;

    double currentQN = impl_->positionQuarterNotes_.load(std::memory_order_acquire);
    double newQN = std::max(0.0, currentQN + qnDelta);
    impl_->setPosition(impl_->quarterNotesToSamples(newQN));
}

void Transport::rewind() noexcept {
    impl_->setPosition(0);
}

// =========================================================================
// Position Queries
// =========================================================================

uint64_t Transport::getPosition() const noexcept {
    return impl_->position_.load(std::memory_order_acquire);
}

double Transport::getPositionSeconds() const noexcept {
    return impl_->samplesToSeconds(impl_->position_.load(std::memory_order_acquire));
}

double Transport::getPositionQuarterNotes() const noexcept {
    return impl_->positionQuarterNotes_.load(std::memory_order_acquire);
}

TransportPosition Transport::getTransportPosition() const noexcept {
    std::lock_guard<std::mutex> lock(impl_->positionMutex_);
    return impl_->cachedPosition_;
}

// =========================================================================
// Tempo Control
// =========================================================================

void Transport::setTempo(double bpm) noexcept {
    bpm = std::clamp(bpm, kMinTempo, kMaxTempo);
    impl_->tempo_.store(bpm, std::memory_order_release);
    impl_->updateCachedPosition();
    impl_->invokeTempoCallback(bpm);
}

double Transport::getTempo() const noexcept {
    return impl_->tempo_.load(std::memory_order_acquire);
}

void Transport::tapTempo() noexcept {
    impl_->tapTempo();
}

void Transport::resetTapTempo() noexcept {
    impl_->resetTapTempo();
}

// =========================================================================
// Time Signature
// =========================================================================

void Transport::setTimeSignature(const TimeSignature& ts) noexcept {
    setTimeSignature(ts.numerator, ts.denominator);
}

void Transport::setTimeSignature(uint8_t numerator, uint8_t denominator) noexcept {
    // Validate (denominator must be power of 2 between 1 and 32)
    if (numerator < 1 || numerator > 32) return;
    if (denominator < 1 || denominator > 32) return;
    if ((denominator & (denominator - 1)) != 0) return;  // Not power of 2

    impl_->timeSignatureNumerator_.store(numerator, std::memory_order_release);
    impl_->timeSignatureDenominator_.store(denominator, std::memory_order_release);
    impl_->updateCachedPosition();
    impl_->invokeTimeSignatureCallback(TimeSignature{numerator, denominator});
}

TimeSignature Transport::getTimeSignature() const noexcept {
    return TimeSignature{
        impl_->timeSignatureNumerator_.load(std::memory_order_acquire),
        impl_->timeSignatureDenominator_.load(std::memory_order_acquire)
    };
}

// =========================================================================
// Loop Control
// =========================================================================

void Transport::setLoopEnabled(bool enabled) noexcept {
    impl_->loopEnabled_.store(enabled, std::memory_order_release);

    LoopRegion loop;
    loop.startSample = impl_->loopStart_.load(std::memory_order_acquire);
    loop.endSample = impl_->loopEnd_.load(std::memory_order_acquire);
    loop.enabled = enabled;
    impl_->invokeLoopCallback(loop);
}

bool Transport::isLoopEnabled() const noexcept {
    return impl_->loopEnabled_.load(std::memory_order_acquire);
}

void Transport::setLoopPoints(uint64_t startSample, uint64_t endSample) noexcept {
    if (endSample <= startSample) return;

    impl_->loopStart_.store(startSample, std::memory_order_release);
    impl_->loopEnd_.store(endSample, std::memory_order_release);

    LoopRegion loop;
    loop.startSample = startSample;
    loop.endSample = endSample;
    loop.enabled = impl_->loopEnabled_.load(std::memory_order_acquire);
    impl_->invokeLoopCallback(loop);
}

void Transport::setLoopPointsSeconds(double startSeconds, double endSeconds) noexcept {
    setLoopPoints(impl_->secondsToSamples(startSeconds),
                  impl_->secondsToSamples(endSeconds));
}

void Transport::setLoopPointsQuarterNotes(double startQN, double endQN) noexcept {
    setLoopPoints(impl_->quarterNotesToSamples(startQN),
                  impl_->quarterNotesToSamples(endQN));
}

void Transport::setLoopBars(uint32_t startBar, uint32_t endBar) noexcept {
    setLoopPoints(impl_->barsBeatsToSamples(startBar, 0),
                  impl_->barsBeatsToSamples(endBar, 0));
}

LoopRegion Transport::getLoopRegion() const noexcept {
    LoopRegion loop;
    loop.startSample = impl_->loopStart_.load(std::memory_order_acquire);
    loop.endSample = impl_->loopEnd_.load(std::memory_order_acquire);
    loop.enabled = impl_->loopEnabled_.load(std::memory_order_acquire);
    return loop;
}

// =========================================================================
// Audio Processing
// =========================================================================

bool Transport::advance(uint32_t numSamples) noexcept {
    return impl_->advance(numSamples);
}

uint32_t Transport::getSampleOffsetForQuarterNote(double quarterNote) const noexcept {
    double currentQN = impl_->positionQuarterNotes_.load(std::memory_order_acquire);
    double deltaQN = quarterNote - currentQN;

    if (deltaQN < 0) return 0;

    uint64_t deltaSamples = impl_->quarterNotesToSamples(deltaQN);
    return static_cast<uint32_t>(std::min(deltaSamples, uint64_t(UINT32_MAX)));
}

bool Transport::isQuarterNoteInCurrentBuffer(double quarterNote,
                                              uint32_t bufferSize) const noexcept {
    double currentQN = impl_->positionQuarterNotes_.load(std::memory_order_acquire);
    double bufferEndQN = impl_->samplesToQuarterNotes(
        impl_->position_.load(std::memory_order_acquire) + bufferSize);

    return quarterNote >= currentQN && quarterNote < bufferEndQN;
}

// =========================================================================
// Configuration
// =========================================================================

void Transport::setSampleRate(double sampleRate) noexcept {
    if (sampleRate > 0) {
        impl_->sampleRate_.store(sampleRate, std::memory_order_release);
        impl_->updateCachedPosition();
    }
}

double Transport::getSampleRate() const noexcept {
    return impl_->sampleRate_.load(std::memory_order_acquire);
}

void Transport::setPPQ(uint32_t ppq) noexcept {
    if (ppq > 0) {
        impl_->ppq_.store(ppq, std::memory_order_release);
        impl_->updateCachedPosition();
    }
}

uint32_t Transport::getPPQ() const noexcept {
    return impl_->ppq_.load(std::memory_order_acquire);
}

// =========================================================================
// Callbacks
// =========================================================================

void Transport::setStateCallback(TransportStateCallback callback) {
    std::lock_guard<std::mutex> lock(impl_->callbackMutex_);
    impl_->stateCallback_ = std::move(callback);
}

void Transport::setPositionCallback(TransportPositionCallback callback) {
    std::lock_guard<std::mutex> lock(impl_->callbackMutex_);
    impl_->positionCallback_ = std::move(callback);
}

void Transport::setTempoCallback(TransportTempoCallback callback) {
    std::lock_guard<std::mutex> lock(impl_->callbackMutex_);
    impl_->tempoCallback_ = std::move(callback);
}

void Transport::setTimeSignatureCallback(TransportTimeSignatureCallback callback) {
    std::lock_guard<std::mutex> lock(impl_->callbackMutex_);
    impl_->timeSignatureCallback_ = std::move(callback);
}

void Transport::setLoopCallback(TransportLoopCallback callback) {
    std::lock_guard<std::mutex> lock(impl_->callbackMutex_);
    impl_->loopCallback_ = std::move(callback);
}

// =========================================================================
// Conversion Utilities
// =========================================================================

uint64_t Transport::secondsToSamples(double seconds) const noexcept {
    return impl_->secondsToSamples(seconds);
}

double Transport::samplesToSeconds(uint64_t samples) const noexcept {
    return impl_->samplesToSeconds(samples);
}

uint64_t Transport::quarterNotesToSamples(double quarterNotes) const noexcept {
    return impl_->quarterNotesToSamples(quarterNotes);
}

double Transport::samplesToQuarterNotes(uint64_t samples) const noexcept {
    return impl_->samplesToQuarterNotes(samples);
}

uint64_t Transport::beatsToSamples(double beats) const noexcept {
    uint8_t tsDenom = impl_->timeSignatureDenominator_.load(std::memory_order_acquire);
    double beatDurationQN = 4.0 / tsDenom;
    return impl_->quarterNotesToSamples(beats * beatDurationQN);
}

double Transport::samplesToBeats(uint64_t samples) const noexcept {
    double qn = impl_->samplesToQuarterNotes(samples);
    uint8_t tsDenom = impl_->timeSignatureDenominator_.load(std::memory_order_acquire);
    double beatDurationQN = 4.0 / tsDenom;
    return beatDurationQN > 0 ? qn / beatDurationQN : 0.0;
}

uint64_t Transport::barsBeatsToSamples(uint32_t bars, double beats) const noexcept {
    return impl_->barsBeatsToSamples(bars, beats);
}

void Transport::samplesToBarsBeats(uint64_t samples, uint32_t& bars,
                                    double& beats) const noexcept {
    impl_->samplesToBarsBeats(samples, bars, beats);
}

// =============================================================================
// Factory Functions
// =============================================================================

std::unique_ptr<Transport> createTransport() {
    return std::make_unique<Transport>();
}

std::unique_ptr<Transport> createTransport(const TransportConfig& config) {
    return std::make_unique<Transport>(config);
}

}  // namespace penta::transport
