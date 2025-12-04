#!/usr/bin/env python3
"""
iDAWi Music Brain Bridge
Connects Python Music Brain to Tauri frontend via JSON IPC

This bridge provides a lightweight interface between the Tauri/Rust backend
and the Python-based Music Brain emotion and rule-breaking system.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

# Rule breaking effects database (simplified from DAiW-Music-Brain)
RULE_BREAKING_EFFECTS = {
    # Harmony Rules
    "HARMONY_AvoidTonicResolution": {
        "effect": "Creates unresolved yearning and emotional tension",
        "examples": ["Radiohead - 'Exit Music'", "Jeff Buckley - 'Hallelujah'"],
        "mixer_params": {"reverb": 0.7, "delay": 0.5},
        "emotions": ["grief", "yearning", "sadness", "longing"]
    },
    "HARMONY_ParallelFifths": {
        "effect": "Raw, primal power that bypasses conventional beauty",
        "examples": ["Nine Inch Nails", "Grunge genre"],
        "mixer_params": {"distortion": 0.4, "compression": 0.6},
        "emotions": ["anger", "rage", "frustration", "power"]
    },
    "HARMONY_ModalMixture": {
        "effect": "Bittersweet complexity, emotional ambiguity",
        "examples": ["The Beatles - 'Yesterday'", "Adele - 'Someone Like You'"],
        "mixer_params": {"reverb": 0.5},
        "emotions": ["melancholy", "nostalgia", "bittersweet"]
    },
    "HARMONY_ChromaticMediants": {
        "effect": "Dreamlike quality, unexpected emotional shifts",
        "examples": ["Film scores", "Max Richter"],
        "mixer_params": {"reverb": 0.8, "chorus": 0.3},
        "emotions": ["wonder", "mystery", "transcendence"]
    },

    # Rhythm Rules
    "RHYTHM_ConstantDisplacement": {
        "effect": "Anxiety, restlessness, inability to settle",
        "examples": ["Radiohead - 'Everything In Its Right Place'"],
        "mixer_params": {"pan_mod": 0.3},
        "emotions": ["anxiety", "fear", "unease", "paranoia"]
    },
    "RHYTHM_AgainstTheGrid": {
        "effect": "Human imperfection, emotional authenticity",
        "examples": ["D'Angelo - 'Voodoo'", "J Dilla beats"],
        "mixer_params": {"swing": 0.2, "humanize": 0.4},
        "emotions": ["soul", "authenticity", "groove"]
    },
    "RHYTHM_PolyrhythmicTension": {
        "effect": "Complexity, intellectual engagement, tension",
        "examples": ["Meshuggah", "Steve Reich"],
        "mixer_params": {},
        "emotions": ["complexity", "tension", "intellectual"]
    },

    # Production Rules
    "PRODUCTION_BuriedVocals": {
        "effect": "Dissociation, distance from emotion, dream-like",
        "examples": ["My Bloody Valentine", "Cocteau Twins"],
        "mixer_params": {"vocal_level": -6, "reverb": 0.9},
        "emotions": ["dissociation", "dreamlike", "ethereal"]
    },
    "PRODUCTION_LoFiHiFi": {
        "effect": "Memory, nostalgia, imperfect recollection",
        "examples": ["Bon Iver - 'For Emma'", "Grouper"],
        "mixer_params": {"bitcrush": 0.3, "filter_lp": 8000},
        "emotions": ["nostalgia", "memory", "longing"]
    },
    "PRODUCTION_ExtremeCompression": {
        "effect": "Claustrophobia, intensity, relentlessness",
        "examples": ["Death Grips", "Yeezus-era Kanye"],
        "mixer_params": {"compression": 0.9, "limiting": 0.8},
        "emotions": ["intensity", "aggression", "relentless"]
    },
    "PRODUCTION_PitchImperfection": {
        "effect": "Emotional honesty, vulnerability",
        "examples": ["Bon Iver", "James Blake"],
        "mixer_params": {"pitch_drift": 0.02},
        "emotions": ["vulnerability", "honesty", "raw"]
    },

    # Arrangement Rules
    "ARRANGEMENT_BuriedMelody": {
        "effect": "Hidden emotional content, discovery",
        "examples": ["Sigur Rós", "Ambient music"],
        "mixer_params": {"melody_level": -8, "pad_level": 0},
        "emotions": ["mystery", "discovery", "subtle"]
    },
    "ARRANGEMENT_EmptySpace": {
        "effect": "Isolation, focus, weight to every note",
        "examples": ["Billie Eilish", "Frank Ocean - 'Blonde'"],
        "mixer_params": {"density": 0.2},
        "emotions": ["isolation", "loneliness", "focus"]
    },
    "ARRANGEMENT_DynamicInversion": {
        "effect": "Subverted expectations, emotional surprise",
        "examples": ["Pixies - 'Quiet Loud'"],
        "mixer_params": {},
        "emotions": ["surprise", "contrast", "drama"]
    },
}

# Emotion to rule mapping
EMOTION_RULE_MAPPING = {
    "grief": ["HARMONY_AvoidTonicResolution", "ARRANGEMENT_EmptySpace", "PRODUCTION_BuriedVocals"],
    "yearning": ["HARMONY_AvoidTonicResolution", "PRODUCTION_LoFiHiFi", "HARMONY_ModalMixture"],
    "sadness": ["HARMONY_AvoidTonicResolution", "HARMONY_ModalMixture", "ARRANGEMENT_EmptySpace"],
    "loneliness": ["ARRANGEMENT_EmptySpace", "PRODUCTION_BuriedVocals", "HARMONY_AvoidTonicResolution"],
    "melancholy": ["HARMONY_ModalMixture", "PRODUCTION_LoFiHiFi", "HARMONY_ChromaticMediants"],
    "anger": ["HARMONY_ParallelFifths", "PRODUCTION_ExtremeCompression", "RHYTHM_ConstantDisplacement"],
    "rage": ["HARMONY_ParallelFifths", "PRODUCTION_ExtremeCompression", "ARRANGEMENT_DynamicInversion"],
    "frustration": ["RHYTHM_ConstantDisplacement", "HARMONY_ParallelFifths", "PRODUCTION_ExtremeCompression"],
    "fear": ["RHYTHM_ConstantDisplacement", "HARMONY_ChromaticMediants", "PRODUCTION_BuriedVocals"],
    "anxiety": ["RHYTHM_ConstantDisplacement", "RHYTHM_PolyrhythmicTension", "PRODUCTION_ExtremeCompression"],
    "terror": ["RHYTHM_ConstantDisplacement", "HARMONY_ChromaticMediants", "PRODUCTION_ExtremeCompression"],
    "joy": ["RHYTHM_AgainstTheGrid", "HARMONY_ModalMixture", "ARRANGEMENT_DynamicInversion"],
    "happiness": ["RHYTHM_AgainstTheGrid", "HARMONY_ModalMixture"],
    "contentment": ["ARRANGEMENT_EmptySpace", "PRODUCTION_PitchImperfection"],
    "love": ["PRODUCTION_PitchImperfection", "HARMONY_ModalMixture", "ARRANGEMENT_BuriedMelody"],
    "passion": ["RHYTHM_AgainstTheGrid", "ARRANGEMENT_DynamicInversion", "PRODUCTION_ExtremeCompression"],
    "hope": ["HARMONY_ModalMixture", "HARMONY_ChromaticMediants", "ARRANGEMENT_DynamicInversion"],
    "nostalgia": ["PRODUCTION_LoFiHiFi", "HARMONY_ModalMixture", "PRODUCTION_BuriedVocals"],
}

# Available emotions with categories
EMOTIONS_DATABASE = [
    # Sadness spectrum
    {"name": "Grief", "category": "Sadness", "intensity": 0.9},
    {"name": "Yearning", "category": "Sadness", "intensity": 0.7},
    {"name": "Melancholy", "category": "Sadness", "intensity": 0.6},
    {"name": "Loneliness", "category": "Sadness", "intensity": 0.7},
    {"name": "Despair", "category": "Sadness", "intensity": 1.0},
    {"name": "Sorrow", "category": "Sadness", "intensity": 0.8},
    # Joy spectrum
    {"name": "Happiness", "category": "Joy", "intensity": 0.7},
    {"name": "Euphoria", "category": "Joy", "intensity": 1.0},
    {"name": "Contentment", "category": "Joy", "intensity": 0.5},
    {"name": "Bliss", "category": "Joy", "intensity": 0.9},
    {"name": "Elation", "category": "Joy", "intensity": 0.8},
    {"name": "Delight", "category": "Joy", "intensity": 0.6},
    # Anger spectrum
    {"name": "Rage", "category": "Anger", "intensity": 1.0},
    {"name": "Frustration", "category": "Anger", "intensity": 0.6},
    {"name": "Resentment", "category": "Anger", "intensity": 0.7},
    {"name": "Fury", "category": "Anger", "intensity": 0.9},
    {"name": "Irritation", "category": "Anger", "intensity": 0.4},
    {"name": "Wrath", "category": "Anger", "intensity": 0.95},
    # Fear spectrum
    {"name": "Terror", "category": "Fear", "intensity": 1.0},
    {"name": "Anxiety", "category": "Fear", "intensity": 0.7},
    {"name": "Dread", "category": "Fear", "intensity": 0.8},
    {"name": "Panic", "category": "Fear", "intensity": 0.9},
    {"name": "Unease", "category": "Fear", "intensity": 0.5},
    {"name": "Paranoia", "category": "Fear", "intensity": 0.8},
    # Love spectrum
    {"name": "Devotion", "category": "Love", "intensity": 0.8},
    {"name": "Passion", "category": "Love", "intensity": 0.9},
    {"name": "Tenderness", "category": "Love", "intensity": 0.6},
    {"name": "Adoration", "category": "Love", "intensity": 0.85},
    {"name": "Longing", "category": "Love", "intensity": 0.7},
    {"name": "Desire", "category": "Love", "intensity": 0.8},
    # Hope spectrum
    {"name": "Optimism", "category": "Hope", "intensity": 0.7},
    {"name": "Faith", "category": "Hope", "intensity": 0.8},
    {"name": "Anticipation", "category": "Hope", "intensity": 0.6},
    {"name": "Trust", "category": "Hope", "intensity": 0.65},
    {"name": "Wonder", "category": "Hope", "intensity": 0.75},
    {"name": "Aspiration", "category": "Hope", "intensity": 0.7},
]


def suggest_rule_break(emotion: str) -> List[Dict[str, Any]]:
    """
    Suggest rules to break based on the given emotion.

    Args:
        emotion: The core emotion (e.g., "grief", "anger", "joy")

    Returns:
        List of rule break suggestions with effects and mixer parameters
    """
    emotion_lower = emotion.lower()

    # Get rules for this emotion
    rule_ids = EMOTION_RULE_MAPPING.get(emotion_lower, [])

    suggestions = []
    for rule_id in rule_ids:
        if rule_id in RULE_BREAKING_EFFECTS:
            rule_data = RULE_BREAKING_EFFECTS[rule_id]
            suggestions.append({
                "rule": rule_id,
                "effect": rule_data["effect"],
                "examples": rule_data["examples"],
                "mixer_params": rule_data.get("mixer_params", {}),
            })

    # If no specific rules found, return generic suggestions
    if not suggestions:
        suggestions = [
            {
                "rule": "HARMONY_ModalMixture",
                "effect": "Bittersweet complexity, emotional ambiguity",
                "examples": ["The Beatles - 'Yesterday'"],
                "mixer_params": {"reverb": 0.5},
            },
            {
                "rule": "ARRANGEMENT_EmptySpace",
                "effect": "Isolation, focus, weight to every note",
                "examples": ["Billie Eilish", "Frank Ocean"],
                "mixer_params": {"density": 0.2},
            },
        ]

    return suggestions


def process_intent(intent_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a complete song intent and return musical parameters.

    Args:
        intent_data: Dictionary with song_root, song_intent, technical_constraints

    Returns:
        Dictionary with harmony, tempo, key, and mixer parameters
    """
    song_root = intent_data.get("song_root", {})
    song_intent = intent_data.get("song_intent", {})
    tech = intent_data.get("technical_constraints", {})

    core_emotion = song_root.get("core_emotion", "neutral")
    vulnerability = song_intent.get("vulnerability_scale", 5)
    narrative_arc = song_intent.get("narrative_arc", "ascending")
    rule_to_break = tech.get("rule_to_break")

    # Determine key based on emotion
    emotion_keys = {
        "grief": "A minor",
        "sadness": "D minor",
        "yearning": "E minor",
        "anger": "F# minor",
        "fear": "B minor",
        "joy": "G major",
        "love": "F major",
        "hope": "C major",
    }
    key = emotion_keys.get(core_emotion.lower(), "C major")

    # Determine tempo based on emotion and vulnerability
    base_tempos = {
        "grief": 60,
        "sadness": 70,
        "yearning": 75,
        "anger": 140,
        "fear": 100,
        "joy": 120,
        "love": 85,
        "hope": 110,
    }
    base_tempo = base_tempos.get(core_emotion.lower(), 100)
    tempo = base_tempo + (vulnerability - 5) * 3  # Adjust by vulnerability

    # Generate chord progression based on emotion and narrative arc
    progressions = {
        ("sadness", "ascending"): ["i", "VI", "III", "VII"],
        ("sadness", "descending"): ["i", "iv", "v", "i"],
        ("grief", "ascending"): ["i", "bVI", "bIII", "bVII"],
        ("grief", "circular"): ["i", "bVI", "IV", "bVII"],
        ("anger", "ascending"): ["i", "bVII", "bVI", "V"],
        ("joy", "ascending"): ["I", "V", "vi", "IV"],
        ("love", "circular"): ["I", "vi", "IV", "V"],
        ("hope", "ascending"): ["I", "V", "vi", "IV"],
    }

    prog_key = (core_emotion.lower(), narrative_arc)
    chords = progressions.get(prog_key, ["I", "IV", "V", "I"])

    # Apply mixer parameters from rule breaking
    mixer_params = {}
    if rule_to_break and rule_to_break in RULE_BREAKING_EFFECTS:
        mixer_params = RULE_BREAKING_EFFECTS[rule_to_break].get("mixer_params", {})

    # Add vulnerability-based adjustments
    mixer_params["reverb"] = mixer_params.get("reverb", 0.3) + (vulnerability / 20)

    return {
        "harmony": chords,
        "tempo": tempo,
        "key": key,
        "mixer_params": mixer_params,
    }


