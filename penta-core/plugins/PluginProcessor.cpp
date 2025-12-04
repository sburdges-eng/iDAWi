#include "PluginProcessor.h"
#include "PluginEditor.h"

PentaCoreProcessor::PentaCoreProcessor()
    : AudioProcessor(BusesProperties()
                       .withInput("Input", juce::AudioChannelSet::stereo(), true)
                       .withOutput("Output", juce::AudioChannelSet::stereo(), true))
    , parameters_(*this, nullptr, juce::Identifier("PentaCore"), createParameterLayout())
{
    // Initialize C++ engines
    penta::harmony::HarmonyEngine::Config harmonyConfig;
    harmonyEngine_ = std::make_unique<penta::harmony::HarmonyEngine>(harmonyConfig);
    
    penta::groove::GrooveEngine::Config grooveConfig;
    grooveEngine_ = std::make_unique<penta::groove::GrooveEngine>(grooveConfig);
    
    penta::diagnostics::DiagnosticsEngine::Config diagConfig;
    diagnosticsEngine_ = std::make_unique<penta::diagnostics::DiagnosticsEngine>(diagConfig);
    
    penta::osc::OSCHub::Config oscConfig;
    oscConfig.serverPort = 8000;
    oscConfig.clientPort = 9000;
    oscHub_ = std::make_unique<penta::osc::OSCHub>(oscConfig);
}

PentaCoreProcessor::~PentaCoreProcessor()
{
    oscHub_->stop();
}

void PentaCoreProcessor::prepareToPlay(double sampleRate, int samplesPerBlock)
{
    // Update engine configurations with DAW settings
    penta::harmony::HarmonyEngine::Config harmonyConfig;
    harmonyConfig.sampleRate = sampleRate;
    harmonyEngine_->updateConfig(harmonyConfig);
    
    penta::groove::GrooveEngine::Config grooveConfig;
    grooveConfig.sampleRate = sampleRate;
    grooveEngine_->updateConfig(grooveConfig);
    
    // Start OSC communication
    oscHub_->start();
}

void PentaCoreProcessor::releaseResources()
{
    oscHub_->stop();
}

bool PentaCoreProcessor::isBusesLayoutSupported(const BusesLayout& layouts) const
{
    return layouts.getMainOutputChannelSet() == juce::AudioChannelSet::stereo();
}

void PentaCoreProcessor::processBlock(juce::AudioBuffer<float>& buffer, 
                                      juce::MidiBuffer& midiMessages)
{
    juce::ScopedNoDenormals noDenormals;
    
    // Performance monitoring
    diagnosticsEngine_->beginMeasurement();
    
    // Process MIDI for harmony analysis
    processMidiForHarmony(midiMessages);
    
    // Process audio for groove analysis
    processAudioForGroove(buffer);
    
    // Audio analysis
    diagnosticsEngine_->analyzeAudio(
        buffer.getReadPointer(0), 
        buffer.getNumSamples(), 
        buffer.getNumChannels()
    );
    
    // Send OSC updates
    penta::osc::OSCMessage msg;
    msg.setAddress("/penta/harmony/chord");
    const auto& chord = harmonyEngine_->getCurrentChord();
    msg.addInt(chord.root);
    msg.addInt(chord.quality);
    msg.addFloat(chord.confidence);
    oscHub_->sendMessage(msg);
    
    diagnosticsEngine_->endMeasurement();
}

void PentaCoreProcessor::processMidiForHarmony(const juce::MidiBuffer& midiMessages)
{
    std::vector<penta::Note> notes;
    
    for (const auto metadata : midiMessages) {
        auto message = metadata.getMessage();
        
        if (message.isNoteOn()) {
            penta::Note note{
                static_cast<uint8_t>(message.getNoteNumber()),
                static_cast<uint8_t>(message.getVelocity()),
                static_cast<uint8_t>(message.getChannel() - 1),
                static_cast<uint64_t>(metadata.samplePosition)
            };
            notes.push_back(note);
        }
    }
    
    if (!notes.empty()) {
        harmonyEngine_->processNotes(notes.data(), notes.size());
    }
}

void PentaCoreProcessor::processAudioForGroove(const juce::AudioBuffer<float>& buffer)
{
    // Process first channel for groove analysis
    if (buffer.getNumChannels() > 0) {
        grooveEngine_->processAudio(
            buffer.getReadPointer(0), 
            buffer.getNumSamples()
        );
    }
}

juce::AudioProcessorEditor* PentaCoreProcessor::createEditor()
{
    return new PentaCoreEditor(*this);
}

void PentaCoreProcessor::getStateInformation(juce::MemoryBlock& destData)
{
    auto state = parameters_.copyState();
    std::unique_ptr<juce::XmlElement> xml(state.createXml());
    copyXmlToBinary(*xml, destData);
}

void PentaCoreProcessor::setStateInformation(const void* data, int sizeInBytes)
{
    std::unique_ptr<juce::XmlElement> xmlState(getXmlFromBinary(data, sizeInBytes));
    
    if (xmlState.get() != nullptr) {
        if (xmlState->hasTagName(parameters_.state.getType())) {
            parameters_.replaceState(juce::ValueTree::fromXml(*xmlState));
        }
    }
}

juce::AudioProcessorValueTreeState::ParameterLayout PentaCoreProcessor::createParameterLayout()
{
    juce::AudioProcessorValueTreeState::ParameterLayout layout;
    
    // Harmony parameters
    layout.add(std::make_unique<juce::AudioParameterFloat>(
        "harmonyConfidence", "Harmony Confidence", 0.0f, 1.0f, 0.5f));
    
    // Groove parameters
    layout.add(std::make_unique<juce::AudioParameterFloat>(
        "quantizeStrength", "Quantize Strength", 0.0f, 1.0f, 0.8f));
    layout.add(std::make_unique<juce::AudioParameterFloat>(
        "swingAmount", "Swing Amount", 0.0f, 1.0f, 0.5f));
    
    // OSC parameters
    layout.add(std::make_unique<juce::AudioParameterBool>(
        "oscEnabled", "OSC Enabled", true));
    
    return layout;
}

// Plugin entry point
juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new PentaCoreProcessor();
}
