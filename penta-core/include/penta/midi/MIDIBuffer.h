#pragma once

#include "penta/midi/MIDITypes.h"
#include <algorithm>
#include <atomic>
#include <cstring>

namespace penta::midi {

// =============================================================================
// RT-Safe MIDI Event Buffer
// =============================================================================
// Pre-allocated, fixed-size buffer for storing MIDI events during audio
// processing. Designed for single-producer, single-consumer usage pattern.
//
// Producer (non-RT thread): Calls addEvent() to queue incoming MIDI
// Consumer (RT audio thread): Iterates through events via begin()/end()
//
// Thread safety is achieved through atomic index operations without locks.
// =============================================================================

class MIDIBuffer {
public:
    static constexpr size_t kDefaultCapacity = 4096;

    explicit MIDIBuffer(size_t capacity = kDefaultCapacity) noexcept
        : capacity_(capacity)
        , size_(0)
    {
        events_.resize(capacity_);
    }

    // Non-copyable but movable
    MIDIBuffer(const MIDIBuffer&) = delete;
    MIDIBuffer& operator=(const MIDIBuffer&) = delete;

    MIDIBuffer(MIDIBuffer&& other) noexcept
        : events_(std::move(other.events_))
        , capacity_(other.capacity_)
        , size_(other.size_.load())
    {
        other.size_ = 0;
    }

    MIDIBuffer& operator=(MIDIBuffer&& other) noexcept {
        if (this != &other) {
            events_ = std::move(other.events_);
            capacity_ = other.capacity_;
            size_ = other.size_.load();
            other.size_ = 0;
        }
        return *this;
    }

    // ==========================================================================
    // Buffer Management (non-RT safe, call from non-audio thread)
    // ==========================================================================

    void reserve(size_t newCapacity) {
        if (newCapacity > capacity_) {
            events_.resize(newCapacity);
            capacity_ = newCapacity;
        }
    }

    // ==========================================================================
    // Event Addition (RT-safe if within capacity)
    // ==========================================================================

    bool addEvent(const MIDIEvent& event) noexcept {
        size_t currentSize = size_.load(std::memory_order_acquire);
        if (currentSize >= capacity_) {
            return false;  // Buffer full
        }

        events_[currentSize] = event;
        size_.store(currentSize + 1, std::memory_order_release);
        return true;
    }

    bool addNoteOn(uint8_t channel, uint8_t note, uint8_t velocity,
                   uint32_t sampleOffset = 0) noexcept {
        return addEvent(MIDIEvent::noteOn(channel, note, velocity, sampleOffset));
    }

    bool addNoteOff(uint8_t channel, uint8_t note, uint8_t velocity = 0,
                    uint32_t sampleOffset = 0) noexcept {
        return addEvent(MIDIEvent::noteOff(channel, note, velocity, sampleOffset));
    }

    bool addControlChange(uint8_t channel, uint8_t controller, uint8_t value,
                          uint32_t sampleOffset = 0) noexcept {
        return addEvent(MIDIEvent::controlChange(channel, controller, value, sampleOffset));
    }

    bool addPitchBend(uint8_t channel, int16_t value,
                      uint32_t sampleOffset = 0) noexcept {
        return addEvent(MIDIEvent::pitchBend(channel, value, sampleOffset));
    }

    bool addProgramChange(uint8_t channel, uint8_t program,
                          uint32_t sampleOffset = 0) noexcept {
        return addEvent(MIDIEvent::programChange(channel, program, sampleOffset));
    }

    // ==========================================================================
    // Buffer Access (RT-safe)
    // ==========================================================================

    void clear() noexcept {
        size_.store(0, std::memory_order_release);
    }

    size_t size() const noexcept {
        return size_.load(std::memory_order_acquire);
    }

    size_t capacity() const noexcept {
        return capacity_;
    }

    bool isEmpty() const noexcept {
        return size() == 0;
    }

    bool isFull() const noexcept {
        return size() >= capacity_;
    }

    // Direct access (RT-safe reads)
    const MIDIEvent& operator[](size_t index) const noexcept {
        return events_[index];
    }

    MIDIEvent& operator[](size_t index) noexcept {
        return events_[index];
    }

    // Iterator support for range-based for loops
    using iterator = MIDIEvent*;
    using const_iterator = const MIDIEvent*;

    const_iterator begin() const noexcept {
        return events_.data();
    }

    const_iterator end() const noexcept {
        return events_.data() + size_.load(std::memory_order_acquire);
    }

    iterator begin() noexcept {
        return events_.data();
    }

    iterator end() noexcept {
        return events_.data() + size_.load(std::memory_order_acquire);
    }

    // ==========================================================================
    // Sorting (call before processing to ensure sample-accurate playback)
    // ==========================================================================

