/**
 * @file MidiIO.h
 * @brief MIDI input/output device management (STUB)
 *
 * This is an interface-only stub for MIDI device I/O.
 * Full implementation requires a MIDI library (RtMidi, PortMidi, etc.)
 *
 * Integration guide:
 *   1. Add RtMidi dependency (https://github.com/thestk/rtmidi)
 *   2. Replace stub methods in MidiIO.cpp with RtMidi API calls
 *   3. Handle platform-specific MIDI device enumeration
 *
 * @see MidiIO.cpp for implementation notes and integration examples
 */

#pragma once

#include "daiw/midi/MidiMessage.h"
#include <string>
#include <vector>
#include <functional>

namespace daiw {
namespace midi {

/**
 * @brief Callback function for incoming MIDI messages
 */
using MidiInputCallback = std::function<void(const MidiMessage&)>;

/**
 * @brief Information about a MIDI device
 */
struct MidiDeviceInfo {
    std::string name;
    int deviceId;
    bool isInput;
    bool isOutput;
};

/**
 * @brief MIDI input device interface (STUB)
 *
 * NOTE: This is a stub implementation. Actual device I/O requires
 * integration with a MIDI library such as:
 * - RtMidi (cross-platform, C++)
 * - PortMidi (cross-platform, C)
 * - JUCE MIDI classes (cross-platform, C++)
 *
 * Current status: Interface only - no actual device communication
 */
class MidiInput {
public:
    /**
     * @brief Enumerate available MIDI input devices
     */
    static std::vector<MidiDeviceInfo> getAvailableDevices();

    /**
     * @brief Open a MIDI input device
     * @param deviceId Device ID from getAvailableDevices()
     * @return true if successful
     */
    bool open(int deviceId);

    /**
     * @brief Close the MIDI input device
     */
    void close();

    /**
     * @brief Check if device is open
     */
    [[nodiscard]] bool isOpen() const { return isOpen_; }

    /**
     * @brief Set callback for incoming messages
     */
    void setCallback(MidiInputCallback callback) {
        callback_ = callback;
    }

    /**
     * @brief Start receiving MIDI messages
     */
    void start();

    /**
     * @brief Stop receiving MIDI messages
     */
    void stop();

private:
    bool isOpen_ = false;
    bool isRunning_ = false;
    int deviceId_ = -1;
    MidiInputCallback callback_;
};

/**
 * @brief MIDI output device interface (STUB)
 *
 * NOTE: This is a stub implementation. See MidiInput documentation
 * for library integration requirements.
 */
class MidiOutput {
public:
    /**
     * @brief Enumerate available MIDI output devices
     */
    static std::vector<MidiDeviceInfo> getAvailableDevices();

    /**
     * @brief Open a MIDI output device
     * @param deviceId Device ID from getAvailableDevices()
     * @return true if successful
     */
    bool open(int deviceId);

    /**
     * @brief Close the MIDI output device
     */
    void close();

    /**
     * @brief Check if device is open
     */
    [[nodiscard]] bool isOpen() const { return isOpen_; }

    /**
     * @brief Send a MIDI message
     * @param message The message to send
     * @return true if successful
     */
    bool sendMessage(const MidiMessage& message);

    /**
     * @brief Send all notes off on all channels
     */
    void allNotesOff();

private:
    bool isOpen_ = false;
    int deviceId_ = -1;
};

} // namespace midi
} // namespace daiw
