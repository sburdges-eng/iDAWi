/**
 * @file MidiIO.cpp
 * @brief MIDI I/O stub implementation
 */

#include "daiw/midi/MidiIO.h"

namespace daiw {
namespace midi {

// ============================================================================
// MidiInput Implementation (STUB)
// ============================================================================

std::vector<MidiDeviceInfo> MidiInput::getAvailableDevices() {
    // TODO: Implement with actual MIDI library
    // For now, return empty list
    return {};
}

bool MidiInput::open(int deviceId) {
    // TODO: Implement with actual MIDI library
    deviceId_ = deviceId;
    isOpen_ = false;  // Would be true after successful open
    return false;  // Not implemented
}

void MidiInput::close() {
    // TODO: Implement with actual MIDI library
    isOpen_ = false;
    isRunning_ = false;
}

void MidiInput::start() {
    // TODO: Implement with actual MIDI library
    isRunning_ = false;  // Would be true after successful start
}

void MidiInput::stop() {
    // TODO: Implement with actual MIDI library
    isRunning_ = false;
}

// ============================================================================
// MidiOutput Implementation (STUB)
// ============================================================================

std::vector<MidiDeviceInfo> MidiOutput::getAvailableDevices() {
    // TODO: Implement with actual MIDI library
    // For now, return empty list
    return {};
}

bool MidiOutput::open(int deviceId) {
    // TODO: Implement with actual MIDI library
    deviceId_ = deviceId;
    isOpen_ = false;  // Would be true after successful open
    return false;  // Not implemented
}

void MidiOutput::close() {
    // TODO: Implement with actual MIDI library
    isOpen_ = false;
}

bool MidiOutput::sendMessage(const MidiMessage& message) {
    // TODO: Implement with actual MIDI library
    (void)message;  // Suppress unused parameter warning
    return false;  // Not implemented
}

void MidiOutput::allNotesOff() {
    // TODO: Implement with actual MIDI library
    // Would send All Notes Off (CC 123) on all channels
}

} // namespace midi
} // namespace daiw
