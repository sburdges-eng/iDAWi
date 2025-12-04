#pragma once

#include <JuceHeader.h>
#include "penta/harmony/HarmonyEngine.h"
#include "penta/groove/GrooveEngine.h"
#include "penta/diagnostics/DiagnosticsEngine.h"
#include "penta/osc/OSCHub.h"
#include <memory>

/**
 * Penta Core JUCE Plugin Processor
 * Integrates C++ engines with JUCE audio plugin framework
 */
class PentaCoreProcessor : public juce::AudioProcessor {
public:
    PentaCoreProcessor();
    ~PentaCoreProcessor() override;
    
    // AudioProcessor interface
    void prepareToPlay(double sampleRate, int samplesPerBlock) override;
    void releaseResources() override;
    
    bool isBusesLayoutSupported(const BusesLayout& layouts) const override;
    
    void processBlock(juce::AudioBuffer<float>& buffer, 
                     juce::MidiBuffer& midiMessages) override;
    
    // Editor
    juce::AudioProcessorEditor* createEditor() override;
    bool hasEditor() const override { return true; }
    
    // Plugin state
    const juce::String getName() const override { return JucePlugin_Name; }
    bool acceptsMidi() const override { return true; }
    bool producesMidi() const override { return true; }
    bool isMidiEffect() const override { return true; }
    double getTailLengthSeconds() const override { return 0.0; }
    
    int getNumPrograms() override { return 1; }
    int getCurrentProgram() override { return 0; }
    void setCurrentProgram(int) override {}
    const juce::String getProgramName(int) override { return {}; }
    void changeProgramName(int, const juce::String&) override {}
    
    // State management
    void getStateInformation(juce::MemoryBlock& destData) override;
    void setStateInformation(const void* data, int sizeInBytes) override;
    
    // Access to engines (for editor)
    penta::harmony::HarmonyEngine& getHarmonyEngine() { return *harmonyEngine_; }
    penta::groove::GrooveEngine& getGrooveEngine() { return *grooveEngine_; }
    penta::diagnostics::DiagnosticsEngine& getDiagnosticsEngine() { return *diagnosticsEngine_; }
    penta::osc::OSCHub& getOSCHub() { return *oscHub_; }
    
    // Parameters
    juce::AudioProcessorValueTreeState& getParameters() { return parameters_; }
    
private:
    void processMidiForHarmony(const juce::MidiBuffer& midiMessages);
    void processAudioForGroove(const juce::AudioBuffer<float>& buffer);
    
    // Parameter layout
    juce::AudioProcessorValueTreeState::ParameterLayout createParameterLayout();
    
    // C++ engines
    std::unique_ptr<penta::harmony::HarmonyEngine> harmonyEngine_;
    std::unique_ptr<penta::groove::GrooveEngine> grooveEngine_;
    std::unique_ptr<penta::diagnostics::DiagnosticsEngine> diagnosticsEngine_;
    std::unique_ptr<penta::osc::OSCHub> oscHub_;
    
    // JUCE parameters
    juce::AudioProcessorValueTreeState parameters_;
    
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(PentaCoreProcessor)
};
