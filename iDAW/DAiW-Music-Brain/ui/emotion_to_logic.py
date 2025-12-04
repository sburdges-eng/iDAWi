"""
Streamlit UI for Music Brain Logic Pro Integration
"""

import streamlit as st
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from music_brain.api import MusicBrain
from music_brain.emotion.text_analyzer import TextEmotionAnalyzer


st.set_page_config(
    page_title="Music Brain - Logic Pro",
    page_icon="",
    layout="wide"
)

st.title("Music Brain - Logic Pro")
st.markdown("*Interrogate Before Generate* - Emotion-driven music automation")

# Sidebar
st.sidebar.header("Settings")
mode = st.sidebar.radio(
    "Generation Mode",
    ["Simple Text", "Detailed Intent", "Emotion Explorer"]
)

# Initialize
if 'brain' not in st.session_state:
    st.session_state.brain = MusicBrain()
    st.session_state.analyzer = TextEmotionAnalyzer()

brain = st.session_state.brain
analyzer = st.session_state.analyzer

# ========== SIMPLE TEXT MODE ==========
if mode == "Simple Text":
    st.header("Generate from Emotional Text")

    emotion_text = st.text_area(
        "Describe your emotional state:",
        placeholder="e.g., 'grief and loss', 'explosive anger', 'anxious tension'",
        height=100
    )

    col1, col2 = st.columns([1, 3])

    with col1:
        if st.button("Analyze", type="primary"):
            if emotion_text:
                with st.spinner("Analyzing..."):
                    matches = analyzer.analyze(emotion_text)
                    st.session_state.matches = matches
                    st.session_state.analyzed_text = emotion_text

    with col2:
        if st.button("Generate Music", type="primary"):
            if emotion_text:
                with st.spinner("Generating..."):
                    music = brain.generate_from_text(emotion_text)
                    st.session_state.music = music
                    st.success("Music generated!")

    # Show analysis results
    if 'matches' in st.session_state and st.session_state.get('analyzed_text') == emotion_text:
        st.subheader("Detected Emotions")

        for i, match in enumerate(st.session_state.matches[:5], 1):
            with st.expander(f"{i}. {match.emotion} - {match.confidence:.0%} confidence"):
                st.write(f"**Category:** {match.category}")
                st.write(f"**Sub-emotion:** {match.sub_emotion}")
                st.write(f"**Keywords matched:** {', '.join(match.keywords_matched)}")

    # Show generated music
    if 'music' in st.session_state:
        music = st.session_state.music

        st.divider()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("Emotional State")
            st.metric("Primary Emotion", music.emotional_state.primary_emotion)
            st.metric("Valence", f"{music.emotional_state.valence:.2f}")
            st.metric("Arousal", f"{music.emotional_state.arousal:.2f}")

        with col2:
            st.subheader("Musical Parameters")
            st.metric("Tempo", f"{music.musical_params.tempo_suggested} BPM")
            st.metric("Dissonance", f"{music.musical_params.dissonance:.1%}")
            st.metric("Timing Feel", music.musical_params.timing_feel.value)

        with col3:
            st.subheader("Mixer Settings")
            st.metric("Reverb Mix", f"{music.mixer_params.reverb_mix:.1%}")
            st.metric("Compression", f"{music.mixer_params.compression_ratio:.1f}:1")
            st.metric("Saturation", f"{music.mixer_params.saturation:.1%}")

        st.divider()

        # Detailed mixer settings
        with st.expander("Detailed Mixer Settings"):
            col1, col2 = st.columns(2)

            with col1:
                st.write("**EQ Settings (dB)**")
                st.write(f"Sub Bass: {music.mixer_params.eq_sub_bass:+.1f}")
                st.write(f"Bass: {music.mixer_params.eq_bass:+.1f}")
                st.write(f"Low Mid: {music.mixer_params.eq_low_mid:+.1f}")
                st.write(f"Mid: {music.mixer_params.eq_mid:+.1f}")
                st.write(f"High Mid: {music.mixer_params.eq_high_mid:+.1f}")
                st.write(f"Presence: {music.mixer_params.eq_presence:+.1f}")
                st.write(f"Air: {music.mixer_params.eq_air:+.1f}")

            with col2:
                st.write("**Dynamics**")
                st.write(f"Ratio: {music.mixer_params.compression_ratio:.1f}:1")
                st.write(f"Threshold: {music.mixer_params.compression_threshold:.1f} dB")
                st.write(f"Attack: {music.mixer_params.compression_attack:.1f} ms")
                st.write(f"Release: {music.mixer_params.compression_release:.1f} ms")

                st.write("\n**Reverb**")
                st.write(f"Decay: {music.mixer_params.reverb_decay:.1f}s")
                st.write(f"Predelay: {music.mixer_params.reverb_predelay:.0f}ms")
                st.write(f"Size: {music.mixer_params.reverb_size:.1%}")

        # Export
        st.subheader("Export to Logic Pro")

        output_name = st.text_input("Output filename:", value="my_song")

        if st.button("Export Automation"):
            with st.spinner("Exporting..."):
                result = brain.export_to_logic(music, output_name)
                st.success(f"Exported: {result['automation']}")

                # Provide download
                with open(result['automation']) as f:
                    automation_data = f.read()

                st.download_button(
                    label="Download Automation File",
                    data=automation_data,
                    file_name=f"{output_name}_automation.json",
                    mime="application/json"
                )