    void sortByTimestamp() noexcept {
        size_t currentSize = size_.load(std::memory_order_acquire);
        if (currentSize <= 1) return;

        std::sort(events_.begin(), events_.begin() + currentSize,
                  [](const MIDIEvent& a, const MIDIEvent& b) {
                      if (a.sampleOffset != b.sampleOffset) {
                          return a.sampleOffset < b.sampleOffset;
                      }
                      return a.timestamp < b.timestamp;
                  });
    }

    // ==========================================================================
    // Swap (for double-buffering pattern)
    // ==========================================================================

    void swap(MIDIBuffer& other) noexcept {
        events_.swap(other.events_);
        std::swap(capacity_, other.capacity_);

        size_t thisSize = size_.load(std::memory_order_acquire);
        size_t otherSize = other.size_.load(std::memory_order_acquire);
        size_.store(otherSize, std::memory_order_release);
        other.size_.store(thisSize, std::memory_order_release);
    }

    // ==========================================================================
    // Copy events within a sample range (for buffer splitting)
    // ==========================================================================

    size_t copyEventsInRange(const MIDIBuffer& source, uint32_t startSample,
                             uint32_t endSample) noexcept {
        size_t copied = 0;
        for (const auto& event : source) {
            if (event.sampleOffset >= startSample &&
                event.sampleOffset < endSample) {
                if (addEvent(event)) {
                    ++copied;
                } else {
                    break;  // Buffer full
                }
            }
        }
        return copied;
    }

private:
    std::vector<MIDIEvent> events_;
    size_t capacity_;
    std::atomic<size_t> size_;
};

// =============================================================================
// Lock-Free MIDI Ring Buffer (SPSC)
// =============================================================================
// For passing MIDI events between threads without locks.
// Uses atomic index operations for thread-safe SPSC access.
// =============================================================================

class MIDIRingBuffer {
public:
    static constexpr size_t kDefaultCapacity = 8192;

    explicit MIDIRingBuffer(size_t capacity = kDefaultCapacity)
        : buffer_(capacity)
        , capacity_(capacity)
        , writeIndex_(0)
        , readIndex_(0)
    {
    }

    // Non-copyable
    MIDIRingBuffer(const MIDIRingBuffer&) = delete;
    MIDIRingBuffer& operator=(const MIDIRingBuffer&) = delete;

    // ==========================================================================
    // Producer Interface (non-RT or RT thread)
    // ==========================================================================

    bool push(const MIDIEvent& event) noexcept {
        const size_t currentWrite = writeIndex_.load(std::memory_order_relaxed);
        const size_t nextWrite = (currentWrite + 1) % capacity_;

        // Check if full (leave one slot empty to distinguish full from empty)
        if (nextWrite == readIndex_.load(std::memory_order_acquire)) {
            return false;
        }

        buffer_[currentWrite] = event;
        writeIndex_.store(nextWrite, std::memory_order_release);
        return true;
    }

    // ==========================================================================
    // Consumer Interface (RT audio thread)
    // ==========================================================================

    bool pop(MIDIEvent& outEvent) noexcept {
        const size_t currentRead = readIndex_.load(std::memory_order_relaxed);

        // Check if empty
        if (currentRead == writeIndex_.load(std::memory_order_acquire)) {
            return false;
        }

        outEvent = buffer_[currentRead];
        const size_t nextRead = (currentRead + 1) % capacity_;
        readIndex_.store(nextRead, std::memory_order_release);
        return true;
    }

    // Drain all events into a buffer
    size_t drainTo(MIDIBuffer& dest) noexcept {
        size_t count = 0;
        MIDIEvent event;
        while (pop(event)) {
            if (dest.addEvent(event)) {
                ++count;
            } else {
                // Destination full, try to push back
                push(event);
                break;
            }
        }
        return count;
    }

    // ==========================================================================
    // Status Queries (approximate, may race)
    // ==========================================================================

    bool isEmpty() const noexcept {
        return readIndex_.load(std::memory_order_acquire) ==
               writeIndex_.load(std::memory_order_acquire);
    }

    size_t size() const noexcept {
        const size_t write = writeIndex_.load(std::memory_order_acquire);
        const size_t read = readIndex_.load(std::memory_order_acquire);
        return (write >= read) ? (write - read) : (capacity_ - read + write);
    }

    size_t capacity() const noexcept { return capacity_; }

    size_t available() const noexcept {
        return capacity_ - size() - 1;  // -1 for empty slot
    }

private:
    std::vector<MIDIEvent> buffer_;
    size_t capacity_;
    std::atomic<size_t> writeIndex_;
    std::atomic<size_t> readIndex_;
};

}  // namespace penta::midi
