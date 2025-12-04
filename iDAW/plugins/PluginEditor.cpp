#include "PluginEditor.h"

static const char* NOTE_NAMES[] = {"C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"};
static const char* CHORD_QUALITY_NAMES[] = {"Maj", "min", "dim", "aug", "dom7", "maj7", "min7"};

PentaCoreEditor::PentaCoreEditor(PentaCoreProcessor& p)
    : AudioProcessorEditor(&p)
    , processor_(p)
    , currentTempo_(120.0f)
    , cpuUsage_(0.0f)
    , latency_(0.0f)
{
    setSize(800, 600);
    startTimerHz(30); // 30 Hz refresh rate
}

PentaCoreEditor::~PentaCoreEditor()
{
    stopTimer();
}

void PentaCoreEditor::paint(juce::Graphics& g)
{
    g.fillAll(juce::Colour(0xff1a1a1a));
    
    auto bounds = getLocalBounds();
    
    // Split into three panels
    auto harmonyBounds = bounds.removeFromTop(bounds.getHeight() / 3);
    auto grooveBounds = bounds.removeFromTop(bounds.getHeight() / 2);
    auto diagBounds = bounds;
    
    drawHarmonyPanel(g, harmonyBounds.reduced(10));
    drawGroovePanel(g, grooveBounds.reduced(10));
    drawDiagnosticsPanel(g, diagBounds.reduced(10));
}

void PentaCoreEditor::resized()
{
    // Layout will be handled in paint for now
}

void PentaCoreEditor::timerCallback()
{
    // Update harmony info
    const auto& chord = processor_.getHarmonyEngine().getCurrentChord();
    const auto& scale = processor_.getHarmonyEngine().getCurrentScale();
    
    if (chord.root < 12) {
        currentChordText_ = juce::String(NOTE_NAMES[chord.root]);
        if (chord.quality < 7) {
            currentChordText_ += juce::String(" ") + CHORD_QUALITY_NAMES[chord.quality];
        }
        currentChordText_ += juce::String(" (") + juce::String(chord.confidence, 2) + ")";
    } else {
        currentChordText_ = "No chord";
    }
    
    if (scale.tonic < 12) {
        currentScaleText_ = juce::String(NOTE_NAMES[scale.tonic]) + " scale";
        currentScaleText_ += juce::String(" (") + juce::String(scale.confidence, 2) + ")";
    } else {
        currentScaleText_ = "No scale";
    }
    
    // Update groove info
    const auto& analysis = processor_.getGrooveEngine().getAnalysis();
    currentTempo_ = analysis.currentTempo;
    
    // Update diagnostics
    const auto stats = processor_.getDiagnosticsEngine().getStats();
    cpuUsage_ = stats.cpuUsagePercent;
    latency_ = stats.averageLatencyMs;
    
    repaint();
}

void PentaCoreEditor::drawHarmonyPanel(juce::Graphics& g, juce::Rectangle<int> bounds)
{
    g.setColour(juce::Colour(0xff2a2a2a));
    g.fillRoundedRectangle(bounds.toFloat(), 5.0f);
    
    g.setColour(juce::Colours::white);
    g.setFont(16.0f);
    g.drawText("HARMONY ANALYSIS", bounds.removeFromTop(30), juce::Justification::centred);
    
    g.setFont(24.0f);
    g.setColour(juce::Colour(0xff4CAF50));
    g.drawText(currentChordText_, bounds.removeFromTop(40), juce::Justification::centred);
    
    g.setFont(18.0f);
    g.setColour(juce::Colours::lightgrey);
    g.drawText(currentScaleText_, bounds.removeFromTop(30), juce::Justification::centred);
}

void PentaCoreEditor::drawGroovePanel(juce::Graphics& g, juce::Rectangle<int> bounds)
{
    g.setColour(juce::Colour(0xff2a2a2a));
    g.fillRoundedRectangle(bounds.toFloat(), 5.0f);
    
    g.setColour(juce::Colours::white);
    g.setFont(16.0f);
    g.drawText("GROOVE ANALYSIS", bounds.removeFromTop(30), juce::Justification::centred);
    
    g.setFont(24.0f);
    g.setColour(juce::Colour(0xff2196F3));
    auto tempoText = juce::String(currentTempo_, 1) + " BPM";
    g.drawText(tempoText, bounds.removeFromTop(40), juce::Justification::centred);
    
    const auto& analysis = processor_.getGrooveEngine().getAnalysis();
    g.setFont(18.0f);
    g.setColour(juce::Colours::lightgrey);
    auto timeSigText = juce::String(analysis.timeSignatureNum) + "/" + 
                       juce::String(analysis.timeSignatureDen);
    g.drawText(timeSigText, bounds.removeFromTop(30), juce::Justification::centred);
}

void PentaCoreEditor::drawDiagnosticsPanel(juce::Graphics& g, juce::Rectangle<int> bounds)
{
    g.setColour(juce::Colour(0xff2a2a2a));
    g.fillRoundedRectangle(bounds.toFloat(), 5.0f);
    
    g.setColour(juce::Colours::white);
    g.setFont(16.0f);
    g.drawText("DIAGNOSTICS", bounds.removeFromTop(30), juce::Justification::centred);
    
    bounds.reduce(20, 10);
    
    g.setFont(14.0f);
    g.setColour(juce::Colours::lightgrey);
    
    auto cpuText = "CPU: " + juce::String(cpuUsage_, 1) + "%";
    g.drawText(cpuText, bounds.removeFromTop(25), juce::Justification::left);
    
    auto latencyText = "Latency: " + juce::String(latency_, 2) + " ms";
    g.drawText(latencyText, bounds.removeFromTop(25), juce::Justification::left);
    
    const auto stats = processor_.getDiagnosticsEngine().getStats();
    auto xrunText = "XRuns: " + juce::String(stats.xrunCount);
    g.drawText(xrunText, bounds.removeFromTop(25), juce::Justification::left);
}
