#pragma once

#include "penta/midi/MIDITypes.h"
#include <atomic>
#include <chrono>
#include <cstdint>

namespace penta::midi {

// =============================================================================
// MIDI Clock Generator
// =============================================================================
// Generates MIDI clock ticks (24 PPQ) at the correct rate for a given tempo.
// Designed for sample-accurate timing in the audio thread.
// =============================================================================

class MIDIClockGenerator {
public:
    static constexpr uint8_t kPPQ = 24;  // Pulses per quarter note

    explicit MIDIClockGenerator(double sampleRate = 48000.0) noexcept
        : sampleRate_(sampleRate)
        , tempo_(120.0)
        , samplesPerTick_(calculateSamplesPerTick(120.0, sampleRate))
        , accumulator_(0.0)
        , running_(false)
        , tickCount_(0)
    {}

    // =========================================================================
    // Configuration
    // =========================================================================

    void setSampleRate(double sampleRate) noexcept {
        sampleRate_ = sampleRate;
        updateSamplesPerTick();
    }

    double getSampleRate() const noexcept { return sampleRate_; }

    void setTempo(double bpm) noexcept {
        tempo_ = bpm;
        updateSamplesPerTick();
    }

    double getTempo() const noexcept { return tempo_; }

    // =========================================================================
    // Transport Control
    // =========================================================================

    void start() noexcept {
        accumulator_ = 0.0;
        tickCount_ = 0;
        running_ = true;
    }

    void stop() noexcept {
        running_ = false;
    }

    void continuePlay() noexcept {
        running_ = true;
    }

    bool isRunning() const noexcept { return running_; }

    void reset() noexcept {
        accumulator_ = 0.0;
        tickCount_ = 0;
    }

    // =========================================================================
    // Clock Generation (call from audio thread)
    // =========================================================================

    // Process N samples and return the number of clock ticks that should
    // be generated, along with their sample offsets within the buffer
    template<typename OutputIterator>
    size_t process(uint32_t numSamples, OutputIterator tickOffsets) noexcept {
        if (!running_) {
            return 0;
        }

        size_t ticksGenerated = 0;

        for (uint32_t sample = 0; sample < numSamples; ++sample) {
            accumulator_ += 1.0;

            if (accumulator_ >= samplesPerTick_) {
                accumulator_ -= samplesPerTick_;
                *tickOffsets++ = sample;
                ++ticksGenerated;
                ++tickCount_;
            }
        }

        return ticksGenerated;
    }

    // Simpler version: just returns tick count
    size_t processSimple(uint32_t numSamples) noexcept {
        if (!running_) {
            return 0;
        }

        size_t ticksGenerated = 0;
        double samples = static_cast<double>(numSamples);

        while (accumulator_ + samples >= samplesPerTick_) {
            samples -= (samplesPerTick_ - accumulator_);
            accumulator_ = 0.0;
            ++ticksGenerated;
            ++tickCount_;
        }

        accumulator_ += samples;
        return ticksGenerated;
    }

    // =========================================================================
    // Position Queries
    // =========================================================================

    uint64_t getTickCount() const noexcept { return tickCount_; }

    // Get position in quarter notes
    double getQuarterNotePosition() const noexcept {
        return static_cast<double>(tickCount_) / kPPQ;
    }

    // Get position in beats (assuming 4/4 time)
    double getBeatPosition() const noexcept {
        return getQuarterNotePosition();
    }

    // Get position in bars (assuming 4/4 time)
    double getBarPosition() const noexcept {
        return getQuarterNotePosition() / 4.0;
    }

    // Set position by tick count
    void setTickPosition(uint64_t ticks) noexcept {
        tickCount_ = ticks;
        accumulator_ = 0.0;
    }

    // Set position by quarter notes
    void setQuarterNotePosition(double quarterNotes) noexcept {
        tickCount_ = static_cast<uint64_t>(quarterNotes * kPPQ);
        accumulator_ = 0.0;
    }

private:
    static double calculateSamplesPerTick(double bpm, double sampleRate) noexcept {
        // BPM = beats per minute
        // 24 ticks per beat (quarter note)
        // samples per tick = (samples per minute) / (ticks per minute)
        // = (sampleRate * 60) / (BPM * 24)
        return (sampleRate * 60.0) / (bpm * kPPQ);
    }

