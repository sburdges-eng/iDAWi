#pragma once

#include <array>
#include <cstdint>
#include <string>

namespace penta::midi {

// =============================================================================
// MIDI Constants
// =============================================================================

constexpr size_t kMaxMIDIChannels = 16;
constexpr size_t kMaxMIDINotes = 128;
constexpr size_t kMaxMIDIControllers = 128;
constexpr size_t kMIDIEventBufferSize = 4096;
constexpr uint8_t kMIDIClockPPQ = 24;  // Pulses per quarter note for MIDI clock

// =============================================================================
// MIDI Event Types (Status byte high nibble)
// =============================================================================

enum class MIDIEventType : uint8_t {
    // Channel Voice Messages (0x80-0xEF)
    NoteOff         = 0x80,
    NoteOn          = 0x90,
    PolyPressure    = 0xA0,  // Polyphonic aftertouch
    ControlChange   = 0xB0,
    ProgramChange   = 0xC0,
    ChannelPressure = 0xD0,  // Channel aftertouch
    PitchBend       = 0xE0,

    // System Common Messages (0xF0-0xF7)
    SystemExclusive = 0xF0,
    TimeCode        = 0xF1,  // MIDI Time Code Quarter Frame
    SongPosition    = 0xF2,
    SongSelect      = 0xF3,
    TuneRequest     = 0xF6,
    EndOfSysEx      = 0xF7,

    // System Real-Time Messages (0xF8-0xFF)
    TimingClock     = 0xF8,
    Start           = 0xFA,
    Continue        = 0xFB,
    Stop            = 0xFC,
    ActiveSensing   = 0xFE,
    SystemReset     = 0xFF,

    // Special value for invalid/unknown events
    Invalid         = 0x00
};

// =============================================================================
// Common MIDI Controller Numbers (CC)
// =============================================================================

namespace CC {
    constexpr uint8_t BankSelectMSB      = 0;
    constexpr uint8_t ModulationWheel    = 1;
    constexpr uint8_t BreathController   = 2;
    constexpr uint8_t FootController     = 4;
    constexpr uint8_t PortamentoTime     = 5;
    constexpr uint8_t DataEntryMSB       = 6;
    constexpr uint8_t Volume             = 7;
    constexpr uint8_t Balance            = 8;
    constexpr uint8_t Pan                = 10;
    constexpr uint8_t Expression         = 11;
    constexpr uint8_t EffectControl1     = 12;
    constexpr uint8_t EffectControl2     = 13;
    constexpr uint8_t BankSelectLSB      = 32;
    constexpr uint8_t ModulationLSB      = 33;
    constexpr uint8_t DataEntryLSB       = 38;
    constexpr uint8_t Sustain            = 64;
    constexpr uint8_t Portamento         = 65;
    constexpr uint8_t Sostenuto          = 66;
    constexpr uint8_t SoftPedal          = 67;
    constexpr uint8_t Legato             = 68;
    constexpr uint8_t Hold2              = 69;
    constexpr uint8_t SoundVariation     = 70;
    constexpr uint8_t Resonance          = 71;
    constexpr uint8_t ReleaseTime        = 72;
    constexpr uint8_t AttackTime         = 73;
    constexpr uint8_t Brightness         = 74;
    constexpr uint8_t DecayTime          = 75;
    constexpr uint8_t VibratoRate        = 76;
    constexpr uint8_t VibratoDepth       = 77;
    constexpr uint8_t VibratoDelay       = 78;
    constexpr uint8_t ReverbSend         = 91;
    constexpr uint8_t TremoloDepth       = 92;
    constexpr uint8_t ChorusSend         = 93;
    constexpr uint8_t DetuneDepth        = 94;
    constexpr uint8_t PhaserDepth        = 95;
    constexpr uint8_t DataIncrement      = 96;
    constexpr uint8_t DataDecrement      = 97;
    constexpr uint8_t NRPN_LSB           = 98;
    constexpr uint8_t NRPN_MSB           = 99;
    constexpr uint8_t RPN_LSB            = 100;
    constexpr uint8_t RPN_MSB            = 101;
    constexpr uint8_t AllSoundOff        = 120;
    constexpr uint8_t ResetAllControllers = 121;
    constexpr uint8_t LocalControl       = 122;
    constexpr uint8_t AllNotesOff        = 123;
    constexpr uint8_t OmniModeOff        = 124;
    constexpr uint8_t OmniModeOn         = 125;
    constexpr uint8_t MonoModeOn         = 126;
    constexpr uint8_t PolyModeOn         = 127;
}

// =============================================================================
// MIDI Event Structure (RT-safe, fixed size)
// =============================================================================

struct MIDIEvent {
    uint64_t timestamp;     // Sample position (absolute)
    uint32_t sampleOffset;  // Sample offset within buffer (relative)
    uint8_t  status;        // Status byte (type | channel)
    uint8_t  data1;         // First data byte (note, CC number, etc.)
    uint8_t  data2;         // Second data byte (velocity, CC value, etc.)
    uint8_t  channel;       // MIDI channel (0-15)

