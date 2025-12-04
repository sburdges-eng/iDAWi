#include <gtest/gtest.h>
#include "penta/midi/MIDITypes.h"

using namespace penta::midi;

// =============================================================================
// MIDIEvent Tests
// =============================================================================

class MIDIEventTest : public ::testing::Test {
protected:
    void SetUp() override {}
};

TEST_F(MIDIEventTest, DefaultConstructor) {
    MIDIEvent event;
    EXPECT_EQ(event.timestamp, 0u);
    EXPECT_EQ(event.sampleOffset, 0u);
    EXPECT_EQ(event.status, 0);
    EXPECT_EQ(event.data1, 0);
    EXPECT_EQ(event.data2, 0);
    EXPECT_EQ(event.channel, 0);
}

TEST_F(MIDIEventTest, NoteOnFactory) {
    auto event = MIDIEvent::noteOn(5, 60, 100, 128);

    EXPECT_EQ(event.sampleOffset, 128u);
    EXPECT_EQ(event.channel, 5);
    EXPECT_EQ(event.getType(), MIDIEventType::NoteOn);
    EXPECT_EQ(event.getNote(), 60);
    EXPECT_EQ(event.getVelocity(), 100);
    EXPECT_TRUE(event.isNoteOn());
    EXPECT_FALSE(event.isNoteOff());
}

TEST_F(MIDIEventTest, NoteOffFactory) {
    auto event = MIDIEvent::noteOff(3, 72, 64);

    EXPECT_EQ(event.channel, 3);
    EXPECT_EQ(event.getType(), MIDIEventType::NoteOff);
    EXPECT_EQ(event.getNote(), 72);
    EXPECT_TRUE(event.isNoteOff());
    EXPECT_FALSE(event.isNoteOn());
}

TEST_F(MIDIEventTest, NoteOnWithZeroVelocityIsNoteOff) {
    auto event = MIDIEvent::noteOn(0, 60, 0);

    EXPECT_EQ(event.getType(), MIDIEventType::NoteOn);
    EXPECT_TRUE(event.isNoteOff());  // Velocity 0 = note off
    EXPECT_FALSE(event.isNoteOn());
}

TEST_F(MIDIEventTest, ControlChangeFactory) {
    auto event = MIDIEvent::controlChange(1, CC::ModulationWheel, 127);

    EXPECT_EQ(event.channel, 1);
    EXPECT_EQ(event.getType(), MIDIEventType::ControlChange);
    EXPECT_TRUE(event.isControlChange());
    EXPECT_EQ(event.getController(), CC::ModulationWheel);
    EXPECT_EQ(event.getControlValue(), 127);
}

TEST_F(MIDIEventTest, PitchBendFactory) {
    // Center position (0)
    auto center = MIDIEvent::pitchBend(0, 0);
    EXPECT_TRUE(center.isPitchBend());
    EXPECT_EQ(center.getPitchBend(), 0);

    // Max positive
    auto maxPos = MIDIEvent::pitchBend(0, 8191);
    EXPECT_EQ(maxPos.getPitchBend(), 8191);

    // Max negative
    auto maxNeg = MIDIEvent::pitchBend(0, -8192);
    EXPECT_EQ(maxNeg.getPitchBend(), -8192);
}

TEST_F(MIDIEventTest, ProgramChangeFactory) {
    auto event = MIDIEvent::programChange(9, 42);

    EXPECT_EQ(event.channel, 9);
    EXPECT_EQ(event.getType(), MIDIEventType::ProgramChange);
    EXPECT_EQ(event.data1, 42);
}

TEST_F(MIDIEventTest, ClockMessages) {
    auto clock = MIDIEvent::timingClock(256);
    EXPECT_EQ(clock.getType(), MIDIEventType::TimingClock);
    EXPECT_EQ(clock.sampleOffset, 256u);

    auto start = MIDIEvent::start();
    EXPECT_EQ(start.getType(), MIDIEventType::Start);

    auto stop = MIDIEvent::stop();
    EXPECT_EQ(stop.getType(), MIDIEventType::Stop);

    auto cont = MIDIEvent::continuePlay();
    EXPECT_EQ(cont.getType(), MIDIEventType::Continue);
}

TEST_F(MIDIEventTest, ChannelMasking) {
    // Channel should be masked to 0-15
    auto event = MIDIEvent::noteOn(255, 60, 100);
    EXPECT_EQ(event.channel, 15);  // 255 & 0x0F = 15
}

TEST_F(MIDIEventTest, DataByteMasking) {
    // Data bytes should be masked to 0-127
    auto event = MIDIEvent::noteOn(0, 200, 200);
    EXPECT_EQ(event.getNote(), 200 & 0x7F);
    EXPECT_EQ(event.getVelocity(), 200 & 0x7F);
}

// =============================================================================
// MIDIChannelState Tests
// =============================================================================

class MIDIChannelStateTest : public ::testing::Test {
protected:
    MIDIChannelState state;

    void SetUp() override {
        state.reset();
    }
};

