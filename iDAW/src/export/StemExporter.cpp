/**
 * @file StemExporter.cpp
 * @brief Stem exporter implementation
 */

#include "daiw/export/StemExporter.h"
#include <algorithm>
#include <cmath>
#include <filesystem>

namespace daiw {
namespace export_ns {

namespace fs = std::filesystem;

std::vector<StemExportResult> StemExporter::exportAllStems(
    const project::ProjectFile& project,
    const std::string& outputDirectory,
    const ExportOptions& options) {
    
    const auto& tracks = project.getTracks();
    std::vector<size_t> allIndices(tracks.size());
    for (size_t i = 0; i < tracks.size(); ++i) {
        allIndices[i] = i;
    }
    
    return exportSelectedStems(project, allIndices, outputDirectory, options);
}

std::vector<StemExportResult> StemExporter::exportSelectedStems(
    const project::ProjectFile& project,
    const std::vector<size_t>& trackIndices,
    const std::string& outputDirectory,
    const ExportOptions& options) {
    
    std::vector<StemExportResult> results;
    const auto& tracks = project.getTracks();
    
    // Create output directory if it doesn't exist
    fs::create_directories(outputDirectory);
    
    for (size_t i = 0; i < trackIndices.size(); ++i) {
        size_t trackIdx = trackIndices[i];
        
        if (trackIdx >= tracks.size()) {
            StemExportResult result;
            result.success = false;
            result.errorMessage = "Track index out of range";
            results.push_back(result);
            continue;
        }
        
        const auto& track = tracks[trackIdx];
        
        // Progress callback
        if (progressCallback_) {
            progressCallback_(i, trackIndices.size(), track.name);
        }
        
        // Generate filename
        std::string filepath = generateStemFilename(
            track.name, trackIdx, outputDirectory, options.format, options.filenameSuffix);
        
        // Export track
        auto result = exportTrack(track, filepath, options);
        results.push_back(result);
    }
    
    return results;
}

StemExportResult StemExporter::exportTrack(
    const project::Track& track,
    const std::string& filepath,
    const ExportOptions& options) {
    
    StemExportResult result;
    result.trackName = track.name;
    result.filepath = filepath;
    
    try {
        audio::AudioFile audioFile;
        
        if (track.type == project::TrackType::Audio) {
            // Load audio file
            if (!track.audioFilePath.empty()) {
                if (!audioFile.read(track.audioFilePath)) {
                    result.success = false;
                    result.errorMessage = "Failed to read audio file: " + track.audioFilePath;
                    return result;
                }
            } else {
                result.success = false;
                result.errorMessage = "Audio track has no file path";
                return result;
            }
        } else if (track.type == project::TrackType::MIDI) {
            // Render MIDI to audio (stub)
            audioFile = renderMidiTrack(track, 10.0, options.sampleRate);
            
            if (audioFile.getData().empty()) {
                result.success = false;
                result.errorMessage = "MIDI rendering not implemented (stub only)";
                return result;
            }
        } else {
            result.success = false;
            result.errorMessage = "Unsupported track type";
            return result;
        }
        
        // Apply track volume/pan (basic mixing)
        auto& data = audioFile.getData();
        for (auto& sample : data) {
            sample *= track.volume;
        }
        
        // Normalize if requested
        if (options.normalizeStems) {
            normalizeAudio(audioFile);
        }
        
        // Write file
        if (!audioFile.write(filepath, options.format, options.sampleFormat)) {
            result.success = false;
            result.errorMessage = "Failed to write audio file";
            return result;
        }
        
        result.success = true;
        result.numSamples = audioFile.getInfo().numSamples;
        result.durationSeconds = audioFile.getInfo().durationSeconds;
        
    } catch (const std::exception& e) {
        result.success = false;
        result.errorMessage = std::string("Exception: ") + e.what();
    }
    
    return result;
}

audio::AudioFile StemExporter::renderMidiTrack(
    const project::Track& track,
    double durationSeconds,
    SampleRate sampleRate) {
    
    // TODO: Implement MIDI rendering
    // This requires a synth or sampler engine
    // For now, generate a test tone if there are MIDI events
    
    if (track.midiSequence.size() > 0) {
        // Generate a placeholder sine wave
        return audio::AudioFile::generateSineWave(440.0f, durationSeconds, sampleRate, 0.3f);
    }
    
    // Return empty audio file
    return audio::AudioFile();
}

void StemExporter::normalizeAudio(audio::AudioFile& audio, float targetLevel) {
    auto& data = audio.getData();
    
    if (data.empty()) {
        return;
    }
    
    // Find peak
    float peak = 0.0f;
    for (const auto& sample : data) {
        peak = std::max(peak, std::abs(sample));
    }
    
    if (peak > 0.0f) {
        float gain = targetLevel / peak;
        for (auto& sample : data) {
            sample *= gain;
        }
    }
}

std::string StemExporter::generateStemFilename(
    const std::string& trackName,
    size_t trackIndex,
    const std::string& outputDirectory,
    audio::AudioFormat format,
    const std::string& suffix) {
    
    std::string sanitized = sanitizeFilename(trackName);
    if (sanitized.empty()) {
        sanitized = "Track_" + std::to_string(trackIndex);
    }
    
    std::string filename = sanitized;
    if (!suffix.empty()) {
        filename += "_" + suffix;
    }
    filename += getFileExtension(format);
    
    fs::path fullPath = fs::path(outputDirectory) / filename;
    return fullPath.string();
}

std::string StemExporter::sanitizeFilename(const std::string& name) {
    std::string result;
    for (char c : name) {
        if (std::isalnum(c) || c == '_' || c == '-' || c == ' ') {
            result += c;
        } else {
            result += '_';
        }
    }
    return result;
}

std::string StemExporter::getFileExtension(audio::AudioFormat format) {
    switch (format) {
        case audio::AudioFormat::WAV:  return ".wav";
        case audio::AudioFormat::AIFF: return ".aiff";
        case audio::AudioFormat::FLAC: return ".flac";
        default: return ".wav";
    }
}

} // namespace export_ns
} // namespace daiw
