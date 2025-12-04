"""
iDAWi Music Brain
Full-featured Python music intelligence toolkit for emotion-driven music production.

This package provides:
- Groove extraction and application
- Chord and progression analysis
- Intent-based music generation
- Rule-breaking suggestions for emotional expression
- DAW integration (Logic Pro, Pro Tools, Reaper, FL Studio)
- Multi-AI collaboration tools
"""

__version__ = "0.2.0"
__author__ = "Sean Burdges"

from pathlib import Path

# Package root directory
PACKAGE_ROOT = Path(__file__).parent
DATA_ROOT = PACKAGE_ROOT.parent.parent / "data"

# Lazy imports for better startup performance
def __getattr__(name):
    """Lazy import modules on first access."""

    # Core modules
    if name == "GrooveExtractor":
        from .groove.extractor import GrooveExtractor
        return GrooveExtractor
    elif name == "GrooveApplicator":
        from .groove.applicator import GrooveApplicator
        return GrooveApplicator
    elif name == "GrooveEngine":
        from .groove.groove_engine import GrooveEngine
        return GrooveEngine

    # Structure modules
    elif name == "ChordAnalyzer":
        from .structure.chord import ChordAnalyzer
        return ChordAnalyzer
    elif name == "ProgressionAnalyzer":
        from .structure.progression import ProgressionAnalyzer
        return ProgressionAnalyzer

    # Session modules
    elif name == "IntentSchema":
        from .session.intent_schema import IntentSchema
        return IntentSchema
    elif name == "IntentProcessor":
        from .session.intent_processor import IntentProcessor
        return IntentProcessor
    elif name == "Interrogator":
        from .session.interrogator import Interrogator
        return Interrogator

    # Audio modules
    elif name == "AudioAnalyzer":
        from .audio.analyzer import AudioAnalyzer
        return AudioAnalyzer
    elif name == "FeelAnalyzer":
        from .audio.feel import FeelAnalyzer
        return FeelAnalyzer

    # Bridge functions (for Tauri IPC)
    elif name in ("suggest_rule_break", "process_intent", "get_emotions",
                  "RULE_BREAKING_EFFECTS", "EMOTION_RULE_MAPPING", "EMOTIONS_DATABASE"):
        import sys
        sys.path.insert(0, str(PACKAGE_ROOT.parent))
        try:
            from bridge import (
                suggest_rule_break,
                process_intent,
                get_emotions,
                RULE_BREAKING_EFFECTS,
                EMOTION_RULE_MAPPING,
                EMOTIONS_DATABASE,
            )
            return {
                "suggest_rule_break": suggest_rule_break,
                "process_intent": process_intent,
                "get_emotions": get_emotions,
                "RULE_BREAKING_EFFECTS": RULE_BREAKING_EFFECTS,
                "EMOTION_RULE_MAPPING": EMOTION_RULE_MAPPING,
                "EMOTIONS_DATABASE": EMOTIONS_DATABASE,
            }[name]
        except ImportError:
            # Fallback if bridge not available
            if name == "suggest_rule_break":
                return lambda emotion: []
            elif name == "process_intent":
                return lambda intent: {"harmony": ["I", "IV", "V", "I"], "tempo": 120, "key": "C major", "mixer_params": {}}
            elif name == "get_emotions":
                return lambda: []
            else:
                return {}

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# Subpackage exports
__all__ = [
    # Version info
    "__version__",
    "__author__",
    "PACKAGE_ROOT",
    "DATA_ROOT",

    # Groove
    "GrooveExtractor",
    "GrooveApplicator",
    "GrooveEngine",

    # Structure
    "ChordAnalyzer",
    "ProgressionAnalyzer",

    # Session
    "IntentSchema",
    "IntentProcessor",
    "Interrogator",

    # Audio
    "AudioAnalyzer",
    "FeelAnalyzer",

    # Bridge functions
    "suggest_rule_break",
    "process_intent",
    "get_emotions",
    "RULE_BREAKING_EFFECTS",
    "EMOTION_RULE_MAPPING",
    "EMOTIONS_DATABASE",
]