TEST_F(MIDIChannelStateTest, DefaultState) {
    EXPECT_EQ(state.activeNoteCount, 0);
    EXPECT_EQ(state.pitchBend, 0);
    EXPECT_EQ(state.channelPressure, 0);
    EXPECT_EQ(state.programNumber, 0);

    // Default CC values
    EXPECT_EQ(state.ccValues[CC::Volume], 100);
    EXPECT_EQ(state.ccValues[CC::Pan], 64);
    EXPECT_EQ(state.ccValues[CC::Expression], 127);
}

TEST_F(MIDIChannelStateTest, ProcessNoteOn) {
    auto noteOn = MIDIEvent::noteOn(0, 60, 100);
    state.processEvent(noteOn);

    EXPECT_EQ(state.noteVelocities[60], 100);
    EXPECT_EQ(state.activeNoteCount, 1);
}

TEST_F(MIDIChannelStateTest, ProcessNoteOff) {
    // First turn on
    state.processEvent(MIDIEvent::noteOn(0, 60, 100));
    EXPECT_EQ(state.activeNoteCount, 1);

    // Then turn off
    state.processEvent(MIDIEvent::noteOff(0, 60));
    EXPECT_EQ(state.noteVelocities[60], 0);
    EXPECT_EQ(state.activeNoteCount, 0);
}

TEST_F(MIDIChannelStateTest, ProcessNoteOnZeroVelocity) {
    state.processEvent(MIDIEvent::noteOn(0, 60, 100));
    EXPECT_EQ(state.activeNoteCount, 1);

    // Note on with velocity 0 should turn off
    state.processEvent(MIDIEvent::noteOn(0, 60, 0));
    EXPECT_EQ(state.noteVelocities[60], 0);
    EXPECT_EQ(state.activeNoteCount, 0);
}

TEST_F(MIDIChannelStateTest, ProcessControlChange) {
    state.processEvent(MIDIEvent::controlChange(0, CC::ModulationWheel, 64));
    EXPECT_EQ(state.ccValues[CC::ModulationWheel], 64);
}

TEST_F(MIDIChannelStateTest, ProcessPitchBend) {
    auto pb = MIDIEvent::pitchBend(0, 4096);
    state.processEvent(pb);
    EXPECT_EQ(state.pitchBend, 4096);
}

TEST_F(MIDIChannelStateTest, ProcessAllNotesOff) {
    // Add some notes
    state.processEvent(MIDIEvent::noteOn(0, 60, 100));
    state.processEvent(MIDIEvent::noteOn(0, 64, 100));
    state.processEvent(MIDIEvent::noteOn(0, 67, 100));
    EXPECT_EQ(state.activeNoteCount, 3);

    // All notes off
    state.processEvent(MIDIEvent::controlChange(0, CC::AllNotesOff, 0));
    EXPECT_EQ(state.activeNoteCount, 0);
    EXPECT_EQ(state.noteVelocities[60], 0);
    EXPECT_EQ(state.noteVelocities[64], 0);
    EXPECT_EQ(state.noteVelocities[67], 0);
}

// =============================================================================
// MIDIState Tests (Full 16-channel state)
// =============================================================================

class MIDIStateTest : public ::testing::Test {
protected:
    MIDIState state;

    void SetUp() override {
        state.reset();
    }
};

TEST_F(MIDIStateTest, MultiChannelNotes) {
    state.processEvent(MIDIEvent::noteOn(0, 60, 100));
    state.processEvent(MIDIEvent::noteOn(1, 64, 90));
    state.processEvent(MIDIEvent::noteOn(2, 67, 80));

    EXPECT_EQ(state[0].activeNoteCount, 1);
    EXPECT_EQ(state[1].activeNoteCount, 1);
    EXPECT_EQ(state[2].activeNoteCount, 1);
    EXPECT_EQ(state[0].noteVelocities[60], 100);
    EXPECT_EQ(state[1].noteVelocities[64], 90);
    EXPECT_EQ(state[2].noteVelocities[67], 80);
}

TEST_F(MIDIStateTest, SystemMessages) {
    EXPECT_FALSE(state.isPlaying);
    EXPECT_EQ(state.clockCount, 0u);

    state.processEvent(MIDIEvent::start());
    EXPECT_TRUE(state.isPlaying);

    state.processEvent(MIDIEvent::timingClock());
    state.processEvent(MIDIEvent::timingClock());
    state.processEvent(MIDIEvent::timingClock());
    EXPECT_EQ(state.clockCount, 3u);

    state.processEvent(MIDIEvent::stop());
    EXPECT_FALSE(state.isPlaying);
}

TEST_F(MIDIStateTest, ContinueResumesPlay) {
    state.processEvent(MIDIEvent::start());
    EXPECT_TRUE(state.isPlaying);

    state.processEvent(MIDIEvent::stop());
    EXPECT_FALSE(state.isPlaying);

    state.processEvent(MIDIEvent::continuePlay());
    EXPECT_TRUE(state.isPlaying);
}

TEST_F(MIDIStateTest, IndexOperatorChannelMask) {
    // Channel index should be masked to 0-15
    state[255].ccValues[CC::Volume] = 50;
    EXPECT_EQ(state[15].ccValues[CC::Volume], 50);  // 255 & 0x0F = 15
}