    // Default constructor
    constexpr MIDIEvent() noexcept
        : timestamp(0)
        , sampleOffset(0)
        , status(0)
        , data1(0)
        , data2(0)
        , channel(0)
    {}

    // Full constructor
    constexpr MIDIEvent(uint64_t ts, uint32_t offset, uint8_t stat,
                        uint8_t d1, uint8_t d2, uint8_t ch) noexcept
        : timestamp(ts)
        , sampleOffset(offset)
        , status(stat)
        , data1(d1)
        , data2(d2)
        , channel(ch)
    {}

    // Get event type (strips channel from status)
    constexpr MIDIEventType getType() const noexcept {
        if (status >= 0xF0) {
            return static_cast<MIDIEventType>(status);
        }
        return static_cast<MIDIEventType>(status & 0xF0);
    }

    // Convenience methods for note events
    constexpr bool isNoteOn() const noexcept {
        return getType() == MIDIEventType::NoteOn && data2 > 0;
    }

    constexpr bool isNoteOff() const noexcept {
        return getType() == MIDIEventType::NoteOff ||
               (getType() == MIDIEventType::NoteOn && data2 == 0);
    }

    constexpr uint8_t getNote() const noexcept { return data1; }
    constexpr uint8_t getVelocity() const noexcept { return data2; }

    // Convenience methods for CC events
    constexpr bool isControlChange() const noexcept {
        return getType() == MIDIEventType::ControlChange;
    }

    constexpr uint8_t getController() const noexcept { return data1; }
    constexpr uint8_t getControlValue() const noexcept { return data2; }

    // Pitch bend (14-bit value, centered at 8192)
    constexpr bool isPitchBend() const noexcept {
        return getType() == MIDIEventType::PitchBend;
    }

    constexpr int16_t getPitchBend() const noexcept {
        return static_cast<int16_t>((data2 << 7) | data1) - 8192;
    }

    // Factory methods
    static constexpr MIDIEvent noteOn(uint8_t channel, uint8_t note,
                                      uint8_t velocity, uint32_t offset = 0) noexcept {
        return MIDIEvent(0, offset,
                        static_cast<uint8_t>(MIDIEventType::NoteOn) | (channel & 0x0F),
                        note & 0x7F, velocity & 0x7F, channel & 0x0F);
    }

    static constexpr MIDIEvent noteOff(uint8_t channel, uint8_t note,
                                       uint8_t velocity = 0, uint32_t offset = 0) noexcept {
        return MIDIEvent(0, offset,
                        static_cast<uint8_t>(MIDIEventType::NoteOff) | (channel & 0x0F),
                        note & 0x7F, velocity & 0x7F, channel & 0x0F);
    }

