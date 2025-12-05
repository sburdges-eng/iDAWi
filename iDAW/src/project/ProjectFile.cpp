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
    // Simple JSON parser without external library
    // For production: use nlohmann::json for robust parsing
    
    if (json.empty()) {
        return false;
    }
    
    // Helper to find a string value in JSON
    auto findString = [&json](const std::string& key) -> std::string {
        std::string searchKey = "\"" + key + "\"";
        size_t keyPos = json.find(searchKey);
        if (keyPos == std::string::npos) return "";
        
        // Find the colon after the key
        size_t colonPos = json.find(':', keyPos);
        if (colonPos == std::string::npos) return "";
        
        // Find opening quote
        size_t quoteStart = json.find('"', colonPos);
        if (quoteStart == std::string::npos) return "";
        
        // Find closing quote
        size_t quoteEnd = json.find('"', quoteStart + 1);
        if (quoteEnd == std::string::npos) return "";
        
        return json.substr(quoteStart + 1, quoteEnd - quoteStart - 1);
    };
    
    // Helper to find a numeric value in JSON
    auto findNumber = [&json](const std::string& key) -> double {
        std::string searchKey = "\"" + key + "\"";
        size_t keyPos = json.find(searchKey);
        if (keyPos == std::string::npos) return 0.0;
        
        // Find the colon after the key
        size_t colonPos = json.find(':', keyPos);
        if (colonPos == std::string::npos) return 0.0;
        
        // Skip whitespace
        size_t valueStart = colonPos + 1;
        while (valueStart < json.size() && std::isspace(json[valueStart])) {
            valueStart++;
        }
        
        // Validate bounds
        if (valueStart >= json.size()) return 0.0;
        
        // Parse number
        try {
            return std::stod(json.substr(valueStart));
        } catch (...) {
            return 0.0;
        }
    };
    
    // Helper to find a boolean value in JSON
    auto findBool = [&json](const std::string& key) -> bool {
        std::string searchKey = "\"" + key + "\"";
        size_t keyPos = json.find(searchKey);
        if (keyPos == std::string::npos) return false;
        
        // Find the colon after the key
        size_t colonPos = json.find(':', keyPos);
        if (colonPos == std::string::npos) return false;
        
        // Look for "true" or "false"
        size_t truePos = json.find("true", colonPos);
        size_t falsePos = json.find("false", colonPos);
        
        // Return true if "true" comes before "false" (or false not found)
        return (truePos != std::string::npos && 
                (falsePos == std::string::npos || truePos < falsePos));
    };
    
    // Parse metadata
    metadata_.name = findString("name");
    metadata_.author = findString("author");
    metadata_.createdDate = findString("created");
    metadata_.modifiedDate = findString("modified");
    
    // Parse version
    std::string version = findString("version");
    if (!version.empty()) {
        size_t dotPos = version.find('.');
        if (dotPos != std::string::npos) {
            try {
                metadata_.versionMajor = std::stoi(version.substr(0, dotPos));
                metadata_.versionMinor = std::stoi(version.substr(dotPos + 1));
            } catch (...) {
                metadata_.versionMajor = 1;
                metadata_.versionMinor = 0;
            }
        }
    }
    
    // Parse settings
    tempo_.bpm = static_cast<float>(findNumber("tempo"));
    if (tempo_.bpm <= 0) tempo_.bpm = 120.0f;
    
    sampleRate_ = static_cast<SampleRate>(findNumber("sampleRate"));
    if (sampleRate_ == 0) sampleRate_ = DEFAULT_SAMPLE_RATE;
    
    // Parse time signature
    std::string timeSig = findString("timeSignature");
    if (!timeSig.empty()) {
        size_t slashPos = timeSig.find('/');
        if (slashPos != std::string::npos) {
            try {
                timeSignature_.numerator = static_cast<uint8_t>(std::stoi(timeSig.substr(0, slashPos)));
                timeSignature_.denominator = static_cast<uint8_t>(std::stoi(timeSig.substr(slashPos + 1)));
            } catch (...) {
                timeSignature_.numerator = 4;
                timeSignature_.denominator = 4;
            }
        }
    }
    
    // Parse mixer
    mixer_.masterVolume = static_cast<float>(findNumber("masterVolume"));
    if (mixer_.masterVolume <= 0) mixer_.masterVolume = 1.0f;
    mixer_.masterMuted = findBool("masterMuted");
    
    // Parse tracks (simplified - just count track objects for now)
    // Full track parsing would require more complex JSON array handling
    tracks_.clear();
    
    // Find tracks array
    size_t tracksPos = json.find("\"tracks\"");
    if (tracksPos != std::string::npos) {
        size_t arrayStart = json.find('[', tracksPos);
        size_t arrayEnd = json.find(']', arrayStart);
        
        if (arrayStart != std::string::npos && arrayEnd != std::string::npos) {
            std::string tracksSection = json.substr(arrayStart, arrayEnd - arrayStart + 1);
            
            // Find each track object
            size_t pos = 0;
            while ((pos = tracksSection.find('{', pos)) != std::string::npos) {
                size_t endPos = tracksSection.find('}', pos);
                if (endPos == std::string::npos) break;
                
                std::string trackJson = tracksSection.substr(pos, endPos - pos + 1);
                
                Track track;
                
                // Parse track name
                size_t namePos = trackJson.find("\"name\"");
                if (namePos != std::string::npos) {
                    size_t quoteStart = trackJson.find('"', trackJson.find(':', namePos));
                    size_t quoteEnd = trackJson.find('"', quoteStart + 1);
                    if (quoteStart != std::string::npos && quoteEnd != std::string::npos) {
                        track.name = trackJson.substr(quoteStart + 1, quoteEnd - quoteStart - 1);
                    }
                }
                
                // Parse track type
                size_t typePos = trackJson.find("\"type\"");
                if (typePos != std::string::npos) {
                    if (trackJson.find("\"midi\"", typePos) != std::string::npos) {
                        track.type = TrackType::MIDI;
                    } else if (trackJson.find("\"audio\"", typePos) != std::string::npos) {
                        track.type = TrackType::Audio;
                    } else {
                        track.type = TrackType::Aux;
                    }
                }
                
                // Parse track properties
                size_t mutedPos = trackJson.find("\"muted\"");
                if (mutedPos != std::string::npos) {
                    track.muted = (trackJson.find("true", mutedPos) != std::string::npos);
                }
                
                size_t soloedPos = trackJson.find("\"soloed\"");
                if (soloedPos != std::string::npos) {
                    track.soloed = (trackJson.find("true", soloedPos) != std::string::npos);
                }
                
                tracks_.push_back(track);
                pos = endPos + 1;
            }
        }
    }
    
    return true;
}

} // namespace project
} // namespace daiw
