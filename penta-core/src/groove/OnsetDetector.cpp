#include "penta/groove/OnsetDetector.h"
#include <algorithm>
#include <cmath>
#include <numeric>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

namespace penta::groove {

namespace {

// Simple Hann window coefficient generator
inline float hannWindow(size_t n, size_t N) {
    return 0.5f * (1.0f - std::cos(2.0f * static_cast<float>(M_PI) * n / (N - 1)));
}

// Simplified DFT for magnitude spectrum
// In production, use an optimized FFT library (FFTW, pffft, etc.)
// This implementation is RT-safe (no allocations) but not optimal
void computeMagnitudeSpectrum(
    const float* input,
    const float* window,
    size_t fftSize,
    float* spectrum
) noexcept {
    const size_t numBins = fftSize / 2 + 1;

    // Apply window and compute magnitude at each frequency bin
    for (size_t k = 0; k < numBins; ++k) {
        float real = 0.0f;
        float imag = 0.0f;

        for (size_t n = 0; n < fftSize; ++n) {
            float angle = -2.0f * static_cast<float>(M_PI) * k * n / fftSize;
            float windowed = input[n] * window[n];
            real += windowed * std::cos(angle);
            imag += windowed * std::sin(angle);
        }

        spectrum[k] = std::sqrt(real * real + imag * imag);
    }
}

} // anonymous namespace

OnsetDetector::OnsetDetector(const Config& config)
    : config_(config)
    , onsetDetected_(false)
    , onsetStrength_(0.0f)
    , onsetPosition_(0)
    , lastOnsetPosition_(0)
    , sampleCounter_(0)
{
    // Pre-allocate buffers
    fftBuffer_.resize(config_.fftSize);
    spectrum_.resize(config_.fftSize / 2 + 1);
    prevSpectrum_.resize(config_.fftSize / 2 + 1);
    fluxHistory_.resize(100);

    // Initialize Hann window
    window_.resize(config_.fftSize);
    for (size_t i = 0; i < config_.fftSize; ++i) {
        window_[i] = hannWindow(i, config_.fftSize);
    }

    // Initialize spectrums to zero
    std::fill(spectrum_.begin(), spectrum_.end(), 0.0f);
    std::fill(prevSpectrum_.begin(), prevSpectrum_.end(), 0.0f);
    std::fill(fluxHistory_.begin(), fluxHistory_.end(), 0.0f);
}

OnsetDetector::~OnsetDetector() = default;

void OnsetDetector::process(const float* buffer, size_t frames) noexcept {
    onsetDetected_ = false;
    onsetStrength_ = 0.0f;

    // Process in hop-sized chunks
    for (size_t offset = 0; offset + config_.hopSize <= frames; offset += config_.hopSize) {
        // Copy samples to FFT buffer
        size_t available = std::min(config_.fftSize, frames - offset);
        std::copy(buffer + offset, buffer + offset + available, fftBuffer_.begin());

        // Zero-pad if needed
        if (available < config_.fftSize) {
            std::fill(fftBuffer_.begin() + available, fftBuffer_.end(), 0.0f);
        }

        // Compute spectral flux for this frame
        computeSpectralFlux(fftBuffer_.data(), config_.fftSize);

        // Check for peaks
        detectPeaks();
    }

    sampleCounter_ += frames;
}

void OnsetDetector::setThreshold(float threshold) noexcept {
    config_.threshold = std::clamp(threshold, 0.0f, 1.0f);
}

void OnsetDetector::reset() noexcept {
    onsetDetected_ = false;
    onsetStrength_ = 0.0f;
    onsetPosition_ = 0;
    lastOnsetPosition_ = 0;
    sampleCounter_ = 0;
    std::fill(prevSpectrum_.begin(), prevSpectrum_.end(), 0.0f);
    std::fill(fluxHistory_.begin(), fluxHistory_.end(), 0.0f);
}

void OnsetDetector::computeSpectralFlux(const float* buffer, size_t frames) noexcept {
    // Compute magnitude spectrum
    computeMagnitudeSpectrum(buffer, window_.data(), frames, spectrum_.data());

    // Calculate spectral flux (half-wave rectified difference)
    // Only positive changes (increases in energy) count as potential onsets
    float flux = 0.0f;
    const size_t numBins = frames / 2 + 1;

    for (size_t k = 0; k < numBins; ++k) {
        float diff = spectrum_[k] - prevSpectrum_[k];
        if (diff > 0.0f) {
            flux += diff * diff;  // Square for emphasis
        }
    }

    // Normalize by number of bins
    flux = std::sqrt(flux / numBins);

    // Store current spectrum as previous for next frame
    std::copy(spectrum_.begin(), spectrum_.end(), prevSpectrum_.begin());

    // Add to flux history (circular buffer)
    static size_t fluxIndex = 0;
    fluxHistory_[fluxIndex % fluxHistory_.size()] = flux;
    fluxIndex++;

    // Store latest flux as onset strength
    onsetStrength_ = flux;
}

void OnsetDetector::detectPeaks() noexcept {
    // Adaptive threshold based on recent flux history
    float mean = 0.0f;
    float stddev = 0.0f;

    // Calculate mean of flux history
    for (float f : fluxHistory_) {
        mean += f;
    }
    mean /= static_cast<float>(fluxHistory_.size());

    // Calculate standard deviation
    for (float f : fluxHistory_) {
        float diff = f - mean;
        stddev += diff * diff;
    }
    stddev = std::sqrt(stddev / static_cast<float>(fluxHistory_.size()));

    // Dynamic threshold: mean + threshold * stddev
    float dynamicThreshold = mean + config_.threshold * stddev;

    // Check if current flux exceeds threshold
    if (onsetStrength_ > dynamicThreshold && onsetStrength_ > 0.01f) {
        // Enforce minimum time between onsets
        uint64_t minSamplesBetween = static_cast<uint64_t>(
            config_.minTimeBetweenOnsets * config_.sampleRate
        );

        if (sampleCounter_ - lastOnsetPosition_ >= minSamplesBetween) {
            onsetDetected_ = true;
            onsetPosition_ = sampleCounter_;
            lastOnsetPosition_ = sampleCounter_;

            // Normalize onset strength to 0-1 range
            if (dynamicThreshold > 0.0f) {
                onsetStrength_ = std::clamp(
                    (onsetStrength_ - dynamicThreshold) / dynamicThreshold,
                    0.0f, 1.0f
                );
            }
        }
    }
}

} // namespace penta::groove