def get_emotions() -> List[Dict[str, Any]]:
    """Return the full list of available emotions."""
    return EMOTIONS_DATABASE


def handle_command(command: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle a command from the Tauri frontend.

    Args:
        command: The command name
        args: Command arguments

    Returns:
        Response dictionary with success status and data/error
    """
    try:
        if command == "suggest_rule_break":
            emotion = args.get("emotion", "grief")
            suggestions = suggest_rule_break(emotion)
            return {
                "success": True,
                "data": suggestions
            }

        elif command == "process_intent":
            intent = args.get("intent", {})
            result = process_intent(intent)
            return {
                "success": True,
                "data": result
            }

        elif command == "get_emotions":
            emotions = get_emotions()
            return {
                "success": True,
                "data": emotions
            }

        else:
            return {
                "success": False,
                "error": f"Unknown command: {command}"
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def main():
    """Main entry point for the bridge script."""
    try:
        # Read input from stdin (Tauri sends JSON)
        input_data = json.loads(sys.stdin.read())
        command = input_data.get("command")
        args = input_data.get("args", {})

        result = handle_command(command, args)
        print(json.dumps(result))

    except json.JSONDecodeError as e:
        print(json.dumps({
            "success": False,
            "error": f"Invalid JSON input: {str(e)}"
        }))

    except Exception as e:
        print(json.dumps({
            "success": False,
            "error": f"Bridge error: {str(e)}"
        }))


if __name__ == "__main__":
    main()