    static constexpr MIDIEvent controlChange(uint8_t channel, uint8_t controller,
                                             uint8_t value, uint32_t offset = 0) noexcept {
        return MIDIEvent(0, offset,
                        static_cast<uint8_t>(MIDIEventType::ControlChange) | (channel & 0x0F),
                        controller & 0x7F, value & 0x7F, channel & 0x0F);
    }

    static constexpr MIDIEvent programChange(uint8_t channel, uint8_t program,
                                             uint32_t offset = 0) noexcept {
        return MIDIEvent(0, offset,
                        static_cast<uint8_t>(MIDIEventType::ProgramChange) | (channel & 0x0F),
                        program & 0x7F, 0, channel & 0x0F);
    }

    static constexpr MIDIEvent pitchBend(uint8_t channel, int16_t value,
                                         uint32_t offset = 0) noexcept {
        uint16_t bendVal = static_cast<uint16_t>(value + 8192);
        return MIDIEvent(0, offset,
                        static_cast<uint8_t>(MIDIEventType::PitchBend) | (channel & 0x0F),
                        bendVal & 0x7F, (bendVal >> 7) & 0x7F, channel & 0x0F);
    }

    static constexpr MIDIEvent timingClock(uint32_t offset = 0) noexcept {
        return MIDIEvent(0, offset, static_cast<uint8_t>(MIDIEventType::TimingClock),
                        0, 0, 0);
    }

    static constexpr MIDIEvent start(uint32_t offset = 0) noexcept {
        return MIDIEvent(0, offset, static_cast<uint8_t>(MIDIEventType::Start),
                        0, 0, 0);
    }

    static constexpr MIDIEvent stop(uint32_t offset = 0) noexcept {
        return MIDIEvent(0, offset, static_cast<uint8_t>(MIDIEventType::Stop),
                        0, 0, 0);
    }

    static constexpr MIDIEvent continuePlay(uint32_t offset = 0) noexcept {
        return MIDIEvent(0, offset, static_cast<uint8_t>(MIDIEventType::Continue),
                        0, 0, 0);
    }
};

// =============================================================================
// MIDI Device Information
// =============================================================================

struct MIDIDeviceInfo {
    uint32_t id;            // Platform-specific device ID
    std::string name;       // Human-readable device name
    std::string manufacturer;
    bool isInput;           // True if device can receive MIDI
    bool isOutput;          // True if device can send MIDI
    bool isVirtual;         // True if software/virtual port
    bool isOpen;            // True if currently open

    MIDIDeviceInfo()
        : id(0)
        , isInput(false)
        , isOutput(false)
        , isVirtual(false)
        , isOpen(false)
    {}

    MIDIDeviceInfo(uint32_t deviceId, const std::string& deviceName,
                   bool input, bool output, bool isVirt = false)
        : id(deviceId)
        , name(deviceName)
        , isInput(input)
        , isOutput(output)
        , isVirtual(isVirt)
        , isOpen(false)
    {}
};

// =============================================================================
// MIDI Channel State (tracks current values per channel)
// =============================================================================

class MIDIChannelState {
public:
    // Controller values (0-127 for each CC)
    std::array<uint8_t, kMaxMIDIControllers> ccValues{};

    // Per-note velocity (0 = note off)
    std::array<uint8_t, kMaxMIDINotes> noteVelocities{};

    // Channel-wide state
    int16_t pitchBend = 0;          // -8192 to 8191
    uint8_t channelPressure = 0;    // 0-127
    uint8_t programNumber = 0;      // 0-127
    uint16_t bankNumber = 0;        // 0-16383 (MSB:LSB)

    // Per-note polyphonic pressure
    std::array<uint8_t, kMaxMIDINotes> polyPressure{};

    // Active note count for this channel
    uint8_t activeNoteCount = 0;

    void reset() noexcept {
        ccValues.fill(0);
        noteVelocities.fill(0);
        polyPressure.fill(0);
        pitchBend = 0;
        channelPressure = 0;
        programNumber = 0;
        bankNumber = 0;
        activeNoteCount = 0;

        // Set default CC values
        ccValues[CC::Volume] = 100;
        ccValues[CC::Pan] = 64;       // Center
        ccValues[CC::Expression] = 127;
    }

