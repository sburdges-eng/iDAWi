# JUCE plugin targets

juce_add_plugin(PentaCorePlugin
    COMPANY_NAME "Penta"
    IS_SYNTH FALSE
    NEEDS_MIDI_INPUT TRUE
    NEEDS_MIDI_OUTPUT TRUE
    IS_MIDI_EFFECT TRUE
    EDITOR_WANTS_KEYBOARD_FOCUS FALSE
    COPY_PLUGIN_AFTER_BUILD TRUE
    PLUGIN_MANUFACTURER_CODE Pent
    PLUGIN_CODE Pcor
    FORMATS AU VST3 Standalone
    PRODUCT_NAME "Penta Core"
)

target_sources(PentaCorePlugin PRIVATE
    PluginProcessor.cpp
    PluginEditor.cpp
)

target_compile_definitions(PentaCorePlugin PUBLIC
    JUCE_WEB_BROWSER=0
    JUCE_USE_CURL=0
    JUCE_VST3_CAN_REPLACE_VST2=0
)

target_link_libraries(PentaCorePlugin PRIVATE
    penta_core
    juce::juce_audio_utils
    juce::juce_audio_processors
    juce::juce_gui_basics
)
