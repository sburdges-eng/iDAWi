#include "penta/osc/RTMessageQueue.h"

#include <algorithm>

namespace penta::osc {

RTMessageQueue::RTMessageQueue(size_t capacity)
    : buffer_(capacity)
    , capacity_(capacity)
    , writeIndex_(0)
    , readIndex_(0)
{
    // Pre-allocate buffer to avoid allocations during operation
    // Buffer is sized to capacity for simplicity (power of 2 would be more efficient
    // for modulo operations, but we use explicit comparison for clarity)
}

RTMessageQueue::~RTMessageQueue() = default;

bool RTMessageQueue::push(const OSCMessage& message) noexcept {
    // Load current indices
    const size_t currentWrite = writeIndex_.load(std::memory_order_relaxed);
    const size_t nextWrite = (currentWrite + 1) % capacity_;

    // Check if queue is full
    // We leave one slot empty to distinguish full from empty
    if (nextWrite == readIndex_.load(std::memory_order_acquire)) {
        return false;  // Queue is full
    }

    // Write the message
    buffer_[currentWrite] = message;

    // Update write index with release semantics to ensure
    // the message write is visible before the index update
    writeIndex_.store(nextWrite, std::memory_order_release);

    return true;
}

bool RTMessageQueue::pop(OSCMessage& outMessage) noexcept {
    // Load current read index
    const size_t currentRead = readIndex_.load(std::memory_order_relaxed);

    // Check if queue is empty
    if (currentRead == writeIndex_.load(std::memory_order_acquire)) {
        return false;  // Queue is empty
    }

    // Read the message
    outMessage = buffer_[currentRead];

    // Update read index with release semantics
    const size_t nextRead = (currentRead + 1) % capacity_;
    readIndex_.store(nextRead, std::memory_order_release);

    return true;
}

bool RTMessageQueue::isEmpty() const noexcept {
    return readIndex_.load(std::memory_order_acquire) ==
           writeIndex_.load(std::memory_order_acquire);
}

size_t RTMessageQueue::size() const noexcept {
    const size_t write = writeIndex_.load(std::memory_order_acquire);
    const size_t read = readIndex_.load(std::memory_order_acquire);

    if (write >= read) {
        return write - read;
    } else {
        return capacity_ - read + write;
    }
}

} // namespace penta::osc
