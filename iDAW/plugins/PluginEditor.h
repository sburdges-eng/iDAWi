#pragma once

#include <JuceHeader.h>
#include "PluginProcessor.h"

/**
 * Penta Core Plugin Editor
 * Displays harmony analysis, groove info, and diagnostics
 */
class PentaCoreEditor : public juce::AudioProcessorEditor,
                        public juce::Timer {
public:
    explicit PentaCoreEditor(PentaCoreProcessor& processor);
    ~PentaCoreEditor() override;
    
    void paint(juce::Graphics& g) override;
    void resized() override;
    void timerCallback() override;
    
private:
    void drawHarmonyPanel(juce::Graphics& g, juce::Rectangle<int> bounds);
    void drawGroovePanel(juce::Graphics& g, juce::Rectangle<int> bounds);
    void drawDiagnosticsPanel(juce::Graphics& g, juce::Rectangle<int> bounds);
    
    PentaCoreProcessor& processor_;
    
    // Cached display values
    juce::String currentChordText_;
    juce::String currentScaleText_;
    float currentTempo_;
    float cpuUsage_;
    float latency_;
    
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR(PentaCoreEditor)
};
