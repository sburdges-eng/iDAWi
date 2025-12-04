"""
Text-to-Emotion Analyzer
Sophisticated mapping from natural language to emotional states.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from music_brain.data.emotional_mapping import EmotionalState


@dataclass
class EmotionMatch:
    """A potential emotion match from text."""
    emotion: str
    category: str
    sub_emotion: str
    sub_sub_emotion: str
    confidence: float
    keywords_matched: List[str]


class TextEmotionAnalyzer:
    """
    Analyzes text and maps to the 216-node emotion thesaurus.
    Uses keyword matching across all emotion files.
    """

    def __init__(self):
        self.emotion_data = self._load_all_emotions()
        self.keyword_map = self._build_keyword_map()

    def _load_all_emotions(self) -> Dict:
        """Load all emotion category JSON files."""
        emotions = {}
        data_dir = Path(__file__).parent.parent / "data"

        for json_file in data_dir.glob("*.json"):
            if json_file.stem in ["sad", "joy", "anger", "fear", "surprise", "disgust"]:
                with open(json_file) as f:
                    emotions[json_file.stem] = json.load(f)

        return emotions

    def _build_keyword_map(self) -> Dict[str, List[Tuple[str, str, str]]]:
        """
        Build reverse index: keyword -> [(category, sub_emotion, sub_sub_emotion), ...]
        """
        keyword_map = {}

        for category, cat_data in self.emotion_data.items():
            for sub_name, sub_data in cat_data.get("sub_emotions", {}).items():
                for subsub_name, subsub_data in sub_data.get("sub_sub_emotions", {}).items():
                    # Add all intensity tier words as keywords
                    for tier, words in subsub_data.get("intensity_tiers", {}).items():
                        for word in words:
                            word_lower = word.lower()
                            if word_lower not in keyword_map:
                                keyword_map[word_lower] = []
                            keyword_map[word_lower].append((
                                category,
                                sub_name,
                                subsub_name
                            ))

        return keyword_map

    def analyze(self, text: str) -> List[EmotionMatch]:
        """
        Analyze text and return ranked emotion matches.

        Args:
            text: Natural language emotional description

        Returns:
            List of EmotionMatch objects, sorted by confidence
        """
        text_lower = text.lower()
        words = text_lower.split()

        # Track matches
        matches = {}  # (category, sub, subsub) -> (count, keywords)

        for word in words:
            if word in self.keyword_map:
                for category, sub, subsub in self.keyword_map[word]:
                    key = (category, sub, subsub)
                    if key not in matches:
                        matches[key] = (0, [])
                    count, keywords = matches[key]
                    matches[key] = (count + 1, keywords + [word])

        # Convert to EmotionMatch objects
        results = []
        for (category, sub, subsub), (count, keywords) in matches.items():
            # Calculate confidence based on keyword matches
            confidence = min(1.0, count / 3.0)  # 3+ keywords = 100% confidence

            results.append(EmotionMatch(
                emotion=subsub,
                category=category,
                sub_emotion=sub,
                sub_sub_emotion=subsub,
                confidence=confidence,
                keywords_matched=keywords
            ))

        # Sort by confidence
        results.sort(key=lambda m: m.confidence, reverse=True)

        return results

    def text_to_emotional_state(
        self,
        text: str,
        default_valence: float = 0.0,
        default_arousal: float = 0.5
    ) -> EmotionalState:
        """
        Convert text directly to EmotionalState.

        Args:
            text: Natural language description
            default_valence: Fallback if no match
            default_arousal: Fallback if no match

        Returns:
            EmotionalState object
        """
        matches = self.analyze(text)

        if not matches:
            return EmotionalState(
                valence=default_valence,
                arousal=default_arousal,
                primary_emotion="neutral"
            )

        # Use best match
        best_match = matches[0]

        # Get valence/arousal from category
        valence_map = {
            "sad": -0.7,
            "joy": 0.8,
            "anger": -0.6,
            "fear": -0.7,
            "surprise": 0.2,
            "disgust": -0.5
        }

        arousal_map = {
            "sad": 0.3,
            "joy": 0.7,
            "anger": 0.9,
            "fear": 0.8,
            "surprise": 0.8,
            "disgust": 0.5
        }

        valence = valence_map.get(best_match.category, 0.0)
        arousal = arousal_map.get(best_match.category, 0.5)

        return EmotionalState(
            valence=valence,
            arousal=arousal,
            primary_emotion=best_match.sub_sub_emotion,
            secondary_emotions=[m.sub_sub_emotion for m in matches[1:3]]
        )


# Example usage
if __name__ == "__main__":
    analyzer = TextEmotionAnalyzer()

    test_texts = [
        "I feel deeply bereaved and heartbroken",
        "Explosive rage and fury",
        "Anxious and terrified",
        "Joyful and euphoric",
        "Disgusted and repulsed"
    ]

    print("=" * 70)
    print("TEXT-TO-EMOTION ANALYSIS")
    print("=" * 70)

    for text in test_texts:
        print(f"\nText: \"{text}\"")
        matches = analyzer.analyze(text)

        if matches:
            print(f"\n   Top Matches:")
            for i, match in enumerate(matches[:3], 1):
                print(f"   {i}. {match.emotion} ({match.category}/{match.sub_emotion})")
                print(f"      Confidence: {match.confidence:.1%}")
                print(f"      Keywords: {', '.join(match.keywords_matched)}")

        state = analyzer.text_to_emotional_state(text)
        print(f"\n   Emotional State:")
        print(f"      Primary: {state.primary_emotion}")
        print(f"      Valence: {state.valence:.2f}, Arousal: {state.arousal:.2f}")
