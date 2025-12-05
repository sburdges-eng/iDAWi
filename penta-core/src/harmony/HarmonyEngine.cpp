#include "penta/harmony/HarmonyEngine.h"

namespace penta::harmony {

HarmonyEngine::HarmonyEngine(const Config& config)
    : config_(config)
{
    chordAnalyzer_ = std::make_unique<ChordAnalyzer>();
    scaleDetector_ = std::make_unique<ScaleDetector>();
    voiceLeading_ = std::make_unique<VoiceLeading>();
    
    activeNotes_.fill(0);
    pitchClassSet_.fill(false);
    
    // Reserve space for history
    chordHistory_.reserve(config.historySize > 0 ? config.historySize : 16);
    scaleHistory_.reserve(config.historySize > 0 ? config.historySize : 16);
}

HarmonyEngine::~HarmonyEngine() = default;

void HarmonyEngine::processNotes(const Note* notes, size_t count) noexcept {
    // Update active notes and pitch class set
    for (size_t i = 0; i < count; ++i) {
        const auto& note = notes[i];
        
        if (note.velocity > 0) {
            activeNotes_[note.pitch] = note.velocity;
            pitchClassSet_[note.pitch % 12] = true;
        } else {
            activeNotes_[note.pitch] = 0;
            // Check if this was the last note of this pitch class
            bool hasNote = false;
            for (int j = note.pitch % 12; j < 128; j += 12) {
                if (activeNotes_[j] > 0) {
                    hasNote = true;
                    break;
                }
            }
            if (!hasNote) {
                pitchClassSet_[note.pitch % 12] = false;
            }
        }
    }
    
    updateChordAnalysis();
    
    if (config_.enableScaleDetection) {
        updateScaleDetection();
    }
}

void HarmonyEngine::updateChordAnalysis() noexcept {
    chordAnalyzer_->update(pitchClassSet_);
    Chord newChord = chordAnalyzer_->getCurrentChord();
    
    // Track chord history if chord changed
    if (newChord.root != currentChord_.root || newChord.quality != currentChord_.quality) {
        // Add previous chord to history if it was valid
        if (currentChord_.confidence > 0.5f) {
            chordHistory_.push_back(currentChord_);
            // Keep history bounded
            size_t maxHistory = config_.historySize > 0 ? config_.historySize : 16;
            if (chordHistory_.size() > maxHistory) {
                chordHistory_.erase(chordHistory_.begin());
            }
        }
        currentChord_ = newChord;
    } else {
        currentChord_ = newChord;
    }
}

void HarmonyEngine::updateScaleDetection() noexcept {
    // Build weighted histogram from active notes
    std::array<float, 12> histogram{};
    for (size_t i = 0; i < 128; ++i) {
        if (activeNotes_[i] > 0) {
            histogram[i % 12] += activeNotes_[i] / 127.0f;
        }
    }
    
    scaleDetector_->update(histogram);
    Scale newScale = scaleDetector_->getCurrentScale();
    
    // Track scale history if scale changed
    if (newScale.tonic != currentScale_.tonic || newScale.mode != currentScale_.mode) {
        // Add previous scale to history if it was valid
        if (currentScale_.confidence > 0.5f) {
            scaleHistory_.push_back(currentScale_);
            // Keep history bounded
            size_t maxHistory = config_.historySize > 0 ? config_.historySize : 16;
            if (scaleHistory_.size() > maxHistory) {
                scaleHistory_.erase(scaleHistory_.begin());
            }
        }
        currentScale_ = newScale;
    } else {
        currentScale_ = newScale;
    }
}

std::vector<Note> HarmonyEngine::suggestVoiceLeading(
    const Chord& targetChord,
    const std::vector<Note>& currentVoices
) const noexcept {
    if (!config_.enableVoiceLeading) {
        return {};
    }
    
    return voiceLeading_->findOptimalVoicing(targetChord, currentVoices);
}

void HarmonyEngine::updateConfig(const Config& config) {
    config_ = config;
    
    if (chordAnalyzer_) {
        chordAnalyzer_->setConfidenceThreshold(config.confidenceThreshold);
    }
    
    if (scaleDetector_) {
        scaleDetector_->setConfidenceThreshold(config.confidenceThreshold);
    }
}

std::vector<Chord> HarmonyEngine::getChordHistory(size_t maxCount) const {
    if (chordHistory_.empty()) {
        return {currentChord_};
    }
    
    size_t count = std::min(maxCount, chordHistory_.size());
    std::vector<Chord> result;
    result.reserve(count + 1);
    
    // Return most recent chords first
    for (size_t i = chordHistory_.size() - count; i < chordHistory_.size(); ++i) {
        result.push_back(chordHistory_[i]);
    }
    
    // Add current chord
    result.push_back(currentChord_);
    
    return result;
}

std::vector<Scale> HarmonyEngine::getScaleHistory(size_t maxCount) const {
    if (scaleHistory_.empty()) {
        return {currentScale_};
    }
    
    size_t count = std::min(maxCount, scaleHistory_.size());
    std::vector<Scale> result;
    result.reserve(count + 1);
    
    // Return most recent scales first
    for (size_t i = scaleHistory_.size() - count; i < scaleHistory_.size(); ++i) {
        result.push_back(scaleHistory_[i]);
    }
    
    // Add current scale
    result.push_back(currentScale_);
    
    return result;
}

} // namespace penta::harmony
