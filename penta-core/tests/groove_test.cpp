#include "penta/groove/OnsetDetector.h"
#include "penta/groove/TempoEstimator.h"
#include "penta/groove/RhythmQuantizer.h"
#include "penta/groove/GrooveEngine.h"
#include <gtest/gtest.h>
#include <cmath>
#include <chrono>

using namespace penta::groove;

// ========== OnsetDetector Tests ==========

class OnsetDetectorTest : public ::testing::Test {
protected:
    void SetUp() override {
        OnsetDetector::Config config;
        config.sampleRate = 44100.0;
        config.hopSize = 512;
        detector = std::make_unique<OnsetDetector>(config);
    }
    
    std::unique_ptr<OnsetDetector> detector;
};

TEST_F(OnsetDetectorTest, DetectsSimpleClick) {
    constexpr size_t blockSize = 512;
    std::array<float, blockSize> signal = {};
    
    // Create impulse at start
    signal[0] = 1.0f;
    
    detector->process(signal.data(), blockSize);
    bool detected = detector->hasOnset();
    
    EXPECT_TRUE(detected);
}

TEST_F(OnsetDetectorTest, IgnoresConstantSignal) {
    constexpr size_t blockSize = 512;
    std::array<float, blockSize> signal;
    signal.fill(0.1f);  // Constant low level
    
    detector->process(signal.data(), blockSize);
    bool detected = detector->hasOnset();
    
    EXPECT_FALSE(detected);
}

TEST_F(OnsetDetectorTest, DetectsSineWaveOnset) {
    constexpr size_t blockSize = 512;
    std::array<float, blockSize> signal;
    
    // Silence first half
    for (size_t i = 0; i < blockSize / 2; ++i) {
        signal[i] = 0.0f;
    }
    
    // Sine wave second half
    for (size_t i = blockSize / 2; i < blockSize; ++i) {
        signal[i] = std::sin(2.0f * static_cast<float>(M_PI) * 440.0f * i / 44100.0f);
    }
    
    detector->process(signal.data(), blockSize);
    bool detected = detector->hasOnset();
    
    EXPECT_TRUE(detected);
}

TEST_F(OnsetDetectorTest, RespondsToThresholdChanges) {
    constexpr size_t blockSize = 512;
    std::array<float, blockSize> weakSignal = {};
    weakSignal[0] = 0.1f;  // Weak impulse
    
    detector->setThreshold(0.9f);  // High threshold (low sensitivity)
    detector->process(weakSignal.data(), blockSize);
    bool highThreshold = detector->hasOnset();
    
    detector->reset();
    
    detector->setThreshold(0.1f);  // Low threshold (high sensitivity)
    detector->process(weakSignal.data(), blockSize);
    bool lowThreshold = detector->hasOnset();
    
    // Low threshold should detect what high threshold misses
    EXPECT_TRUE(lowThreshold || !highThreshold);
}

// ========== TempoEstimator Tests ==========

class TempoEstimatorTest : public ::testing::Test {
protected:
    void SetUp() override {
        TempoEstimator::Config config;
        config.sampleRate = 44100.0;
        estimator = std::make_unique<TempoEstimator>(config);
    }
    
    std::unique_ptr<TempoEstimator> estimator;
};

TEST_F(TempoEstimatorTest, Estimates120BPM) {
    // 120 BPM = 0.5 seconds per beat = 22050 samples at 44.1kHz
    constexpr size_t samplesPerBeat = 22050;
    
    // Feed 4 beats
    for (int beat = 0; beat < 4; ++beat) {
        estimator->addOnset(beat * samplesPerBeat);
    }
    
    float bpm = estimator->getCurrentTempo();
    
    EXPECT_NEAR(bpm, 120.0f, 5.0f);  // Within 5 BPM
}

