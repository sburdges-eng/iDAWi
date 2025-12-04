#include <gtest/gtest.h>
#include "penta/midi/MIDIBuffer.h"
#include <thread>
#include <atomic>

using namespace penta::midi;

// =============================================================================
// MIDIBuffer Tests
// =============================================================================

class MIDIBufferTest : public ::testing::Test {
protected:
    MIDIBuffer buffer{256};

    void SetUp() override {
        buffer.clear();
    }
};

TEST_F(MIDIBufferTest, InitialState) {
    EXPECT_TRUE(buffer.isEmpty());
    EXPECT_EQ(buffer.size(), 0u);
    EXPECT_EQ(buffer.capacity(), 256u);
    EXPECT_FALSE(buffer.isFull());
}

TEST_F(MIDIBufferTest, AddEvent) {
    auto event = MIDIEvent::noteOn(0, 60, 100);
    EXPECT_TRUE(buffer.addEvent(event));

    EXPECT_FALSE(buffer.isEmpty());
    EXPECT_EQ(buffer.size(), 1u);
}

TEST_F(MIDIBufferTest, AddConvenienceMethods) {
    EXPECT_TRUE(buffer.addNoteOn(0, 60, 100, 0));
    EXPECT_TRUE(buffer.addNoteOff(0, 60, 0, 128));
    EXPECT_TRUE(buffer.addControlChange(0, 1, 64, 256));
    EXPECT_TRUE(buffer.addPitchBend(0, 4096, 384));
    EXPECT_TRUE(buffer.addProgramChange(0, 42, 512));

    EXPECT_EQ(buffer.size(), 5u);
}

TEST_F(MIDIBufferTest, BufferFull) {
    MIDIBuffer smallBuffer{4};

    for (size_t i = 0; i < 4; ++i) {
        EXPECT_TRUE(smallBuffer.addNoteOn(0, static_cast<uint8_t>(i), 100));
    }

    EXPECT_TRUE(smallBuffer.isFull());
    EXPECT_FALSE(smallBuffer.addNoteOn(0, 60, 100));  // Should fail
}

TEST_F(MIDIBufferTest, Clear) {
    buffer.addNoteOn(0, 60, 100);
    buffer.addNoteOn(0, 64, 100);
    buffer.addNoteOn(0, 67, 100);

    EXPECT_EQ(buffer.size(), 3u);

    buffer.clear();
    EXPECT_TRUE(buffer.isEmpty());
    EXPECT_EQ(buffer.size(), 0u);
}

TEST_F(MIDIBufferTest, IndexAccess) {
    buffer.addNoteOn(0, 60, 100, 0);
    buffer.addNoteOn(0, 64, 90, 128);
    buffer.addNoteOn(0, 67, 80, 256);

    EXPECT_EQ(buffer[0].getNote(), 60);
    EXPECT_EQ(buffer[1].getNote(), 64);
    EXPECT_EQ(buffer[2].getNote(), 67);

    EXPECT_EQ(buffer[0].sampleOffset, 0u);
    EXPECT_EQ(buffer[1].sampleOffset, 128u);
    EXPECT_EQ(buffer[2].sampleOffset, 256u);
}

TEST_F(MIDIBufferTest, Iterator) {
    buffer.addNoteOn(0, 60, 100);
    buffer.addNoteOn(0, 64, 90);
    buffer.addNoteOn(0, 67, 80);

    std::vector<uint8_t> notes;
    for (const auto& event : buffer) {
        notes.push_back(event.getNote());
    }

    EXPECT_EQ(notes.size(), 3u);
    EXPECT_EQ(notes[0], 60);
    EXPECT_EQ(notes[1], 64);
    EXPECT_EQ(notes[2], 67);
}

TEST_F(MIDIBufferTest, SortByTimestamp) {
    // Add events out of order
    buffer.addNoteOn(0, 67, 80, 256);
    buffer.addNoteOn(0, 60, 100, 0);
    buffer.addNoteOn(0, 64, 90, 128);

    buffer.sortByTimestamp();

    EXPECT_EQ(buffer[0].sampleOffset, 0u);
    EXPECT_EQ(buffer[1].sampleOffset, 128u);
    EXPECT_EQ(buffer[2].sampleOffset, 256u);
}

TEST_F(MIDIBufferTest, CopyEventsInRange) {
    buffer.addNoteOn(0, 60, 100, 0);
    buffer.addNoteOn(0, 64, 90, 128);
    buffer.addNoteOn(0, 67, 80, 256);
    buffer.addNoteOn(0, 72, 70, 384);

    MIDIBuffer dest{256};
    size_t copied = dest.copyEventsInRange(buffer, 100, 300);

    EXPECT_EQ(copied, 2u);  // Events at 128 and 256
    EXPECT_EQ(dest[0].sampleOffset, 128u);
    EXPECT_EQ(dest[1].sampleOffset, 256u);
}