# ========== EMOTION EXPLORER MODE ==========
elif mode == "Emotion Explorer":
    st.header("Explore 216 Emotions")

    # Category selector
    categories = list(analyzer.emotion_data.keys())
    selected_category = st.selectbox("Select Category", categories)

    if selected_category:
        cat_data = analyzer.emotion_data[selected_category]

        st.write(f"**Description:** {cat_data.get('description', '')}")
        st.write(f"**Valence:** {cat_data.get('valence', 'neutral')}")

        # Sub-emotion selector
        sub_emotions = list(cat_data.get('sub_emotions', {}).keys())
        selected_sub = st.selectbox("Select Sub-Emotion", sub_emotions)

        if selected_sub:
            sub_data = cat_data['sub_emotions'][selected_sub]
            st.write(f"**Description:** {sub_data.get('description', '')}")

            # Sub-sub-emotion selector
            sub_sub_emotions = list(sub_data.get('sub_sub_emotions', {}).keys())
            selected_subsub = st.selectbox("Select Specific Emotion", sub_sub_emotions)

            if selected_subsub:
                subsub_data = sub_data['sub_sub_emotions'][selected_subsub]

                st.subheader(f"Emotion: {selected_subsub}")
                st.write(f"**Description:** {subsub_data.get('description', '')}")

                # Show intensity tiers
                st.write("**Intensity Tiers:**")
                for tier, words in subsub_data.get('intensity_tiers', {}).items():
                    st.write(f"*{tier.replace('_', ' ').title()}:* {', '.join(words)}")

                # Generate from this emotion
                if st.button("Generate from this emotion"):
                    emotion_text = f"{selected_subsub} {selected_sub} {selected_category}"
                    with st.spinner("Generating..."):
                        music = brain.generate_from_text(emotion_text)
                        st.session_state.music = music
                        st.success("Generated!")

# ========== DETAILED INTENT MODE ==========
elif mode == "Detailed Intent":
    st.header("Complete Song Intent")

    st.write("Build a complete three-phase intent for maximum control.")

    with st.expander("Phase 0: Core Wound/Desire", expanded=True):
        core_event = st.text_area("Core Event", placeholder="The inciting moment...")
        core_resistance = st.text_area("Core Resistance", placeholder="What's holding you back...")
        core_longing = st.text_area("Core Longing", placeholder="What you want to feel...")

    with st.expander("Phase 1: Emotional Intent"):
        mood_primary = st.text_input("Primary Mood", value="grief")
        mood_tension = st.slider("Secondary Tension", 0.0, 1.0, 0.3)
        vulnerability = st.select_slider("Vulnerability", ["Low", "Medium", "High"])
        narrative_arc = st.text_input("Narrative Arc", value="Slow Reveal")

    with st.expander("Phase 2: Technical Constraints"):
        key = st.text_input("Key", value="F")
        mode_select = st.selectbox("Mode", ["major", "minor", "dorian", "phrygian", "lydian", "mixolydian"])
        tempo = st.slider("Tempo (BPM)", 40, 200, 82)
        genre = st.text_input("Genre", value="lo-fi bedroom emo")
        rule_break = st.text_input("Rule to Break", value="HARMONY_ModalInterchange")
        justification = st.text_area("Justification", placeholder="Why break this rule?")

    if st.button("Generate from Complete Intent", type="primary"):
        # Build intent object
        from music_brain.session.intent_schema import CompleteSongIntent, SongRoot, SongIntent, TechnicalConstraints

        intent = CompleteSongIntent(
            song_root=SongRoot(
                core_event=core_event,
                core_resistance=core_resistance,
                core_longing=core_longing
            ),
            song_intent=SongIntent(
                mood_primary=mood_primary,
                mood_secondary_tension=mood_tension,
                vulnerability_scale=vulnerability,
                narrative_arc=narrative_arc
            ),
            technical_constraints=TechnicalConstraints(
                technical_key=key,
                technical_mode=mode_select,
                technical_tempo_range=(tempo, tempo),
                technical_genre=genre,
                technical_rule_to_break=rule_break,
                rule_breaking_justification=justification
            )
        )

        with st.spinner("Generating from complete intent..."):
            music = brain.generate_from_intent(intent)
            st.session_state.music = music
            st.success("Generated from complete intent!")

# Footer
st.divider()
st.markdown("*Philosophy: 'Interrogate Before Generate' - Every parameter justified by emotion*")
