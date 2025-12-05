#include <gtest/gtest.h>
#include "penta/transport/Transport.h"
#include <thread>
#include <chrono>

using namespace penta::transport;

// =============================================================================
// Transport Basic Tests
// =============================================================================

class TransportTest : public ::testing::Test {
protected:
    std::unique_ptr<Transport> transport;

    void SetUp() override {
        TransportConfig config;
        config.sampleRate = 48000.0;
        config.initialTempo = 120.0;
        config.initialTimeSignature = TimeSignature{4, 4};
        transport = createTransport(config);
    }
};

TEST_F(TransportTest, InitialState) {
    EXPECT_TRUE(transport->isStopped());
    EXPECT_FALSE(transport->isPlaying());
    EXPECT_FALSE(transport->isPaused());
    EXPECT_FALSE(transport->isRecording());
    EXPECT_EQ(transport->getState(), TransportState::Stopped);
}

TEST_F(TransportTest, InitialPosition) {
    EXPECT_EQ(transport->getPosition(), 0u);
    EXPECT_DOUBLE_EQ(transport->getPositionSeconds(), 0.0);
    EXPECT_DOUBLE_EQ(transport->getPositionQuarterNotes(), 0.0);
}

TEST_F(TransportTest, InitialTempo) {
    EXPECT_DOUBLE_EQ(transport->getTempo(), 120.0);
}

TEST_F(TransportTest, InitialTimeSignature) {
    auto ts = transport->getTimeSignature();
    EXPECT_EQ(ts.numerator, 4);
    EXPECT_EQ(ts.denominator, 4);
}

// =============================================================================
// Transport Control Tests
// =============================================================================

TEST_F(TransportTest, PlayFromStopped) {
    EXPECT_TRUE(transport->play());
    EXPECT_TRUE(transport->isPlaying());
    EXPECT_EQ(transport->getState(), TransportState::Playing);
}

TEST_F(TransportTest, Pause) {
    transport->play();
    EXPECT_TRUE(transport->pause());
    EXPECT_TRUE(transport->isPaused());
    EXPECT_EQ(transport->getState(), TransportState::Paused);
}

TEST_F(TransportTest, StopFromPlaying) {
    transport->play();
    EXPECT_TRUE(transport->stop());
    EXPECT_TRUE(transport->isStopped());
    EXPECT_EQ(transport->getPosition(), 0u);  // Position reset
}

TEST_F(TransportTest, StopWithoutReset) {
    transport->setPosition(48000);  // 1 second at 48kHz
    transport->play();
    transport->stop(false);  // Don't reset position

    EXPECT_TRUE(transport->isStopped());
    EXPECT_EQ(transport->getPosition(), 48000u);  // Position preserved
}

TEST_F(TransportTest, TogglePlayPause) {
    EXPECT_TRUE(transport->togglePlayPause());  // Play
    EXPECT_TRUE(transport->isPlaying());

    EXPECT_TRUE(transport->togglePlayPause());  // Pause
    EXPECT_TRUE(transport->isPaused());

    EXPECT_TRUE(transport->togglePlayPause());  // Play again
    EXPECT_TRUE(transport->isPlaying());
}

TEST_F(TransportTest, Record) {
    EXPECT_TRUE(transport->record());
    EXPECT_TRUE(transport->isRecording());
    EXPECT_TRUE(transport->isPlaying());  // Recording implies playing
    EXPECT_EQ(transport->getState(), TransportState::Recording);
}

TEST_F(TransportTest, StopRecording) {
    transport->record();
    EXPECT_TRUE(transport->stopRecording());
    EXPECT_FALSE(transport->isRecording());
    EXPECT_TRUE(transport->isPlaying());  // Continues playing
}

// =============================================================================
// Position Tests
// =============================================================================

TEST_F(TransportTest, SetPositionSamples) {
    transport->setPosition(96000);  // 2 seconds at 48kHz
    EXPECT_EQ(transport->getPosition(), 96000u);
    EXPECT_DOUBLE_EQ(transport->getPositionSeconds(), 2.0);
}

TEST_F(TransportTest, SetPositionSeconds) {
    transport->setPositionSeconds(1.5);
    EXPECT_EQ(transport->getPosition(), 72000u);  // 1.5 * 48000
}

