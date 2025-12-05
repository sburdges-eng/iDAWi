#include "penta/groove/GrooveEngine.h"
#include <algorithm>
#include <cmath>
#include <numeric>

namespace penta::groove {

GrooveEngine::GrooveEngine(const Config& config)
    : config_(config)
    , analysis_{}
    , onsetDetector_(std::make_unique<OnsetDetector>())
    , tempoEstimator_(std::make_unique<TempoEstimator>())
    , quantizer_(std::make_unique<RhythmQuantizer>())
    , samplePosition_(0)
{
    analysis_.currentTempo = 120.0f;
    analysis_.tempoConfidence = 0.0f;
    analysis_.timeSignatureNum = 4;
    analysis_.timeSignatureDen = 4;
    analysis_.swing = 0.0f;
    
    // Initialize tempo estimator with config
    TempoEstimator::Config tempoConfig;
    tempoConfig.sampleRate = config.sampleRate;
    tempoConfig.minTempo = config.minTempo;
    tempoConfig.maxTempo = config.maxTempo;
    tempoEstimator_->updateConfig(tempoConfig);
}

GrooveEngine::~GrooveEngine() = default;

void GrooveEngine::processAudio(const float* buffer, size_t frames) noexcept {
    if (onsetDetector_) {
        onsetDetector_->process(buffer, frames);
        
        if (onsetDetector_->hasOnset()) {
            uint64_t onsetPos = onsetDetector_->getOnsetPosition();
            float onsetStrength = onsetDetector_->getOnsetStrength();
            analysis_.onsetPositions.push_back(onsetPos);
            analysis_.onsetStrengths.push_back(onsetStrength);
            
            // Feed onset to tempo estimator
            if (tempoEstimator_) {
                tempoEstimator_->addOnset(samplePosition_);
            }
            
            // Keep history manageable
            onsetHistory_.push_back(onsetPos);
            if (onsetHistory_.size() > 64) {
                onsetHistory_.erase(onsetHistory_.begin());
            }
        }
    }
    
    samplePosition_ += frames;
    
    // Periodically update analysis
    if (samplePosition_ % (config_.hopSize * 8) == 0) {
        updateTempoEstimate();
        detectTimeSignature();
        analyzeSwing();
    }
}

uint64_t GrooveEngine::quantizeToGrid(uint64_t timestamp) const noexcept {
    // Guard against invalid tempo values (including very small values)
    if (!config_.enableQuantization || analysis_.currentTempo < 1.0f) {
        return timestamp;
    }
    
    // Calculate samples per beat
    double samplesPerBeat = (60.0 * config_.sampleRate) / analysis_.currentTempo;
    
    // Find the nearest beat position
    double beatPosition = static_cast<double>(timestamp) / samplesPerBeat;
    double nearestBeat = std::round(beatPosition);
    double quantizedPos = nearestBeat * samplesPerBeat;
    
    // Apply quantization strength (blend between original and quantized)
    double blendedPos = timestamp * (1.0 - config_.quantizationStrength) 
                      + quantizedPos * config_.quantizationStrength;
    
    return static_cast<uint64_t>(blendedPos);
}

uint64_t GrooveEngine::applySwing(uint64_t position) const noexcept {
    // Guard against invalid tempo values
    if (analysis_.swing <= 0.001f || analysis_.currentTempo < 1.0f) {
        return position;
    }
    
    // Calculate samples per beat and per eighth note
    double samplesPerBeat = (60.0 * config_.sampleRate) / analysis_.currentTempo;
    double samplesPerEighth = samplesPerBeat / 2.0;
    
    // Find which eighth note we're on (0 = on beat, 1 = off beat)
    double eighthPosition = static_cast<double>(position) / samplesPerEighth;
    int eighthIndex = static_cast<int>(eighthPosition) % 2;
    
    // Apply swing to off-beat notes
    if (eighthIndex == 1) {
        // Swing amount: 0.0 = straight, 1.0 = triplet feel
        double swingOffset = samplesPerEighth * analysis_.swing * 0.33;
        return static_cast<uint64_t>(position + swingOffset);
    }
    
    return position;
}

void GrooveEngine::updateConfig(const Config& config) {
    config_ = config;
    
    // Update sub-components
    if (tempoEstimator_) {
        TempoEstimator::Config tempoConfig;
        tempoConfig.sampleRate = config.sampleRate;
        tempoConfig.minTempo = config.minTempo;
        tempoConfig.maxTempo = config.maxTempo;
        tempoEstimator_->updateConfig(tempoConfig);
    }
}

void GrooveEngine::reset() {
    if (onsetDetector_) onsetDetector_->reset();
    if (tempoEstimator_) tempoEstimator_->reset();
    samplePosition_ = 0;
    onsetHistory_.clear();
    analysis_ = GrooveAnalysis{};
    analysis_.currentTempo = 120.0f;
    analysis_.timeSignatureNum = 4;
    analysis_.timeSignatureDen = 4;
}

void GrooveEngine::updateTempoEstimate() noexcept {
    if (!tempoEstimator_) return;
    
    // Get tempo estimate from the tempo estimator
    analysis_.currentTempo = tempoEstimator_->getCurrentTempo();
    analysis_.tempoConfidence = tempoEstimator_->getConfidence();
}

void GrooveEngine::detectTimeSignature() noexcept {
    if (onsetHistory_.size() < 8) {
        // Not enough data, keep default 4/4
        return;
    }
    
    // Analyze accent patterns to detect time signature
    // Count onsets per beat period
    double samplesPerBeat = (60.0 * config_.sampleRate) / analysis_.currentTempo;
    
    // Group onsets by beat position modulo different time signatures
    std::array<int, 4> counts34 = {0, 0, 0, 0};  // 3/4
    std::array<int, 5> counts44 = {0, 0, 0, 0, 0};  // 4/4
    
    for (uint64_t onset : onsetHistory_) {
        double beatPos = static_cast<double>(onset) / samplesPerBeat;
        
        // Count for 3/4
        int pos3 = static_cast<int>(beatPos) % 3;
        if (pos3 >= 0 && pos3 < 3) counts34[pos3]++;
        
        // Count for 4/4
        int pos4 = static_cast<int>(beatPos) % 4;
        if (pos4 >= 0 && pos4 < 4) counts44[pos4]++;
    }
    
    // Calculate accent strength variance - lower variance suggests that signature
    auto calcVariance = [](const auto& arr, int n) {
        float sum = 0.0f;
        for (int i = 0; i < n; i++) sum += arr[i];
        float mean = sum / n;
        float variance = 0.0f;
        for (int i = 0; i < n; i++) {
            float diff = arr[i] - mean;
            variance += diff * diff;
        }
        return variance / n;
    };
    
    float var34 = calcVariance(counts34, 3);
    float var44 = calcVariance(counts44, 4);
    
    // Higher variance suggests clearer accents on beat 1
    // Use the one with better accent pattern
    if (var34 > var44 * 1.2f) {
        analysis_.timeSignatureNum = 3;
        analysis_.timeSignatureDen = 4;
    } else {
        analysis_.timeSignatureNum = 4;
        analysis_.timeSignatureDen = 4;
    }
}

void GrooveEngine::analyzeSwing() noexcept {
    if (onsetHistory_.size() < 4 || analysis_.currentTempo <= 0.0f) {
        analysis_.swing = 0.0f;
        return;
    }
    
    // Calculate samples per eighth note
    double samplesPerBeat = (60.0 * config_.sampleRate) / analysis_.currentTempo;
    double samplesPerEighth = samplesPerBeat / 2.0;
    
    // Analyze timing deviations of off-beat notes
    float totalDeviation = 0.0f;
    int count = 0;
    
    for (size_t i = 1; i < onsetHistory_.size(); i++) {
        // Calculate which eighth note this onset is closest to
        double eighthPos = static_cast<double>(onsetHistory_[i]) / samplesPerEighth;
        int eighthIndex = static_cast<int>(std::round(eighthPos));
        
        // Check if it's an off-beat (odd eighth note)
        if (eighthIndex % 2 == 1) {
            // Calculate deviation from straight timing
            double expectedPos = eighthIndex * samplesPerEighth;
            double actualPos = static_cast<double>(onsetHistory_[i]);
            double deviation = (actualPos - expectedPos) / samplesPerEighth;
            
            // Positive deviation = pushing later (swing feel)
            if (deviation > 0.0f && deviation < 0.5f) {
                totalDeviation += static_cast<float>(deviation);
                count++;
            }
        }
    }
    
    // Calculate average swing amount
    if (count > 0) {
        float avgDeviation = totalDeviation / count;
        // Normalize: 0.0 = straight, 0.33 = triplet feel -> scale to 0-1
        analysis_.swing = std::clamp(avgDeviation * 3.0f, 0.0f, 1.0f);
    } else {
        analysis_.swing = 0.0f;
    }
}

} // namespace penta::groove
