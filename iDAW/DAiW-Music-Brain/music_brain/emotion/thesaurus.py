"""
DAiW Emotion Thesaurus

A comprehensive 6×6×6 emotion taxonomy with V-A-D (Valence-Arousal-Dominance) coordinates.
Follows the 6×6×6 grid convention (216 total nodes):
- Valence: 6 levels (-1 to +1)
- Arousal: 6 levels (-1 to +1)
- Dominance: 6 levels (-1 to +1)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Literal
from enum import Enum
import math


class EmotionCategory(str, Enum):
    """Base emotion categories."""
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    NEUTRAL = "neutral"


class MusicalMode(str, Enum):
    """Musical modes for emotion mapping."""
    MAJOR = "major"
    MINOR = "minor"
    DORIAN = "dorian"
    PHRYGIAN = "phrygian"
    LYDIAN = "lydian"
    MIXOLYDIAN = "mixolydian"
    AEOLIAN = "aeolian"
    LOCRIAN = "locrian"


class DynamicLevel(str, Enum):
    """Musical dynamic levels."""
    PP = "pp"  # pianissimo
    P = "p"    # piano
    MP = "mp"  # mezzo-piano
    MF = "mf"  # mezzo-forte
    F = "f"    # forte
    FF = "ff"  # fortissimo


class Articulation(str, Enum):
    """Musical articulation styles."""
    LEGATO = "legato"
    STACCATO = "staccato"
    MARCATO = "marcato"
    TENUTO = "tenuto"


@dataclass
class VADCoordinates:
    """
    V-A-D coordinates for emotion mapping.
    
    Attributes:
        valence: Negative to positive feeling (-1 to +1)
        arousal: Calm to excited (-1 to +1)
        dominance: Submissive to dominant (-1 to +1)
    """
    valence: float
    arousal: float
    dominance: float
    
    def __post_init__(self):
        """Clamp values to valid range."""
        self.valence = max(-1.0, min(1.0, self.valence))
        self.arousal = max(-1.0, min(1.0, self.arousal))
        self.dominance = max(-1.0, min(1.0, self.dominance))
    
    def to_grid_position(self) -> Tuple[int, int, int]:
        """Get grid position for V-A-D coordinates (0-5 for each dimension)."""
        def normalize(value: float) -> int:
            return min(5, int((value + 1) / 2 * 5.99))
        return (normalize(self.valence), normalize(self.arousal), normalize(self.dominance))
    
    def distance_to(self, other: "VADCoordinates") -> float:
        """Calculate Euclidean distance to another VAD coordinate."""
        return math.sqrt(
            (self.valence - other.valence) ** 2 +
            (self.arousal - other.arousal) ** 2 +
            (self.dominance - other.dominance) ** 2
        )


@dataclass
class MusicalCharacteristics:
    """
    Musical characteristics derived from emotion.
    
    Attributes:
        tempo_range: Tempo range in BPM (min, max)
        mode: Musical mode
        dynamics: Dynamic level
        articulation: Articulation style
        harmonic_complexity: Complexity of harmony (0-1)
        rhythmic_density: Density of rhythm (0-1)
        instruments: Suggested instruments
    """
    tempo_range: Tuple[int, int]
    mode: MusicalMode
    dynamics: DynamicLevel
    articulation: Articulation
    harmonic_complexity: float
    rhythmic_density: float
    instruments: List[str] = field(default_factory=list)


@dataclass
class EmotionNode:
    """
    Complete emotion node with all properties.
    
    Attributes:
        name: Unique emotion name
        vad: V-A-D coordinates
        music: Musical characteristics
        category: Category of emotion
        intensity_level: Intensity level (1-6)
        synonyms: Related emotion synonyms
    """
    name: str
    vad: VADCoordinates
    music: MusicalCharacteristics
    category: EmotionCategory
    intensity_level: int  # 1-6
    synonyms: List[str] = field(default_factory=list)


def _arousal_to_tempo(arousal: float) -> Tuple[int, int]:
    """Map arousal to tempo range."""
    # -1 arousal = 40-60 BPM, +1 arousal = 140-180 BPM
    base_tempo = 60 + (arousal + 1) * 50
    return (round(base_tempo - 10), round(base_tempo + 10))


def _valence_to_mode(valence: float) -> MusicalMode:
    """Map valence to musical mode."""
    if valence > 0.5:
        return MusicalMode.MAJOR
    elif valence > 0.2:
        return MusicalMode.LYDIAN
    elif valence > -0.2:
        return MusicalMode.MIXOLYDIAN
    elif valence > -0.5:
        return MusicalMode.DORIAN
    elif valence > -0.8:
        return MusicalMode.AEOLIAN
    else:
        return MusicalMode.PHRYGIAN


def _dominance_to_dynamics(dominance: float) -> DynamicLevel:
    """Map dominance to dynamics."""
    if dominance > 0.6:
        return DynamicLevel.FF
    elif dominance > 0.3:
        return DynamicLevel.F
    elif dominance > 0:
        return DynamicLevel.MF
    elif dominance > -0.3:
        return DynamicLevel.MP
    elif dominance > -0.6:
        return DynamicLevel.P
    else:
        return DynamicLevel.PP


def vad_to_musical_characteristics(vad: VADCoordinates) -> MusicalCharacteristics:
    """
    Generate musical characteristics from V-A-D coordinates.
    
    Args:
        vad: V-A-D coordinates
        
    Returns:
        MusicalCharacteristics object
    """
    valence, arousal, dominance = vad.valence, vad.arousal, vad.dominance
    
    # Articulation based on arousal and dominance combination
    if arousal > 0.5 and dominance > 0:
        articulation = Articulation.MARCATO
    elif arousal > 0.3:
        articulation = Articulation.STACCATO
    elif arousal < -0.3:
        articulation = Articulation.LEGATO
    else:
        articulation = Articulation.TENUTO
    
    # Harmonic complexity increases with negative valence and high arousal
    harmonic_complexity = max(0, min(1, 0.3 + (arousal + 1) * 0.2 - valence * 0.3))
    
    # Rhythmic density increases with arousal
    rhythmic_density = max(0, min(1, 0.3 + (arousal + 1) * 0.35))
    
    # Instrument selection based on emotion category
    instruments: List[str] = []
    if valence > 0.3:
        instruments.extend(["piano", "strings", "brass"])
    elif valence < -0.3:
        instruments.extend(["cello", "violin", "oboe"])
    if arousal > 0.5:
        instruments.extend(["drums", "percussion"])
    if dominance > 0.3:
        instruments.extend(["brass", "timpani"])
    elif dominance < -0.3:
        instruments.extend(["flute", "harp"])
    
    # Remove duplicates while preserving order
    seen = set()
    unique_instruments = []
    for inst in instruments:
        if inst not in seen:
            seen.add(inst)
            unique_instruments.append(inst)
    
    return MusicalCharacteristics(
        tempo_range=_arousal_to_tempo(arousal),
        mode=_valence_to_mode(valence),
        dynamics=_dominance_to_dynamics(dominance),
        articulation=articulation,
        harmonic_complexity=harmonic_complexity,
        rhythmic_density=rhythmic_density,
        instruments=unique_instruments,
    )


def _create_emotion_node(
    name: str,
    valence: float,
    arousal: float,
    dominance: float,
    category: EmotionCategory,
    intensity_level: int,
    synonyms: List[str],
) -> EmotionNode:
    """Helper to create an emotion node."""
    vad = VADCoordinates(valence, arousal, dominance)
    return EmotionNode(
        name=name,
        vad=vad,
        music=vad_to_musical_characteristics(vad),
        category=category,
        intensity_level=intensity_level,
        synonyms=synonyms,
    )


# Core emotion nodes following the 6×6×6 grid convention
EMOTION_NODES: Dict[str, EmotionNode] = {
    # === JOY FAMILY ===
    "ecstatic": _create_emotion_node(
        "Ecstatic", 1.0, 1.0, 0.8, EmotionCategory.JOY, 6,
        ["euphoric", "elated", "overjoyed", "thrilled"]
    ),
    "joyful": _create_emotion_node(
        "Joyful", 0.8, 0.7, 0.5, EmotionCategory.JOY, 5,
        ["happy", "delighted", "cheerful", "glad"]
    ),
    "content": _create_emotion_node(
        "Content", 0.6, 0.2, 0.3, EmotionCategory.JOY, 3,
        ["satisfied", "pleased", "comfortable", "at ease"]
    ),
    "serene": _create_emotion_node(
        "Serene", 0.5, -0.5, 0.2, EmotionCategory.JOY, 2,
        ["peaceful", "calm", "tranquil", "relaxed"]
    ),
    "hopeful": _create_emotion_node(
        "Hopeful", 0.6, 0.4, 0.4, EmotionCategory.JOY, 4,
        ["optimistic", "expectant", "encouraged", "anticipating"]
    ),
    
    # === SADNESS FAMILY ===
    "grieving": _create_emotion_node(
        "Grieving", -0.9, 0.2, -0.7, EmotionCategory.SADNESS, 6,
        ["mourning", "bereaved", "heartbroken", "devastated"]
    ),
    "melancholy": _create_emotion_node(
        "Melancholy", -0.6, -0.3, -0.4, EmotionCategory.SADNESS, 4,
        ["wistful", "pensive", "nostalgic", "bittersweet"]
    ),
    "lonely": _create_emotion_node(
        "Lonely", -0.5, -0.2, -0.5, EmotionCategory.SADNESS, 4,
        ["isolated", "abandoned", "forsaken", "solitary"]
    ),
    "yearning": _create_emotion_node(
        "Yearning", -0.4, 0.3, -0.3, EmotionCategory.SADNESS, 4,
        ["longing", "pining", "craving", "aching"]
    ),
    "despairing": _create_emotion_node(
        "Despairing", -1.0, 0.1, -0.9, EmotionCategory.SADNESS, 6,
        ["hopeless", "defeated", "dejected", "forlorn"]
    ),
    
    # === ANGER FAMILY ===
    "furious": _create_emotion_node(
        "Furious", -0.8, 1.0, 0.8, EmotionCategory.ANGER, 6,
        ["enraged", "livid", "incensed", "wrathful"]
    ),
    "angry": _create_emotion_node(
        "Angry", -0.6, 0.7, 0.6, EmotionCategory.ANGER, 5,
        ["mad", "upset", "irate", "indignant"]
    ),
    "frustrated": _create_emotion_node(
        "Frustrated", -0.5, 0.5, 0.2, EmotionCategory.ANGER, 4,
        ["annoyed", "exasperated", "irritated", "aggravated"]
    ),
    "resentful": _create_emotion_node(
        "Resentful", -0.6, 0.4, 0.3, EmotionCategory.ANGER, 4,
        ["bitter", "grudging", "spiteful", "vengeful"]
    ),
    
    # === FEAR FAMILY ===
    "terrified": _create_emotion_node(
        "Terrified", -0.9, 0.9, -0.8, EmotionCategory.FEAR, 6,
        ["petrified", "horrified", "panicked", "terror-stricken"]
    ),
    "anxious": _create_emotion_node(
        "Anxious", -0.5, 0.6, -0.4, EmotionCategory.FEAR, 4,
        ["worried", "nervous", "apprehensive", "uneasy"]
    ),
    "dread": _create_emotion_node(
        "Dread", -0.7, 0.5, -0.6, EmotionCategory.FEAR, 5,
        ["foreboding", "apprehension", "trepidation", "dismay"]
    ),
    "vulnerable": _create_emotion_node(
        "Vulnerable", -0.3, 0.2, -0.7, EmotionCategory.FEAR, 3,
        ["exposed", "defenseless", "unprotected", "fragile"]
    ),
    
    # === SURPRISE FAMILY ===
    "amazed": _create_emotion_node(
        "Amazed", 0.5, 0.8, 0.0, EmotionCategory.SURPRISE, 5,
        ["astonished", "astounded", "awestruck", "stunned"]
    ),
    "surprised": _create_emotion_node(
        "Surprised", 0.2, 0.7, 0.0, EmotionCategory.SURPRISE, 4,
        ["startled", "shocked", "taken aback", "caught off guard"]
    ),
    "curious": _create_emotion_node(
        "Curious", 0.3, 0.5, 0.2, EmotionCategory.SURPRISE, 3,
        ["intrigued", "inquisitive", "interested", "fascinated"]
    ),
    
    # === DISGUST FAMILY ===
    "revolted": _create_emotion_node(
        "Revolted", -0.8, 0.6, 0.4, EmotionCategory.DISGUST, 6,
        ["repulsed", "nauseated", "sickened", "appalled"]
    ),
    "contemptuous": _create_emotion_node(
        "Contemptuous", -0.5, 0.3, 0.6, EmotionCategory.DISGUST, 4,
        ["disdainful", "scornful", "dismissive", "derisive"]
    ),
    
    # === NEUTRAL ===
    "neutral": _create_emotion_node(
        "Neutral", 0.0, 0.0, 0.0, EmotionCategory.NEUTRAL, 1,
        ["indifferent", "detached", "unmoved", "impassive"]
    ),
    "focused": _create_emotion_node(
        "Focused", 0.1, 0.3, 0.4, EmotionCategory.NEUTRAL, 3,
        ["concentrated", "attentive", "absorbed", "engaged"]
    ),
}


def find_emotion_by_name(name: str) -> Optional[EmotionNode]:
    """Find emotion node by name (case-insensitive)."""
    return EMOTION_NODES.get(name.lower())


def find_emotion_by_synonym(synonym: str) -> Optional[EmotionNode]:
    """Find emotion by synonym."""
    search_term = synonym.lower()
    for emotion in EMOTION_NODES.values():
        if any(s.lower() == search_term for s in emotion.synonyms):
            return emotion
    return None


def get_emotions_by_category(category: EmotionCategory) -> List[EmotionNode]:
    """Get emotions by category."""
    return [e for e in EMOTION_NODES.values() if e.category == category]


def get_emotions_by_intensity(level: int) -> List[EmotionNode]:
    """Get emotions by intensity level (1-6)."""
    return [e for e in EMOTION_NODES.values() if e.intensity_level == level]


def find_closest_emotion(vad: VADCoordinates) -> EmotionNode:
    """Find the closest emotion node to given V-A-D coordinates."""
    closest = EMOTION_NODES["neutral"]
    min_distance = float("inf")
    
    for emotion in EMOTION_NODES.values():
        distance = vad.distance_to(emotion.vad)
        if distance < min_distance:
            min_distance = distance
            closest = emotion
    
    return closest


def interpolate_emotions(
    emotion1: EmotionNode,
    emotion2: EmotionNode,
    t: float,  # 0 to 1
) -> VADCoordinates:
    """Interpolate between two emotion nodes."""
    t = max(0, min(1, t))
    return VADCoordinates(
        valence=emotion1.vad.valence + (emotion2.vad.valence - emotion1.vad.valence) * t,
        arousal=emotion1.vad.arousal + (emotion2.vad.arousal - emotion1.vad.arousal) * t,
        dominance=emotion1.vad.dominance + (emotion2.vad.dominance - emotion1.vad.dominance) * t,
    )


def get_all_emotion_names() -> List[str]:
    """Get all emotion names."""
    return [e.name for e in EMOTION_NODES.values()]


__all__ = [
    "EmotionCategory",
    "MusicalMode",
    "DynamicLevel",
    "Articulation",
    "VADCoordinates",
    "MusicalCharacteristics",
    "EmotionNode",
    "EMOTION_NODES",
    "vad_to_musical_characteristics",
    "find_emotion_by_name",
    "find_emotion_by_synonym",
    "get_emotions_by_category",
    "get_emotions_by_intensity",
    "find_closest_emotion",
    "interpolate_emotions",
    "get_all_emotion_names",
]
