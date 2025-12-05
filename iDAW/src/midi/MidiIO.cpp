/**
 * @file MidiIO.cpp
 * @brief MIDI I/O stub implementation
 *
 * This is a stub implementation providing the interface for MIDI device I/O.
 * To enable actual MIDI communication, integrate with one of these libraries:
 *   - RtMidi (https://github.com/thestk/rtmidi) - Recommended, cross-platform C++
 *   - PortMidi (https://github.com/PortMidi/portmidi) - Cross-platform C
 *   - JUCE MIDI (https://juce.com) - Full audio/MIDI framework
 *
 * Integration steps:
 *   1. Add RtMidi as a dependency in CMakeLists.txt
 *   2. Replace stub methods with RtMidi API calls
 *   3. Handle platform-specific device enumeration
 */

#include "daiw/midi/MidiIO.h"

namespace daiw {
namespace midi {

// ============================================================================
// MidiInput Implementation (STUB)
// ============================================================================

std::vector<MidiDeviceInfo> MidiInput::getAvailableDevices() {
    // When integrated with RtMidi, this would:
    //   RtMidiIn midiIn;
    //   std::vector<MidiDeviceInfo> devices;
    //   for (unsigned int i = 0; i < midiIn.getPortCount(); i++) {
    //       devices.push_back({midiIn.getPortName(i), i, true, false});
    //   }
    //   return devices;
    return {};
}

bool MidiInput::open(int deviceId) {
    // When integrated with RtMidi, this would:
    //   midiIn_.openPort(deviceId);
    //   isOpen_ = true;
    //   return true;
    deviceId_ = deviceId;
    isOpen_ = false;  // Would be true after successful open
    return false;  // Not implemented
}

void MidiInput::close() {
    // When integrated with RtMidi, this would:
    //   midiIn_.closePort();
    isOpen_ = false;
    isRunning_ = false;
}

void MidiInput::start() {
    // When integrated with RtMidi, this would:
    //   midiIn_.setCallback(&midiCallback, this);
    //   isRunning_ = true;
    isRunning_ = false;  // Would be true after successful start
}

void MidiInput::stop() {
    // When integrated with RtMidi, this would:
    //   midiIn_.cancelCallback();
    isRunning_ = false;
}

// ============================================================================
// MidiOutput Implementation (STUB)
// ============================================================================

std::vector<MidiDeviceInfo> MidiOutput::getAvailableDevices() {
    // When integrated with RtMidi, this would:
    //   RtMidiOut midiOut;
    //   std::vector<MidiDeviceInfo> devices;
    //   for (unsigned int i = 0; i < midiOut.getPortCount(); i++) {
    //       devices.push_back({midiOut.getPortName(i), i, false, true});
    //   }
    //   return devices;
    return {};
}

bool MidiOutput::open(int deviceId) {
    // When integrated with RtMidi, this would:
    //   midiOut_.openPort(deviceId);
    //   isOpen_ = true;
    //   return true;
    deviceId_ = deviceId;
    isOpen_ = false;  // Would be true after successful open
    return false;  // Not implemented
}

void MidiOutput::close() {
    // When integrated with RtMidi, this would:
    //   midiOut_.closePort();
    isOpen_ = false;
}

bool MidiOutput::sendMessage(const MidiMessage& message) {
    // When integrated with RtMidi, this would:
    //   std::vector<unsigned char> msg = message.getRawData();
    //   midiOut_.sendMessage(&msg);
    //   return true;
    (void)message;  // Suppress unused parameter warning
    return false;  // Not implemented
}

void MidiOutput::allNotesOff() {
    // When integrated with RtMidi, this would send CC 123 on all channels:
    //   for (int ch = 0; ch < 16; ch++) {
    //       std::vector<unsigned char> msg = {0xB0 | ch, 123, 0};
    //       midiOut_.sendMessage(&msg);
    //   }
}

} // namespace midi
} // namespace daiw