    void processEvent(const MIDIEvent& event) noexcept {
        switch (event.getType()) {
            case MIDIEventType::NoteOn:
                if (event.data2 > 0) {
                    if (noteVelocities[event.data1] == 0) {
                        ++activeNoteCount;
                    }
                    noteVelocities[event.data1] = event.data2;
                } else {
                    // Note on with velocity 0 = note off
                    if (noteVelocities[event.data1] > 0) {
                        --activeNoteCount;
                    }
                    noteVelocities[event.data1] = 0;
                }
                break;

            case MIDIEventType::NoteOff:
                if (noteVelocities[event.data1] > 0) {
                    --activeNoteCount;
                }
                noteVelocities[event.data1] = 0;
                break;

            case MIDIEventType::ControlChange:
                ccValues[event.data1] = event.data2;
                // Handle bank select
                if (event.data1 == CC::BankSelectMSB) {
                    bankNumber = (bankNumber & 0x007F) | (event.data2 << 7);
                } else if (event.data1 == CC::BankSelectLSB) {
                    bankNumber = (bankNumber & 0x3F80) | event.data2;
                } else if (event.data1 == CC::AllNotesOff ||
                          event.data1 == CC::AllSoundOff) {
                    noteVelocities.fill(0);
                    activeNoteCount = 0;
                } else if (event.data1 == CC::ResetAllControllers) {
                    // Reset only modulation controllers, keep notes
                    ccValues[CC::ModulationWheel] = 0;
                    ccValues[CC::Expression] = 127;
                    ccValues[CC::Sustain] = 0;
                    pitchBend = 0;
                    channelPressure = 0;
                }
                break;

            case MIDIEventType::ProgramChange:
                programNumber = event.data1;
                break;

            case MIDIEventType::ChannelPressure:
                channelPressure = event.data1;
                break;

            case MIDIEventType::PolyPressure:
                polyPressure[event.data1] = event.data2;
                break;

            case MIDIEventType::PitchBend:
                pitchBend = event.getPitchBend();
                break;

            default:
                break;
        }
    }
};

// =============================================================================
// Full MIDI State (all 16 channels)
// =============================================================================

class MIDIState {
public:
    std::array<MIDIChannelState, kMaxMIDIChannels> channels;

    // Global timing state from external clock
    double tempo = 120.0;           // BPM from MIDI clock
    uint32_t clockCount = 0;        // Clock ticks received
    bool isPlaying = false;         // Received Start/Continue
    uint32_t songPosition = 0;      // Song position in MIDI beats

    void reset() noexcept {
        for (auto& ch : channels) {
            ch.reset();
        }
        tempo = 120.0;
        clockCount = 0;
        isPlaying = false;
        songPosition = 0;
    }

    void processEvent(const MIDIEvent& event) noexcept {
        // Handle channel messages
        if (event.status < 0xF0) {
            channels[event.channel].processEvent(event);
            return;
        }

        // Handle system messages
        switch (event.getType()) {
            case MIDIEventType::Start:
                isPlaying = true;
                songPosition = 0;
                clockCount = 0;
                break;

            case MIDIEventType::Continue:
                isPlaying = true;
                break;

            case MIDIEventType::Stop:
                isPlaying = false;
                break;

            case MIDIEventType::TimingClock:
                ++clockCount;
                break;

            case MIDIEventType::SongPosition:
                songPosition = (event.data2 << 7) | event.data1;
                break;

            default:
                break;
        }
    }

    MIDIChannelState& operator[](size_t channel) noexcept {
        return channels[channel & 0x0F];
    }

    const MIDIChannelState& operator[](size_t channel) const noexcept {
        return channels[channel & 0x0F];
    }
};

}  // namespace penta::midi
