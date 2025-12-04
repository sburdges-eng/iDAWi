/**
 * @file ProjectFile.cpp
 * @brief Project file implementation with JSON serialization
 *
 * Uses simple JSON formatting for now.
 * For production: consider using a JSON library (nlohmann/json, rapidjson, etc.)
 */

#include "daiw/project/ProjectFile.h"
#include <fstream>
#include <sstream>
#include <iomanip>

namespace daiw {
namespace project {

ProjectFile::ProjectFile() {
    tempo_.bpm = 120.0f;
    timeSignature_.numerator = 4;
    timeSignature_.denominator = 4;
}

bool ProjectFile::load(const std::string& filepath) {
    std::ifstream file(filepath);
    if (!file.is_open()) {
        return false;
    }

    std::stringstream buffer;
    buffer << file.rdbuf();
    return fromJSON(buffer.str());
}

bool ProjectFile::save(const std::string& filepath) const {
    std::ofstream file(filepath);
    if (!file.is_open()) {
        return false;
    }

    file << toJSON();
    return true;
}

std::string ProjectFile::toJSON() const {
    // Simple JSON formatting without external library
    // For production: use nlohmann::json or similar
    
    std::ostringstream json;
    json << std::fixed << std::setprecision(2);
    
    json << "{\n";
    
    // Metadata
    json << "  \"metadata\": {\n";
    json << "    \"name\": \"" << metadata_.name << "\",\n";
    json << "    \"author\": \"" << metadata_.author << "\",\n";
    json << "    \"created\": \"" << metadata_.createdDate << "\",\n";
    json << "    \"modified\": \"" << metadata_.modifiedDate << "\",\n";
    json << "    \"version\": \"" << metadata_.versionMajor << "." << metadata_.versionMinor << "\"\n";
    json << "  },\n";
    
    // Project settings
    json << "  \"settings\": {\n";
    json << "    \"tempo\": " << tempo_.bpm << ",\n";
    json << "    \"timeSignature\": \"" << static_cast<int>(timeSignature_.numerator) 
         << "/" << static_cast<int>(timeSignature_.denominator) << "\",\n";
    json << "    \"sampleRate\": " << sampleRate_ << "\n";
    json << "  },\n";
    
    // Mixer
    json << "  \"mixer\": {\n";
    json << "    \"masterVolume\": " << mixer_.masterVolume << ",\n";
    json << "    \"masterMuted\": " << (mixer_.masterMuted ? "true" : "false") << "\n";
    json << "  },\n";
    
    // Tracks
    json << "  \"tracks\": [\n";
    for (size_t i = 0; i < tracks_.size(); ++i) {
        const auto& track = tracks_[i];
        json << "    {\n";
        json << "      \"name\": \"" << track.name << "\",\n";
        json << "      \"type\": \"" << (track.type == TrackType::MIDI ? "midi" : 
                                        track.type == TrackType::Audio ? "audio" : "aux") << "\",\n";
        json << "      \"index\": " << track.index << ",\n";
        json << "      \"muted\": " << (track.muted ? "true" : "false") << ",\n";
        json << "      \"soloed\": " << (track.soloed ? "true" : "false") << ",\n";
        json << "      \"volume\": " << track.volume << ",\n";
        json << "      \"pan\": " << track.pan;
        
        if (track.type == TrackType::MIDI) {
            json << ",\n      \"midiEvents\": " << track.midiSequence.size();
        } else if (track.type == TrackType::Audio) {
            json << ",\n      \"audioFile\": \"" << track.audioFilePath << "\"";
        }
        
        json << "\n    }";
        if (i < tracks_.size() - 1) {
            json << ",";
        }
        json << "\n";
    }
    json << "  ]\n";
    
    json << "}\n";
    
    return json.str();
}

bool ProjectFile::fromJSON(const std::string& json) {
    // TODO: Implement JSON parsing
    // For production: use nlohmann::json or similar
    // Current stub: just validate it's not empty
    (void)json;
    return !json.empty();
}

} // namespace project
} // namespace daiw
