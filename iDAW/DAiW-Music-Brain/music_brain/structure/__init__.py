"""
Structure Analysis - Chord, section, and progression analysis.

Analyze harmonic content, detect song sections, and work with
chord progressions for reharmonization and diagnosis.

Includes the Comprehensive Engine for therapy-based music generation.

Future integration notes:
- Therapy-based music generation workflows are implemented via comprehensive_engine
- Emotional mapping to harmonic structures available through progression.diagnose_progression
- Session-aware progression recommendations available via intent_processor
- All planned integrations are now complete and functional
"""

from music_brain.structure.chord import (
    analyze_chords,
    ChordProgression,
    Chord,
    detect_key,
)
from music_brain.structure.sections import (
    detect_sections,
    Section,
    SectionType,
)
from music_brain.structure.progression import (
    diagnose_progression,
    generate_reharmonizations,
    parse_progression_string,
)
from music_brain.structure.comprehensive_engine import (
    # Core classes
    AffectResult,
    AffectAnalyzer,
    TherapyState,
    HarmonyPlan,
    TherapySession,
    # Functions
    get_strategy,
    render_plan_to_midi,
    run_cli as run_therapy_cli,
)

__all__ = [
    # Chord analysis
    "analyze_chords",
    "ChordProgression",
    "Chord",
    "detect_key",
    # Section detection
    "detect_sections",
    "Section",
    "SectionType",
    # Progression tools
    "diagnose_progression",
    "generate_reharmonizations",
    "parse_progression_string",
    # Comprehensive Engine (Therapy)
    "AffectResult",
    "AffectAnalyzer",
    "TherapyState",
    "HarmonyPlan",
    "TherapySession",
    "get_strategy",
    "render_plan_to_midi",
    "run_therapy_cli",
]
