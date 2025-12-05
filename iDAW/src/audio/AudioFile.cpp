/**
 * @file AudioFile.cpp
 * @brief Audio file implementation
 *
 * NOTE: This is a stub implementation that works without libsndfile.
 * For production use, integrate libsndfile for robust file I/O.
 *
 * Current implementation:
 * - Generates test data (sine waves)
 * - Placeholder read/write methods
 * - Basic WAV header writing (simple PCM only)
 */

#include "daiw/audio/AudioFile.h"
#include <cmath>
#include <fstream>
#include <algorithm>
#include <cstring>

namespace daiw {
namespace audio {

// Simple WAV header structure
struct WAVHeader {
    char riff[4] = {'R', 'I', 'F', 'F'};
    uint32_t fileSize = 0;
    char wave[4] = {'W', 'A', 'V', 'E'};
    char fmt[4] = {'f', 'm', 't', ' '};
    uint32_t fmtSize = 16;
    uint16_t audioFormat = 3;  // 3 = IEEE float
    uint16_t numChannels = 0;
    uint32_t sampleRate = 0;
    uint32_t byteRate = 0;
    uint16_t blockAlign = 0;
    uint16_t bitsPerSample = 32;
    char data[4] = {'d', 'a', 't', 'a'};
    uint32_t dataSize = 0;
};

struct AudioFile::Impl {
    // Placeholder for libsndfile handle
    // In full implementation: SNDFILE* sndfile = nullptr;
};

AudioFile::AudioFile() : impl_(std::make_unique<Impl>()) {}

AudioFile::~AudioFile() = default;

AudioFile::AudioFile(AudioFile&&) noexcept = default;
AudioFile& AudioFile::operator=(AudioFile&&) noexcept = default;

bool AudioFile::read(const std::string& filepath) {
    // Basic WAV file reader implementation
    // Supports: WAV format, float32 and int16 sample formats
    // For extended format support (AIFF, FLAC, OGG), integrate libsndfile

    std::ifstream file(filepath, std::ios::binary);
    if (!file.is_open()) {
        return false;
    }

    // Read WAV header
    WAVHeader header;
    file.read(reinterpret_cast<char*>(&header), sizeof(WAVHeader));
    
    if (std::strncmp(header.riff, "RIFF", 4) != 0 ||
        std::strncmp(header.wave, "WAVE", 4) != 0) {
        return false;  // Not a WAV file
    }

    // Set file info
    info_.format = AudioFormat::WAV;
    info_.sampleRate = header.sampleRate;
    info_.numChannels = header.numChannels;
    info_.numSamples = header.dataSize / (header.numChannels * (header.bitsPerSample / 8));
    info_.durationSeconds = static_cast<double>(info_.numSamples) / info_.sampleRate;
    info_.sampleFormat = (header.bitsPerSample == 32) ? SampleFormat::Float32 : SampleFormat::Int16;

    // Read audio data
    data_.resize(header.dataSize / sizeof(Sample));
    file.read(reinterpret_cast<char*>(data_.data()), header.dataSize);

    return true;
}

bool AudioFile::write(const std::string& filepath,
                     AudioFormat format,
                     SampleFormat sampleFormat) {
    // WAV float32 writer implementation
    // Supports: WAV format with IEEE float (format code 3)
    // For extended format support (AIFF, FLAC, OGG), integrate libsndfile

    if (format != AudioFormat::WAV || sampleFormat != SampleFormat::Float32) {
        // Only WAV float supported in stub
        return false;
    }

    std::ofstream file(filepath, std::ios::binary);
    if (!file.is_open()) {
        return false;
    }

    // Create WAV header
    WAVHeader header;
    header.numChannels = static_cast<uint16_t>(info_.numChannels);
    header.sampleRate = info_.sampleRate;
    header.bitsPerSample = 32;
    header.blockAlign = header.numChannels * (header.bitsPerSample / 8);
    header.byteRate = header.sampleRate * header.blockAlign;
    header.dataSize = static_cast<uint32_t>(data_.size() * sizeof(Sample));
    header.fileSize = 36 + header.dataSize;

    // Write header
    file.write(reinterpret_cast<const char*>(&header), sizeof(WAVHeader));

    // Write audio data
    file.write(reinterpret_cast<const char*>(data_.data()), header.dataSize);

    return true;
}

void AudioFile::setData(const std::vector<Sample>& data,
                       uint32_t numChannels,
                       SampleRate sampleRate) {
    data_ = data;
    info_.numChannels = numChannels;
    info_.sampleRate = sampleRate;
    info_.numSamples = data.size() / numChannels;
    info_.durationSeconds = static_cast<double>(info_.numSamples) / sampleRate;
    info_.format = AudioFormat::WAV;
    info_.sampleFormat = SampleFormat::Float32;
}

std::vector<Sample> AudioFile::getChannelData(uint32_t channel) const {
    if (channel >= info_.numChannels) {
        return {};
    }

    std::vector<Sample> channelData;
    channelData.reserve(info_.numSamples);

    for (size_t i = channel; i < data_.size(); i += info_.numChannels) {
        channelData.push_back(data_[i]);
    }

    return channelData;
}

void AudioFile::setChannelData(const std::vector<std::vector<Sample>>& channels,
                              SampleRate sampleRate) {
    if (channels.empty()) {
        return;
    }

    info_.numChannels = static_cast<uint32_t>(channels.size());
    info_.numSamples = channels[0].size();
    info_.sampleRate = sampleRate;
    info_.durationSeconds = static_cast<double>(info_.numSamples) / sampleRate;
    info_.format = AudioFormat::WAV;
    info_.sampleFormat = SampleFormat::Float32;

    // Interleave channels
    data_.resize(info_.numSamples * info_.numChannels);
    for (size_t sample = 0; sample < info_.numSamples; ++sample) {
        for (size_t ch = 0; ch < info_.numChannels; ++ch) {
            data_[sample * info_.numChannels + ch] = channels[ch][sample];
        }
    }
}

bool AudioFile::convertSampleRate(SampleRate targetRate) {
    if (targetRate == info_.sampleRate || data_.empty()) {
        return true;  // No conversion needed
    }
    
    if (targetRate == 0 || info_.sampleRate == 0) {
        return false;  // Invalid sample rates
    }
    
    // Calculate conversion ratio
    double ratio = static_cast<double>(targetRate) / static_cast<double>(info_.sampleRate);
    
    // Calculate new size
    size_t newNumSamples = static_cast<size_t>(info_.numSamples * ratio);
    size_t newTotalSamples = newNumSamples * info_.numChannels;
    
    std::vector<Sample> newData(newTotalSamples);
    
    // Linear interpolation resampling
    // For production: use libsamplerate for higher quality sinc interpolation
    for (uint32_t ch = 0; ch < info_.numChannels; ++ch) {
        for (size_t i = 0; i < newNumSamples; ++i) {
            // Calculate source position
            double srcPos = static_cast<double>(i) / ratio;
            size_t srcIdx = static_cast<size_t>(srcPos);
            double frac = srcPos - srcIdx;
            
            // Clamp to valid range with underflow protection
            if (info_.numSamples < 2) {
                // If only 0 or 1 samples, just use first sample or zero
                size_t srcOffset0 = (info_.numSamples > 0) ? ch : 0;
                newData[i * info_.numChannels + ch] = (info_.numSamples > 0) ? data_[srcOffset0] : 0.0f;
                continue;
            }
            
            if (srcIdx >= info_.numSamples - 1) {
                srcIdx = info_.numSamples - 2;
                frac = 1.0;
            }
            
            // Get source samples (interleaved format)
            size_t srcOffset0 = srcIdx * info_.numChannels + ch;
            size_t srcOffset1 = (srcIdx + 1) * info_.numChannels + ch;
            
            Sample s0 = data_[srcOffset0];
            Sample s1 = (srcOffset1 < data_.size()) ? data_[srcOffset1] : s0;
            
            // Linear interpolation
            Sample interpolated = static_cast<Sample>(s0 * (1.0 - frac) + s1 * frac);
            
            // Store in new data (interleaved format)
            newData[i * info_.numChannels + ch] = interpolated;
        }
    }
    
    // Update data and info
    data_ = std::move(newData);
    info_.sampleRate = targetRate;
    info_.numSamples = newNumSamples;
    info_.durationSeconds = static_cast<double>(newNumSamples) / targetRate;
    
    return true;
}

AudioFile AudioFile::generateSineWave(float frequency,
                                     double durationSeconds,
                                     SampleRate sampleRate,
                                     float amplitude) {
    AudioFile file;
    
    const size_t numSamples = static_cast<size_t>(durationSeconds * sampleRate);
    std::vector<Sample> data(numSamples);
    
    const float angularFreq = 2.0f * static_cast<float>(M_PI) * frequency;
    
    for (size_t i = 0; i < numSamples; ++i) {
        float time = static_cast<float>(i) / static_cast<float>(sampleRate);
        data[i] = amplitude * std::sin(angularFreq * time);
    }
    
    file.setData(data, 1, sampleRate);
    return file;
}

AudioFormat AudioFile::detectFormat(const std::string& filepath) {
    if (filepath.length() < 4) {
        return AudioFormat::Unknown;
    }

    std::string ext = filepath.substr(filepath.length() - 4);
    std::transform(ext.begin(), ext.end(), ext.begin(), ::tolower);

    if (ext == ".wav") return AudioFormat::WAV;
    if (ext == "aiff" || ext == ".aif") return AudioFormat::AIFF;
    if (ext == "flac") return AudioFormat::FLAC;

    return AudioFormat::Unknown;
}

} // namespace audio
} // namespace daiw