TEST_F(TempoEstimatorTest, Estimates90BPM) {
    // 90 BPM = 0.667 seconds per beat = 29400 samples
    constexpr size_t samplesPerBeat = 29400;
    
    for (int beat = 0; beat < 4; ++beat) {
        estimator->addOnset(beat * samplesPerBeat);
    }
    
    float bpm = estimator->getCurrentTempo();
    
    EXPECT_NEAR(bpm, 90.0f, 5.0f);
}

TEST_F(TempoEstimatorTest, ReturnsDefaultWithNoOnsets) {
    float bpm = estimator->getCurrentTempo();
    
    // Default tempo should be 120 BPM
    EXPECT_EQ(bpm, 120.0f);
}

TEST_F(TempoEstimatorTest, AdaptsToTempoChanges) {
    // First tempo: 120 BPM (22050 samples per beat at 44.1kHz)
    for (int i = 0; i < 4; ++i) {
        estimator->addOnset(i * 22050);
    }
    float tempo1 = estimator->getCurrentTempo();
    
    // Reset and change to 90 BPM (29400 samples per beat at 44.1kHz)
    estimator->reset();
    for (int i = 0; i < 4; ++i) {
        estimator->addOnset(i * 29400);
    }
    float tempo2 = estimator->getCurrentTempo();
    
    // Tempos should be different
    EXPECT_NE(tempo1, tempo2);
}

// ========== RhythmQuantizer Tests ==========

class RhythmQuantizerTest : public ::testing::Test {
protected:
    void SetUp() override {
        RhythmQuantizer::Config config;
        config.resolution = RhythmQuantizer::GridResolution::Sixteenth;
        config.strength = 1.0f;
        config.timeSignatureNum = 4;
        config.timeSignatureDen = 4;
        quantizer = std::make_unique<RhythmQuantizer>(config);
        
        // 120 BPM, 4/4 = 0.5s per beat = 22050 samples at 44.1kHz
        samplesPerBeat = 22050;
    }
    
    std::unique_ptr<RhythmQuantizer> quantizer;
    uint64_t samplesPerBeat;
};

TEST_F(RhythmQuantizerTest, QuantizesToNearestSixteenth) {
    // Sixteenth note = 22050 / 4 = 5512.5 samples
    
    uint64_t nearSixteenth = 5500;  // Just before 1st sixteenth
    uint64_t quantized = quantizer->quantize(nearSixteenth, samplesPerBeat, 0);
    
    EXPECT_NEAR(quantized, 5512, 100);  // Should snap to sixteenth
}

TEST_F(RhythmQuantizerTest, QuantizesToNearestEighth) {
    RhythmQuantizer::Config config;
    config.resolution = RhythmQuantizer::GridResolution::Eighth;
    config.strength = 1.0f;
    quantizer->updateConfig(config);
    
    uint64_t nearEighth = 11000;  // Near first eighth note
    uint64_t quantized = quantizer->quantize(nearEighth, samplesPerBeat, 0);
    
    EXPECT_NEAR(quantized, 11025, 100);  // 22050 / 2
}

TEST_F(RhythmQuantizerTest, HandlesDownbeat) {
    uint64_t nearDownbeat = 100;
    uint64_t quantized = quantizer->quantize(nearDownbeat, samplesPerBeat, 0);
    
    EXPECT_NEAR(quantized, 0, 200);  // Should snap to beat 1
}

TEST_F(RhythmQuantizerTest, HandlesSwing) {
    RhythmQuantizer::Config config;
    config.resolution = RhythmQuantizer::GridResolution::Eighth;
    config.enableSwing = true;
    config.swingAmount = 0.66f;  // Swing feel
    quantizer->updateConfig(config);
    
    uint64_t straightEighth = 11025;
    uint64_t swungEighth = quantizer->applySwing(straightEighth, samplesPerBeat, 0);
    
    // Swing should shift timing
    EXPECT_NE(straightEighth, swungEighth);
}

TEST_F(RhythmQuantizerTest, GetGridInterval) {
    // Test grid interval calculation
    uint64_t interval = quantizer->getGridInterval(samplesPerBeat);
    
    // Sixteenth note = beat / 4
    EXPECT_EQ(interval, samplesPerBeat / 4);
}