    void updateSamplesPerTick() noexcept {
        samplesPerTick_ = calculateSamplesPerTick(tempo_, sampleRate_);
    }

    double sampleRate_;
    double tempo_;
    double samplesPerTick_;
    double accumulator_;
    bool running_;
    uint64_t tickCount_;
};

// =============================================================================
// MIDI Clock Receiver
// =============================================================================
// Tracks incoming MIDI clock and calculates tempo from tick timing.
// Uses averaging to smooth out timing jitter.
// =============================================================================

class MIDIClockReceiver {
public:
    static constexpr size_t kTempoHistorySize = 24;  // One beat of ticks
    static constexpr double kMinTempo = 20.0;
    static constexpr double kMaxTempo = 300.0;
    static constexpr uint64_t kClockTimeoutMicros = 500000;  // 500ms = no clock

    MIDIClockReceiver() noexcept
        : tempo_(120.0)
        , tickCount_(0)
        , historyIndex_(0)
        , historyValid_(false)
        , receivingClock_(false)
        , lastTickTime_(std::chrono::steady_clock::now())
        , isPlaying_(false)
    {
        tickIntervals_.fill(0);
    }

    // =========================================================================
    // Clock Input (call when MIDI clock tick received)
    // =========================================================================

    void receiveTick() noexcept {
        auto now = std::chrono::steady_clock::now();
        auto interval = std::chrono::duration_cast<std::chrono::microseconds>(
            now - lastTickTime_).count();
        lastTickTime_ = now;

        ++tickCount_;

        // Store interval for tempo calculation
        if (interval > 0 && interval < 1000000) {  // Sanity check: < 1 second
            tickIntervals_[historyIndex_] = interval;
            historyIndex_ = (historyIndex_ + 1) % kTempoHistorySize;

            if (tickCount_ >= kTempoHistorySize) {
                historyValid_ = true;
            }

            if (historyValid_) {
                calculateTempo();
            }
        }

        receivingClock_ = true;
    }

    // =========================================================================
    // Transport Events
    // =========================================================================

    void receiveStart() noexcept {
        tickCount_ = 0;
        historyIndex_ = 0;
        historyValid_ = false;
        isPlaying_ = true;
    }

    void receiveContinue() noexcept {
        isPlaying_ = true;
    }

    void receiveStop() noexcept {
        isPlaying_ = false;
    }

    void receiveSongPosition(uint32_t beats) noexcept {
        // Song position is in MIDI beats (16th notes at 24 PPQ, so 6 ticks per beat)
        tickCount_ = static_cast<uint64_t>(beats) * 6;
    }

    // =========================================================================
    // Status Queries
    // =========================================================================

    double getTempo() const noexcept { return tempo_.load(std::memory_order_acquire); }

    uint64_t getTickCount() const noexcept { return tickCount_; }

    bool isPlaying() const noexcept { return isPlaying_; }

    bool isReceivingClock() noexcept {
        auto now = std::chrono::steady_clock::now();
        auto elapsed = std::chrono::duration_cast<std::chrono::microseconds>(
            now - lastTickTime_).count();

        if (elapsed > kClockTimeoutMicros) {
            receivingClock_ = false;
        }
        return receivingClock_;
    }

    // Get position in quarter notes
    double getQuarterNotePosition() const noexcept {
        return static_cast<double>(tickCount_) / 24.0;
    }

    // Get position in beats (assuming 4/4 time)
    double getBeatPosition() const noexcept {
        return getQuarterNotePosition();
    }

    // =========================================================================
    // Reset
    // =========================================================================

