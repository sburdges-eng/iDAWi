#include "penta/groove/RhythmQuantizer.h"
#include <algorithm>
#include <cmath>

namespace penta::groove {

RhythmQuantizer::RhythmQuantizer(const Config& config)
    : config_(config)
{
    // Configuration is ready - swing parameters can be adjusted via config
}

uint64_t RhythmQuantizer::quantize(
    uint64_t samplePosition,
    uint64_t samplesPerBeat,
    uint64_t barStartPosition
) const noexcept {
    // Get grid interval
    uint64_t gridInterval = getGridInterval(samplesPerBeat);
    
    // Find nearest grid point
    uint64_t nearestGrid = findNearestGridPoint(samplePosition, gridInterval, barStartPosition);
    
    // Apply quantization strength
    int64_t diff = static_cast<int64_t>(nearestGrid) - static_cast<int64_t>(samplePosition);
    int64_t quantized = samplePosition + static_cast<int64_t>(diff * config_.strength);
    
    return static_cast<uint64_t>(quantized);
}

uint64_t RhythmQuantizer::applySwing(
    uint64_t samplePosition,
    uint64_t samplesPerBeat,
    uint64_t barStartPosition
) const noexcept {
    if (!config_.enableSwing || config_.swingAmount <= 0.0f) {
        return samplePosition;
    }

    // Calculate the swing subdivision (typically 8th or 16th notes)
    // Swing affects the "upbeats" - every other note in the subdivision
    uint64_t gridInterval = getGridInterval(samplesPerBeat);
    if (gridInterval == 0) return samplePosition;

    // Calculate position relative to bar start
    int64_t relativePos = static_cast<int64_t>(samplePosition - barStartPosition);
    if (relativePos < 0) return samplePosition;

    // Determine which grid position this falls on
    int64_t gridIndex = relativePos / static_cast<int64_t>(gridInterval);

    // Swing only applies to odd-numbered grid positions (upbeats)
    // e.g., in 8th notes: 1 & 2 & 3 & 4 & - swing affects the "&"s
    if (gridIndex % 2 == 0) {
        // On-beat - no swing applied
        return samplePosition;
    }

    // Calculate swing offset
    // swingAmount of 0.5 = straight (no swing)
    // swingAmount of 0.67 = typical "triplet feel" swing
    // swingAmount of 0.75 = heavy shuffle

    // The swing ratio determines how much the upbeat is delayed
    // A ratio of 2:1 means the downbeat gets 2/3 of the grid, upbeat gets 1/3
    float swingRatio = config_.swingAmount;  // 0.5 to 1.0

    // Calculate the delay for the upbeat
    // At swingRatio = 0.5 (straight), offset = 0
    // At swingRatio = 0.67 (triplet), offset = gridInterval * 0.17
    // At swingRatio = 0.75 (shuffle), offset = gridInterval * 0.25
    float offsetFactor = (swingRatio - 0.5f) * 2.0f;  // 0 to 1 range
    int64_t swingOffset = static_cast<int64_t>(gridInterval * offsetFactor * 0.5f);

    // Apply the swing offset
    return static_cast<uint64_t>(
        std::max(static_cast<int64_t>(0),
                 static_cast<int64_t>(samplePosition) + swingOffset)
    );
}

uint64_t RhythmQuantizer::getGridInterval(uint64_t samplesPerBeat) const noexcept {
    int divisor = static_cast<int>(config_.resolution);
    return samplesPerBeat / divisor;
}

void RhythmQuantizer::updateConfig(const Config& config) noexcept {
    config_ = config;
}

uint64_t RhythmQuantizer::findNearestGridPoint(
    uint64_t position,
    uint64_t gridInterval,
    uint64_t barStart
) const noexcept {
    if (gridInterval == 0) return position;
    
    // Calculate position relative to bar
    int64_t relativePos = static_cast<int64_t>(position - barStart);
    
    // Find nearest grid point
    int64_t gridIndex = (relativePos + gridInterval / 2) / gridInterval;
    int64_t gridPos = gridIndex * gridInterval;
    
    return barStart + static_cast<uint64_t>(gridPos);
}

} // namespace penta::groove
