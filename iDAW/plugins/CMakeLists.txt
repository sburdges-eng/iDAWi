# JUCE plugin targets
# Supports: FL Studio (VST3), Logic Pro (AU), Ableton Live (VST3/AU), Pro Tools (AAX), Standalone

# AAX SDK path (set via environment or CMake variable)
# Download AAX SDK from Avid Developer portal: https://developer.avid.com
if(DEFINED ENV{AAX_SDK_PATH})
    set(AAX_SDK_PATH $ENV{AAX_SDK_PATH})
endif()

# Determine available formats based on SDK availability
set(PLUGIN_FORMATS AU VST3 Standalone)
if(AAX_SDK_PATH AND EXISTS "${AAX_SDK_PATH}")
    list(APPEND PLUGIN_FORMATS AAX)
    message(STATUS "AAX SDK found at: ${AAX_SDK_PATH}")
    message(STATUS "Pro Tools AAX format enabled")
else()
    message(STATUS "AAX SDK not found. Set AAX_SDK_PATH to enable Pro Tools support.")
endif()

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
    FORMATS ${PLUGIN_FORMATS}
    PRODUCT_NAME "Penta Core"

    # FL Studio compatibility settings
    VST3_CATEGORIES "Fx|Tools"
    VST_NUM_MIDI_INS 1
    VST_NUM_MIDI_OUTS 1

    # Pro Tools AAX settings
    AAX_CATEGORY "AAX_ePlugInCategory_Effect"
    AAX_IDENTIFIER "com.penta.pentacore"
)

target_sources(PentaCorePlugin PRIVATE
    PluginProcessor.cpp
    PluginEditor.cpp
)

target_compile_definitions(PentaCorePlugin PUBLIC
    JUCE_WEB_BROWSER=0
    JUCE_USE_CURL=0
    JUCE_VST3_CAN_REPLACE_VST2=0
    # FL Studio compatibility
    JUCE_VST3_EMULATE_MIDI_CC_WITH_PARAMETERS=1
)

# Windows-specific FL Studio optimizations
if(WIN32)
    target_compile_definitions(PentaCorePlugin PUBLIC
        JUCE_WINDOWS_USE_FALLBACK_LOCALE=1
    )
endif()

target_link_libraries(PentaCorePlugin PRIVATE
    penta_core
    juce::juce_audio_utils
    juce::juce_audio_processors
    juce::juce_gui_basics
)