TEST_F(TransportTest, SetPositionQuarterNotes) {
    // At 120 BPM, 1 quarter note = 0.5 seconds = 24000 samples
    transport->setPositionQuarterNotes(4.0);  // 4 quarter notes
    EXPECT_EQ(transport->getPosition(), 96000u);  // 4 * 24000
}

TEST_F(TransportTest, SetPositionBarsBeats) {
    // At 120 BPM, 4/4, 1 bar = 4 quarter notes = 2 seconds
    transport->setPositionBarsBeats(2, 0);  // Bar 2, beat 0
    EXPECT_EQ(transport->getPosition(), 192000u);  // 2 bars = 4 seconds
}

TEST_F(TransportTest, MovePosition) {
    transport->setPosition(48000);
    transport->movePosition(24000);
    EXPECT_EQ(transport->getPosition(), 72000u);

    transport->movePosition(-12000);
    EXPECT_EQ(transport->getPosition(), 60000u);
}

TEST_F(TransportTest, MovePositionClampsToZero) {
    transport->setPosition(10000);
    transport->movePosition(-20000);  // Would go negative
    EXPECT_EQ(transport->getPosition(), 0u);
}

TEST_F(TransportTest, Rewind) {
    transport->setPosition(96000);
    transport->rewind();
    EXPECT_EQ(transport->getPosition(), 0u);
}

// =============================================================================
// Tempo Tests
// =============================================================================

TEST_F(TransportTest, SetTempo) {
    transport->setTempo(140.0);
    EXPECT_DOUBLE_EQ(transport->getTempo(), 140.0);
}

TEST_F(TransportTest, TempoClampedToMin) {
    transport->setTempo(10.0);  // Below minimum
    EXPECT_GE(transport->getTempo(), kMinTempo);
}

TEST_F(TransportTest, TempoClampedToMax) {
    transport->setTempo(1500.0);  // Above maximum
    EXPECT_LE(transport->getTempo(), kMaxTempo);
}

TEST_F(TransportTest, TempoAffectsPositionConversion) {
    // At 120 BPM
    transport->setPositionQuarterNotes(1.0);
    uint64_t pos120 = transport->getPosition();

    // At 60 BPM (half tempo = double time)
    transport->setTempo(60.0);
    transport->setPositionQuarterNotes(1.0);
    uint64_t pos60 = transport->getPosition();

    EXPECT_EQ(pos60, pos120 * 2);  // Same QN takes twice as many samples
}

// =============================================================================
// Time Signature Tests
// =============================================================================

TEST_F(TransportTest, SetTimeSignature) {
    transport->setTimeSignature(3, 4);
    auto ts = transport->getTimeSignature();
    EXPECT_EQ(ts.numerator, 3);
    EXPECT_EQ(ts.denominator, 4);
}

TEST_F(TransportTest, TimeSignatureStruct) {
    transport->setTimeSignature(TimeSignature{6, 8});
    auto ts = transport->getTimeSignature();
    EXPECT_EQ(ts.numerator, 6);
    EXPECT_EQ(ts.denominator, 8);
}

TEST_F(TransportTest, TimeSignatureBeatDuration) {
    TimeSignature ts44{4, 4};
    EXPECT_DOUBLE_EQ(ts44.getBeatDuration(), 1.0);  // Quarter note

    TimeSignature ts68{6, 8};
    EXPECT_DOUBLE_EQ(ts68.getBeatDuration(), 0.5);  // Eighth note

    TimeSignature ts34{3, 4};
    EXPECT_DOUBLE_EQ(ts34.getBarDurationInQuarterNotes(), 3.0);
}

// =============================================================================
// Loop Tests
// =============================================================================

TEST_F(TransportTest, LoopDisabledByDefault) {
    EXPECT_FALSE(transport->isLoopEnabled());
}

TEST_F(TransportTest, EnableLoop) {
    transport->setLoopEnabled(true);
    EXPECT_TRUE(transport->isLoopEnabled());
}

TEST_F(TransportTest, SetLoopPoints) {
    transport->setLoopPoints(48000, 96000);
    auto loop = transport->getLoopRegion();

    EXPECT_EQ(loop.startSample, 48000u);
    EXPECT_EQ(loop.endSample, 96000u);
    EXPECT_EQ(loop.length(), 48000u);
}