    void reset() noexcept {
        tempo_ = 120.0;
        tickCount_ = 0;
        historyIndex_ = 0;
        historyValid_ = false;
        receivingClock_ = false;
        isPlaying_ = false;
        tickIntervals_.fill(0);
    }

private:
    void calculateTempo() noexcept {
        // Average the tick intervals
        uint64_t sum = 0;
        for (const auto& interval : tickIntervals_) {
            sum += interval;
        }

        double avgIntervalMicros = static_cast<double>(sum) / kTempoHistorySize;

        if (avgIntervalMicros > 0) {
            // tempo = 60,000,000 microseconds/minute / (interval * 24 ticks/beat)
            double calculatedTempo = 60000000.0 / (avgIntervalMicros * 24.0);

            // Clamp to reasonable range
            if (calculatedTempo >= kMinTempo && calculatedTempo <= kMaxTempo) {
                tempo_.store(calculatedTempo, std::memory_order_release);
            }
        }
    }

    std::atomic<double> tempo_;
    uint64_t tickCount_;
    std::array<uint64_t, kTempoHistorySize> tickIntervals_;
    size_t historyIndex_;
    bool historyValid_;
    bool receivingClock_;
    std::chrono::steady_clock::time_point lastTickTime_;
    bool isPlaying_;
};

// =============================================================================
// MIDI Clock Manager
// =============================================================================
// Combines generator and receiver for flexible sync modes.
// =============================================================================

class MIDIClockManager {
public:
    enum class Mode {
        Internal,   // Generate clock from internal tempo
        External,   // Follow incoming MIDI clock
        Auto        // Use external if available, otherwise internal
    };

    explicit MIDIClockManager(double sampleRate = 48000.0) noexcept
        : generator_(sampleRate)
        , mode_(Mode::Internal)
    {}

    // =========================================================================
    // Configuration
    // =========================================================================

    void setMode(Mode mode) noexcept { mode_ = mode; }
    Mode getMode() const noexcept { return mode_; }

    void setSampleRate(double sampleRate) noexcept {
        generator_.setSampleRate(sampleRate);
    }

    // Set internal tempo (used when in Internal mode or External not receiving)
    void setTempo(double bpm) noexcept {
        generator_.setTempo(bpm);
    }

    // =========================================================================
    // Get Effective Tempo
    // =========================================================================

    double getTempo() noexcept {
        switch (mode_) {
            case Mode::External:
                return receiver_.getTempo();

            case Mode::Auto:
                if (receiver_.isReceivingClock()) {
                    return receiver_.getTempo();
                }
                return generator_.getTempo();

            case Mode::Internal:
            default:
                return generator_.getTempo();
        }
    }

    // =========================================================================
    // Clock Processing
    // =========================================================================

    // Process clock input
    void receiveTick() noexcept {
        receiver_.receiveTick();
    }

    void receiveStart() noexcept {
        receiver_.receiveStart();
        generator_.start();
    }

    void receiveStop() noexcept {
        receiver_.receiveStop();
        generator_.stop();
    }

    void receiveContinue() noexcept {
        receiver_.receiveContinue();
        generator_.continuePlay();
    }

    // Generate clock ticks
    template<typename OutputIterator>
    size_t generateTicks(uint32_t numSamples, OutputIterator offsets) noexcept {
        if (mode_ == Mode::External) {
            return 0;  // Don't generate in external mode
        }

        if (mode_ == Mode::Auto && receiver_.isReceivingClock()) {
            return 0;  // External clock active
        }

        return generator_.process(numSamples, offsets);
    }

    // =========================================================================
    // Status
    // =========================================================================

    bool isReceivingExternalClock() noexcept {
        return receiver_.isReceivingClock();
    }

    bool isPlaying() const noexcept {
        return receiver_.isPlaying() || generator_.isRunning();
    }

    // =========================================================================
    // Component Access
    // =========================================================================

    MIDIClockGenerator& getGenerator() noexcept { return generator_; }
    const MIDIClockGenerator& getGenerator() const noexcept { return generator_; }

    MIDIClockReceiver& getReceiver() noexcept { return receiver_; }
    const MIDIClockReceiver& getReceiver() const noexcept { return receiver_; }

private:
    MIDIClockGenerator generator_;
    MIDIClockReceiver receiver_;
    Mode mode_;
};

}  // namespace penta::midi
