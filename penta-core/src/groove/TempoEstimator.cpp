#include "penta/groove/TempoEstimator.h"
#include <algorithm>
#include <cmath>
#include <numeric>

namespace penta::groove {

TempoEstimator::TempoEstimator(const Config& config)
    : config_(config)
    , currentTempo_(120.0f)
    , confidence_(0.0f)
    , lastOnsetPosition_(0)
{
    onsetHistory_.reserve(config.historySize);
}

void TempoEstimator::addOnset(uint64_t samplePosition) noexcept {
    onsetHistory_.push_back(samplePosition);

    // Keep only recent history
    if (onsetHistory_.size() > config_.historySize) {
        onsetHistory_.erase(onsetHistory_.begin());
    }

    lastOnsetPosition_ = samplePosition;

    // Estimate tempo if we have enough onsets
    if (onsetHistory_.size() >= 4) {
        estimateTempo();
    }
}

uint64_t TempoEstimator::getSamplesPerBeat() const noexcept {
    if (currentTempo_ <= 0.0f) return 0;
    return static_cast<uint64_t>((60.0 * config_.sampleRate) / currentTempo_);
}

void TempoEstimator::updateConfig(const Config& config) noexcept {
    config_ = config;
    onsetHistory_.reserve(config.historySize);
}

void TempoEstimator::reset() noexcept {
    onsetHistory_.clear();
    currentTempo_ = 120.0f;
    confidence_ = 0.0f;
    lastOnsetPosition_ = 0;
}

void TempoEstimator::estimateTempo() noexcept {
    if (onsetHistory_.size() < 2) return;

    // Calculate inter-onset intervals (IOIs)
    std::vector<float> intervals;
    intervals.reserve(onsetHistory_.size() - 1);

    for (size_t i = 1; i < onsetHistory_.size(); ++i) {
        float intervalSec = static_cast<float>(onsetHistory_[i] - onsetHistory_[i - 1])
                          / config_.sampleRate;
        intervals.push_back(intervalSec);
    }

    if (intervals.empty()) return;

    // Use autocorrelation to find dominant periodicity
    // First, convert intervals to a histogram of tempos

    // Calculate tempo candidates from intervals
    std::vector<float> tempoCandidates;
    tempoCandidates.reserve(intervals.size());

    for (float interval : intervals) {
        if (interval > 0.0f) {
            float bpm = 60.0f / interval;
            // Constrain to reasonable tempo range
            while (bpm < config_.minTempo) bpm *= 2.0f;
            while (bpm > config_.maxTempo) bpm /= 2.0f;
            tempoCandidates.push_back(bpm);
        }
    }

    if (tempoCandidates.empty()) return;

    // Use autocorrelation on the IOI sequence to find periodicity
    float bestTempo = autocorrelate(intervals);

    // If autocorrelation fails, fall back to median IOI
    if (bestTempo <= 0.0f) {
        // Sort and find median interval
        std::sort(tempoCandidates.begin(), tempoCandidates.end());
        bestTempo = tempoCandidates[tempoCandidates.size() / 2];
    }

    // Apply constraints
    bestTempo = std::clamp(bestTempo, config_.minTempo, config_.maxTempo);

    // Calculate confidence based on consistency of intervals
    float variance = 0.0f;
    float meanTempo = std::accumulate(tempoCandidates.begin(), tempoCandidates.end(), 0.0f)
                    / tempoCandidates.size();

    for (float t : tempoCandidates) {
        float diff = t - meanTempo;
        variance += diff * diff;
    }
    variance /= tempoCandidates.size();

    // Convert variance to confidence (lower variance = higher confidence)
    // Normalize by expected variance at this tempo
    float expectedVariance = meanTempo * 0.1f;  // 10% variance is normal
    confidence_ = 1.0f / (1.0f + variance / (expectedVariance * expectedVariance));

    // Apply temporal smoothing using adaptationRate
    // Higher adaptationRate means faster adaptation to new tempo
    float smoothingFactor = 1.0f - config_.adaptationRate;
    currentTempo_ = smoothingFactor * currentTempo_
                  + config_.adaptationRate * bestTempo;
}

float TempoEstimator::autocorrelate(const std::vector<float>& intervals) const noexcept {
    if (intervals.size() < 4) return 0.0f;

    // Convert intervals to a pulse train at multiple tempo hypotheses
    // and find the tempo with highest autocorrelation

    float bestCorrelation = 0.0f;
    float bestTempo = 0.0f;

    // Test tempo hypotheses from minTempo to maxTempo
    const float tempoStep = 1.0f;  // 1 BPM resolution

    for (float tempoHypothesis = config_.minTempo;
         tempoHypothesis <= config_.maxTempo;
         tempoHypothesis += tempoStep) {

        // Calculate expected beat period
        float beatPeriod = 60.0f / tempoHypothesis;

        // Score this tempo hypothesis against the intervals
        float correlation = 0.0f;
        int count = 0;

        for (float interval : intervals) {
            // Find how many beats this interval represents
            float beats = interval / beatPeriod;
            float roundedBeats = std::round(beats);

            // Skip if too far from an integer number of beats
            if (roundedBeats < 0.5f || roundedBeats > 8.0f) continue;

            // Calculate error from exact beat multiple
            float error = std::abs(beats - roundedBeats);
            float score = std::exp(-error * error * 10.0f);  // Gaussian weighting

            correlation += score;
            ++count;
        }

        // Normalize correlation
        if (count > 0) {
            correlation /= count;
        }

        // Prefer tempos that align with more intervals
        correlation *= std::min(1.0f, static_cast<float>(count) / 4.0f);

        if (correlation > bestCorrelation) {
            bestCorrelation = correlation;
            bestTempo = tempoHypothesis;
        }
    }

    return bestTempo;
}

} // namespace penta::groove