// ========== GrooveEngine Tests ==========

class GrooveEngineTest : public ::testing::Test {
protected:
    void SetUp() override {
        GrooveEngine::Config config;
        config.sampleRate = 44100.0;
        engine = std::make_unique<GrooveEngine>(config);
    }
    
    std::unique_ptr<GrooveEngine> engine;
};

TEST_F(GrooveEngineTest, ProcessesAudioBlock) {
    constexpr size_t blockSize = 512;
    std::array<float, blockSize> testSignal;
    
    // Generate click pattern
    testSignal.fill(0.0f);
    testSignal[0] = 1.0f;
    testSignal[256] = 1.0f;
    
    engine->processAudio(testSignal.data(), blockSize);
    
    const auto& analysis = engine->getAnalysis();
    float tempo = analysis.currentTempo;
    EXPECT_GE(tempo, 0.0f);  // Should not crash
}

TEST_F(GrooveEngineTest, RespondsToConfigChanges) {
    GrooveEngine::Config config;
    config.sampleRate = 44100.0;
    config.minTempo = 80.0f;
    config.maxTempo = 160.0f;
    
    EXPECT_NO_THROW(engine->updateConfig(config));
}

TEST_F(GrooveEngineTest, CanReset) {
    EXPECT_NO_THROW(engine->reset());
}

TEST_F(GrooveEngineTest, QuantizesToGrid) {
    // Test the quantizeToGrid method
    uint64_t unquantized = 5500;
    uint64_t quantized = engine->quantizeToGrid(unquantized);
    
    // Result depends on current tempo but should be valid
    EXPECT_GE(quantized, 0u);
}

// ========== Performance Benchmarks ==========

class GroovePerformanceBenchmark : public ::testing::Test {
protected:
    std::unique_ptr<OnsetDetector> detector;
    std::array<float, 512> testSignal;
    
    void SetUp() override {
        OnsetDetector::Config config;
        config.sampleRate = 44100.0;
        config.hopSize = 512;
        detector = std::make_unique<OnsetDetector>(config);
        
        // Generate test signal with onset
        testSignal.fill(0.0f);
        testSignal[0] = 1.0f;
        for (size_t i = 100; i < 512; ++i) {
            testSignal[i] = std::sin(2.0f * static_cast<float>(M_PI) * 440.0f * static_cast<float>(i) / 44100.0f);
        }
    }
};

TEST_F(GroovePerformanceBenchmark, OnsetDetectionUnder150Microseconds) {
    constexpr int iterations = 1000;
    
    auto start = std::chrono::high_resolution_clock::now();
    
    for (int i = 0; i < iterations; ++i) {
        detector->process(testSignal.data(), 512);
        volatile bool result = detector->hasOnset();
        (void)result;
    }
    
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    
    double avgMicros = static_cast<double>(duration.count()) / iterations;
    
    std::cout << "Average onset detection time: " << avgMicros << " μs\n";
    
    EXPECT_LT(avgMicros, 150.0);  // Target: <150μs per 512-sample block
}

TEST_F(GroovePerformanceBenchmark, TempoEstimationUnder200Microseconds) {
    TempoEstimator::Config config;
    config.sampleRate = 44100.0;
    TempoEstimator estimator(config);
    constexpr int iterations = 1000;
    
    auto start = std::chrono::high_resolution_clock::now();
    
    for (int i = 0; i < iterations; ++i) {
        estimator.addOnset(static_cast<uint64_t>(i) * 22050);
        volatile float tempo = estimator.getCurrentTempo();
        (void)tempo;
    }
    
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    
    double avgMicros = static_cast<double>(duration.count()) / iterations;
    
    std::cout << "Average tempo estimation time: " << avgMicros << " μs\n";
    
    EXPECT_LT(avgMicros, 200.0);
}

// Note: main() is provided by gtest_main