TEST_F(MIDIBufferTest, Swap) {
    buffer.addNoteOn(0, 60, 100);

    MIDIBuffer other{256};
    other.addNoteOn(1, 72, 80);
    other.addNoteOn(1, 76, 80);

    buffer.swap(other);

    EXPECT_EQ(buffer.size(), 2u);
    EXPECT_EQ(other.size(), 1u);
    EXPECT_EQ(buffer[0].channel, 1);
    EXPECT_EQ(other[0].channel, 0);
}

// =============================================================================
// MIDIRingBuffer Tests
// =============================================================================

class MIDIRingBufferTest : public ::testing::Test {
protected:
    MIDIRingBuffer ring{256};
};

TEST_F(MIDIRingBufferTest, InitialState) {
    EXPECT_TRUE(ring.isEmpty());
    EXPECT_EQ(ring.size(), 0u);
    EXPECT_EQ(ring.capacity(), 256u);
    EXPECT_GT(ring.available(), 0u);
}

TEST_F(MIDIRingBufferTest, PushPop) {
    auto event = MIDIEvent::noteOn(0, 60, 100);
    EXPECT_TRUE(ring.push(event));

    EXPECT_FALSE(ring.isEmpty());
    EXPECT_EQ(ring.size(), 1u);

    MIDIEvent outEvent;
    EXPECT_TRUE(ring.pop(outEvent));

    EXPECT_EQ(outEvent.getNote(), 60);
    EXPECT_TRUE(ring.isEmpty());
}

TEST_F(MIDIRingBufferTest, FIFO) {
    ring.push(MIDIEvent::noteOn(0, 60, 100));
    ring.push(MIDIEvent::noteOn(0, 64, 100));
    ring.push(MIDIEvent::noteOn(0, 67, 100));

    MIDIEvent event;
    ring.pop(event);
    EXPECT_EQ(event.getNote(), 60);

    ring.pop(event);
    EXPECT_EQ(event.getNote(), 64);

    ring.pop(event);
    EXPECT_EQ(event.getNote(), 67);
}

TEST_F(MIDIRingBufferTest, PopFromEmpty) {
    MIDIEvent event;
    EXPECT_FALSE(ring.pop(event));
}

TEST_F(MIDIRingBufferTest, WrapAround) {
    MIDIRingBuffer smallRing{4};

    // Fill and empty multiple times to test wrap-around
    for (int iteration = 0; iteration < 3; ++iteration) {
        for (int i = 0; i < 3; ++i) {  // Leave one slot empty
            EXPECT_TRUE(smallRing.push(MIDIEvent::noteOn(0, static_cast<uint8_t>(i), 100)));
        }

        MIDIEvent event;
        for (int i = 0; i < 3; ++i) {
            EXPECT_TRUE(smallRing.pop(event));
            EXPECT_EQ(event.getNote(), i);
        }
    }
}

TEST_F(MIDIRingBufferTest, DrainTo) {
    ring.push(MIDIEvent::noteOn(0, 60, 100));
    ring.push(MIDIEvent::noteOn(0, 64, 90));
    ring.push(MIDIEvent::noteOn(0, 67, 80));

    MIDIBuffer dest{256};
    size_t drained = ring.drainTo(dest);

    EXPECT_EQ(drained, 3u);
    EXPECT_TRUE(ring.isEmpty());
    EXPECT_EQ(dest.size(), 3u);
}

TEST_F(MIDIRingBufferTest, ThreadSafety) {
    MIDIRingBuffer sharedRing{1024};
    std::atomic<size_t> produced{0};
    std::atomic<size_t> consumed{0};
    const size_t numEvents = 10000;

    // Producer thread
    std::thread producer([&]() {
        for (size_t i = 0; i < numEvents; ++i) {
            while (!sharedRing.push(MIDIEvent::noteOn(0, static_cast<uint8_t>(i % 128), 100))) {
                std::this_thread::yield();
            }
            ++produced;
        }
    });

    // Consumer thread
    std::thread consumer([&]() {
        MIDIEvent event;
        while (consumed < numEvents) {
            if (sharedRing.pop(event)) {
                ++consumed;
            } else {
                std::this_thread::yield();
            }
        }
    });

    producer.join();
    consumer.join();

    EXPECT_EQ(produced.load(), numEvents);
    EXPECT_EQ(consumed.load(), numEvents);
    EXPECT_TRUE(sharedRing.isEmpty());
}