TEST_F(TransportTest, SetLoopPointsSeconds) {
    transport->setLoopPointsSeconds(1.0, 3.0);
    auto loop = transport->getLoopRegion();

    EXPECT_EQ(loop.startSample, 48000u);
    EXPECT_EQ(loop.endSample, 144000u);
}

TEST_F(TransportTest, SetLoopBars) {
    // 4/4 at 120 BPM: 1 bar = 4 QN = 2 seconds = 96000 samples
    transport->setLoopBars(0, 2);
    auto loop = transport->getLoopRegion();

    EXPECT_EQ(loop.startSample, 0u);
    EXPECT_EQ(loop.endSample, 192000u);  // 2 bars
}

TEST_F(TransportTest, InvalidLoopPointsIgnored) {
    transport->setLoopPoints(100, 50);  // End before start
    auto loop = transport->getLoopRegion();

    // Should be ignored (defaults/previous values)
    EXPECT_FALSE(loop.isValid() && loop.endSample < loop.startSample);
}

// =============================================================================
// Advance Tests (Audio Processing)
// =============================================================================

TEST_F(TransportTest, AdvanceWhileStopped) {
    bool wrapped = transport->advance(512);
    EXPECT_FALSE(wrapped);
    EXPECT_EQ(transport->getPosition(), 0u);  // No movement
}

TEST_F(TransportTest, AdvanceWhilePlaying) {
    transport->play();
    transport->advance(512);
    EXPECT_EQ(transport->getPosition(), 512u);
}

TEST_F(TransportTest, AdvanceMultipleBuffers) {
    transport->play();

    for (int i = 0; i < 10; ++i) {
        transport->advance(256);
    }

    EXPECT_EQ(transport->getPosition(), 2560u);
}

TEST_F(TransportTest, AdvanceWithLoop) {
    transport->setLoopPoints(0, 1000);
    transport->setLoopEnabled(true);
    transport->play();

    // Position at 900, advance by 200 should wrap to 100
    transport->setPosition(900);
    bool wrapped = transport->advance(200);

    EXPECT_TRUE(wrapped);
    EXPECT_LT(transport->getPosition(), 1000u);
}

TEST_F(TransportTest, LoopRegionContains) {
    LoopRegion loop;
    loop.startSample = 1000;
    loop.endSample = 2000;
    loop.enabled = true;

    EXPECT_FALSE(loop.contains(999));
    EXPECT_TRUE(loop.contains(1000));
    EXPECT_TRUE(loop.contains(1500));
    EXPECT_TRUE(loop.contains(1999));
    EXPECT_FALSE(loop.contains(2000));
}

// =============================================================================
// Conversion Tests
// =============================================================================

TEST_F(TransportTest, SecondsToSamples) {
    EXPECT_EQ(transport->secondsToSamples(1.0), 48000u);
    EXPECT_EQ(transport->secondsToSamples(2.5), 120000u);
}

TEST_F(TransportTest, SamplesToSeconds) {
    EXPECT_DOUBLE_EQ(transport->samplesToSeconds(48000), 1.0);
    EXPECT_DOUBLE_EQ(transport->samplesToSeconds(120000), 2.5);
}

TEST_F(TransportTest, QuarterNotesToSamples) {
    // At 120 BPM: 1 QN = 0.5 seconds = 24000 samples
    EXPECT_EQ(transport->quarterNotesToSamples(1.0), 24000u);
    EXPECT_EQ(transport->quarterNotesToSamples(4.0), 96000u);
}

TEST_F(TransportTest, SamplesToQuarterNotes) {
    EXPECT_DOUBLE_EQ(transport->samplesToQuarterNotes(24000), 1.0);
    EXPECT_DOUBLE_EQ(transport->samplesToQuarterNotes(96000), 4.0);
}

TEST_F(TransportTest, BarsBeatsConversion) {
    // 4/4 at 120 BPM
    uint32_t bars;
    double beats;

    transport->samplesToBarsBeats(0, bars, beats);
    EXPECT_EQ(bars, 0u);
    EXPECT_DOUBLE_EQ(beats, 0.0);

    transport->samplesToBarsBeats(96000, bars, beats);  // 2 seconds = 1 bar
    EXPECT_EQ(bars, 1u);
    EXPECT_NEAR(beats, 0.0, 0.001);

    transport->samplesToBarsBeats(144000, bars, beats);  // 3 seconds = 1.5 bars
    EXPECT_EQ(bars, 1u);
    EXPECT_NEAR(beats, 2.0, 0.001);  // 2 beats into bar 2
}

// =============================================================================
// Sample Rate Tests
// =============================================================================

TEST_F(TransportTest, SetSampleRate) {
    transport->setSampleRate(96000.0);
    EXPECT_DOUBLE_EQ(transport->getSampleRate(), 96000.0);
}

TEST_F(TransportTest, SampleRateAffectsConversion) {
    transport->setSampleRate(96000.0);
    // Now 1 second = 96000 samples
    EXPECT_EQ(transport->secondsToSamples(1.0), 96000u);
}

// =============================================================================
// PPQ Tests
// =============================================================================

TEST_F(TransportTest, DefaultPPQ) {
    EXPECT_EQ(transport->getPPQ(), kDefaultPPQ);  // 960
}

TEST_F(TransportTest, SetPPQ) {
    transport->setPPQ(480);
    EXPECT_EQ(transport->getPPQ(), 480u);
}

// =============================================================================
// TransportPosition Tests
// =============================================================================

TEST_F(TransportTest, TransportPositionUpdated) {
    transport->setPosition(48000);  // 1 second

    auto pos = transport->getTransportPosition();

    EXPECT_EQ(pos.samples, 48000u);
    EXPECT_DOUBLE_EQ(pos.seconds, 1.0);
    EXPECT_DOUBLE_EQ(pos.quarterNotes, 2.0);  // 120 BPM, 1 sec = 2 QN
    EXPECT_DOUBLE_EQ(pos.tempo, 120.0);
}

// =============================================================================
// Callback Tests
// =============================================================================

TEST_F(TransportTest, StateCallback) {
    TransportState receivedState = TransportState::Stopped;
    int callCount = 0;

    transport->setStateCallback([&](TransportState state) {
        receivedState = state;
        ++callCount;
    });

    transport->play();
    EXPECT_EQ(receivedState, TransportState::Playing);

    transport->pause();
    EXPECT_EQ(receivedState, TransportState::Paused);

    transport->stop();
    EXPECT_EQ(receivedState, TransportState::Stopped);

    EXPECT_EQ(callCount, 3);
}

TEST_F(TransportTest, TempoCallback) {
    double receivedTempo = 0.0;

    transport->setTempoCallback([&](double tempo) {
        receivedTempo = tempo;
    });

    transport->setTempo(140.0);
    EXPECT_DOUBLE_EQ(receivedTempo, 140.0);
}

TEST_F(TransportTest, TimeSignatureCallback) {
    TimeSignature receivedTS;

    transport->setTimeSignatureCallback([&](const TimeSignature& ts) {
        receivedTS = ts;
    });

    transport->setTimeSignature(6, 8);
    EXPECT_EQ(receivedTS.numerator, 6);
    EXPECT_EQ(receivedTS.denominator, 8);
}

TEST_F(TransportTest, LoopCallback) {
    LoopRegion receivedLoop;

    transport->setLoopCallback([&](const LoopRegion& loop) {
        receivedLoop = loop;
    });

    transport->setLoopPoints(1000, 5000);
    EXPECT_EQ(receivedLoop.startSample, 1000u);
    EXPECT_EQ(receivedLoop.endSample, 5000u);
}

// =============================================================================
// Thread Safety Tests
// =============================================================================

TEST_F(TransportTest, ConcurrentStateChanges) {
    std::atomic<bool> running{true};

    // Thread 1: Play/Stop
    std::thread t1([&]() {
        while (running) {
            transport->play();
            transport->stop();
        }
    });

    // Thread 2: Position changes
    std::thread t2([&]() {
        while (running) {
            transport->setPosition(48000);
            transport->rewind();
        }
    });

    // Thread 3: Tempo changes
    std::thread t3([&]() {
        while (running) {
            transport->setTempo(120.0);
            transport->setTempo(140.0);
        }
    });

    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    running = false;

    t1.join();
    t2.join();
    t3.join();

    // Should not crash or deadlock
    SUCCEED();
}
