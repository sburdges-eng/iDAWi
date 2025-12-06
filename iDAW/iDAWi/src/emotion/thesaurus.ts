/**
 * DAiW Emotion Thesaurus
 *
 * A comprehensive 6×6×6 emotion taxonomy with V-A-D (Valence-Arousal-Dominance) coordinates.
 * Follows the 6×6×6 grid convention (216 total nodes):
 * - Valence: 6 levels (-1 to +1)
 * - Arousal: 6 levels (-1 to +1)
 * - Dominance: 6 levels (-1 to +1)
 */

/** V-A-D coordinates for emotion mapping */
export interface VADCoordinates {
  /** Valence: negative to positive feeling (-1 to +1) */
  valence: number;
  /** Arousal: calm to excited (-1 to +1) */
  arousal: number;
  /** Dominance: submissive to dominant (-1 to +1) */
  dominance: number;
}

/** Musical characteristics derived from emotion */
export interface MusicalCharacteristics {
  /** Tempo in BPM */
  tempoRange: [number, number];
  /** Musical mode (major, minor, etc.) */
  mode: 'major' | 'minor' | 'dorian' | 'phrygian' | 'lydian' | 'mixolydian' | 'aeolian' | 'locrian';
  /** Dynamic level (pp to ff) */
  dynamics: 'pp' | 'p' | 'mp' | 'mf' | 'f' | 'ff';
  /** Articulation style */
  articulation: 'legato' | 'staccato' | 'marcato' | 'tenuto';
  /** Harmonic complexity (0-1) */
  harmonicComplexity: number;
  /** Rhythmic density (0-1) */
  rhythmicDensity: number;
  /** Suggested instruments */
  instruments: string[];
}

/** Complete emotion node with all properties */
export interface EmotionNode {
  /** Unique emotion name */
  name: string;
  /** V-A-D coordinates */
  vad: VADCoordinates;
  /** Musical characteristics */
  music: MusicalCharacteristics;
  /** Category of emotion */
  category: 'joy' | 'sadness' | 'anger' | 'fear' | 'surprise' | 'disgust' | 'neutral';
  /** Intensity level (1-6) */
  intensityLevel: 1 | 2 | 3 | 4 | 5 | 6;
  /** Related emotion synonyms */
  synonyms: string[];
}

/**
 * Map valence/arousal/dominance level to grid index (0-5)
 * Follows the 6×6×6 grid convention matching vadToGridPosition
 */
export function valueToGridLevel(value: number): 0 | 1 | 2 | 3 | 4 | 5 {
  return Math.min(5, Math.floor((value + 1) / 2 * 5.99)) as 0 | 1 | 2 | 3 | 4 | 5;
}

/**
 * Map arousal to tempo range
 */
function arousalToTempo(arousal: number): [number, number] {
  // -1 arousal = 40-60 BPM, +1 arousal = 140-180 BPM
  const baseTempo = 60 + (arousal + 1) * 50;
  return [Math.round(baseTempo - 10), Math.round(baseTempo + 10)];
}

/**
 * Map valence to mode
 */
function valenceToMode(valence: number): MusicalCharacteristics['mode'] {
  if (valence > 0.5) return 'major';
  if (valence > 0.2) return 'lydian';
  if (valence > -0.2) return 'mixolydian';
  if (valence > -0.5) return 'dorian';
  if (valence > -0.8) return 'aeolian';
  return 'phrygian';
}

/**
 * Map dominance to dynamics
 */
function dominanceToDynamics(dominance: number): MusicalCharacteristics['dynamics'] {
  if (dominance > 0.6) return 'ff';
  if (dominance > 0.3) return 'f';
  if (dominance > 0) return 'mf';
  if (dominance > -0.3) return 'mp';
  if (dominance > -0.6) return 'p';
  return 'pp';
}

/**
 * Generate musical characteristics from V-A-D coordinates
 */
export function vadToMusicalCharacteristics(vad: VADCoordinates): MusicalCharacteristics {
  const { valence, arousal, dominance } = vad;

  // Articulation based on arousal and dominance combination
  let articulation: MusicalCharacteristics['articulation'] = 'tenuto';
  if (arousal > 0.5 && dominance > 0) {
    articulation = 'marcato';
  } else if (arousal > 0.3) {
    articulation = 'staccato';
  } else if (arousal < -0.3) {
    articulation = 'legato';
  }

  // Harmonic complexity increases with negative valence and high arousal
  const harmonicComplexity = Math.max(0, Math.min(1, 
    0.3 + (arousal + 1) * 0.2 - valence * 0.3
  ));

  // Rhythmic density increases with arousal
  const rhythmicDensity = Math.max(0, Math.min(1,
    0.3 + (arousal + 1) * 0.35
  ));

  // Instrument selection based on emotion category
  const instruments: string[] = [];
  if (valence > 0.3) {
    instruments.push('piano', 'strings', 'brass');
  } else if (valence < -0.3) {
    instruments.push('cello', 'violin', 'oboe');
  }
  if (arousal > 0.5) {
    instruments.push('drums', 'percussion');
  }
  if (dominance > 0.3) {
    instruments.push('brass', 'timpani');
  } else if (dominance < -0.3) {
    instruments.push('flute', 'harp');
  }

  return {
    tempoRange: arousalToTempo(arousal),
    mode: valenceToMode(valence),
    dynamics: dominanceToDynamics(dominance),
    articulation,
    harmonicComplexity,
    rhythmicDensity,
    instruments: [...new Set(instruments)], // Remove duplicates
  };
}

/**
 * Core emotion nodes following the 6×6×6 grid convention
 */
export const EMOTION_NODES: Record<string, EmotionNode> = {
  // === JOY FAMILY ===
  ecstatic: {
    name: 'Ecstatic',
    vad: { valence: 1.0, arousal: 1.0, dominance: 0.8 },
    music: vadToMusicalCharacteristics({ valence: 1.0, arousal: 1.0, dominance: 0.8 }),
    category: 'joy',
    intensityLevel: 6,
    synonyms: ['euphoric', 'elated', 'overjoyed', 'thrilled'],
  },
  joyful: {
    name: 'Joyful',
    vad: { valence: 0.8, arousal: 0.7, dominance: 0.5 },
    music: vadToMusicalCharacteristics({ valence: 0.8, arousal: 0.7, dominance: 0.5 }),
    category: 'joy',
    intensityLevel: 5,
    synonyms: ['happy', 'delighted', 'cheerful', 'glad'],
  },
  content: {
    name: 'Content',
    vad: { valence: 0.6, arousal: 0.2, dominance: 0.3 },
    music: vadToMusicalCharacteristics({ valence: 0.6, arousal: 0.2, dominance: 0.3 }),
    category: 'joy',
    intensityLevel: 3,
    synonyms: ['satisfied', 'pleased', 'comfortable', 'at ease'],
  },
  serene: {
    name: 'Serene',
    vad: { valence: 0.5, arousal: -0.5, dominance: 0.2 },
    music: vadToMusicalCharacteristics({ valence: 0.5, arousal: -0.5, dominance: 0.2 }),
    category: 'joy',
    intensityLevel: 2,
    synonyms: ['peaceful', 'calm', 'tranquil', 'relaxed'],
  },
  hopeful: {
    name: 'Hopeful',
    vad: { valence: 0.6, arousal: 0.4, dominance: 0.4 },
    music: vadToMusicalCharacteristics({ valence: 0.6, arousal: 0.4, dominance: 0.4 }),
    category: 'joy',
    intensityLevel: 4,
    synonyms: ['optimistic', 'expectant', 'encouraged', 'anticipating'],
  },

  // === SADNESS FAMILY ===
  grieving: {
    name: 'Grieving',
    vad: { valence: -0.9, arousal: 0.2, dominance: -0.7 },
    music: vadToMusicalCharacteristics({ valence: -0.9, arousal: 0.2, dominance: -0.7 }),
    category: 'sadness',
    intensityLevel: 6,
    synonyms: ['mourning', 'bereaved', 'heartbroken', 'devastated'],
  },
  melancholy: {
    name: 'Melancholy',
    vad: { valence: -0.6, arousal: -0.3, dominance: -0.4 },
    music: vadToMusicalCharacteristics({ valence: -0.6, arousal: -0.3, dominance: -0.4 }),
    category: 'sadness',
    intensityLevel: 4,
    synonyms: ['wistful', 'pensive', 'nostalgic', 'bittersweet'],
  },
  lonely: {
    name: 'Lonely',
    vad: { valence: -0.5, arousal: -0.2, dominance: -0.5 },
    music: vadToMusicalCharacteristics({ valence: -0.5, arousal: -0.2, dominance: -0.5 }),
    category: 'sadness',
    intensityLevel: 4,
    synonyms: ['isolated', 'abandoned', 'forsaken', 'solitary'],
  },
  yearning: {
    name: 'Yearning',
    vad: { valence: -0.4, arousal: 0.3, dominance: -0.3 },
    music: vadToMusicalCharacteristics({ valence: -0.4, arousal: 0.3, dominance: -0.3 }),
    category: 'sadness',
    intensityLevel: 4,
    synonyms: ['longing', 'pining', 'craving', 'aching'],
  },
  despairing: {
    name: 'Despairing',
    vad: { valence: -1.0, arousal: 0.1, dominance: -0.9 },
    music: vadToMusicalCharacteristics({ valence: -1.0, arousal: 0.1, dominance: -0.9 }),
    category: 'sadness',
    intensityLevel: 6,
    synonyms: ['hopeless', 'defeated', 'dejected', 'forlorn'],
  },

  // === ANGER FAMILY ===
  furious: {
    name: 'Furious',
    vad: { valence: -0.8, arousal: 1.0, dominance: 0.8 },
    music: vadToMusicalCharacteristics({ valence: -0.8, arousal: 1.0, dominance: 0.8 }),
    category: 'anger',
    intensityLevel: 6,
    synonyms: ['enraged', 'livid', 'incensed', 'wrathful'],
  },
  angry: {
    name: 'Angry',
    vad: { valence: -0.6, arousal: 0.7, dominance: 0.6 },
    music: vadToMusicalCharacteristics({ valence: -0.6, arousal: 0.7, dominance: 0.6 }),
    category: 'anger',
    intensityLevel: 5,
    synonyms: ['mad', 'upset', 'irate', 'indignant'],
  },
  frustrated: {
    name: 'Frustrated',
    vad: { valence: -0.5, arousal: 0.5, dominance: 0.2 },
    music: vadToMusicalCharacteristics({ valence: -0.5, arousal: 0.5, dominance: 0.2 }),
    category: 'anger',
    intensityLevel: 4,
    synonyms: ['annoyed', 'exasperated', 'irritated', 'aggravated'],
  },
  resentful: {
    name: 'Resentful',
    vad: { valence: -0.6, arousal: 0.4, dominance: 0.3 },
    music: vadToMusicalCharacteristics({ valence: -0.6, arousal: 0.4, dominance: 0.3 }),
    category: 'anger',
    intensityLevel: 4,
    synonyms: ['bitter', 'grudging', 'spiteful', 'vengeful'],
  },

  // === FEAR FAMILY ===
  terrified: {
    name: 'Terrified',
    vad: { valence: -0.9, arousal: 0.9, dominance: -0.8 },
    music: vadToMusicalCharacteristics({ valence: -0.9, arousal: 0.9, dominance: -0.8 }),
    category: 'fear',
    intensityLevel: 6,
    synonyms: ['petrified', 'horrified', 'panicked', 'terror-stricken'],
  },
  anxious: {
    name: 'Anxious',
    vad: { valence: -0.5, arousal: 0.6, dominance: -0.4 },
    music: vadToMusicalCharacteristics({ valence: -0.5, arousal: 0.6, dominance: -0.4 }),
    category: 'fear',
    intensityLevel: 4,
    synonyms: ['worried', 'nervous', 'apprehensive', 'uneasy'],
  },
  dread: {
    name: 'Dread',
    vad: { valence: -0.7, arousal: 0.5, dominance: -0.6 },
    music: vadToMusicalCharacteristics({ valence: -0.7, arousal: 0.5, dominance: -0.6 }),
    category: 'fear',
    intensityLevel: 5,
    synonyms: ['foreboding', 'apprehension', 'trepidation', 'dismay'],
  },
  vulnerable: {
    name: 'Vulnerable',
    vad: { valence: -0.3, arousal: 0.2, dominance: -0.7 },
    music: vadToMusicalCharacteristics({ valence: -0.3, arousal: 0.2, dominance: -0.7 }),
    category: 'fear',
    intensityLevel: 3,
    synonyms: ['exposed', 'defenseless', 'unprotected', 'fragile'],
  },

  // === SURPRISE FAMILY ===
  amazed: {
    name: 'Amazed',
    vad: { valence: 0.5, arousal: 0.8, dominance: 0.0 },
    music: vadToMusicalCharacteristics({ valence: 0.5, arousal: 0.8, dominance: 0.0 }),
    category: 'surprise',
    intensityLevel: 5,
    synonyms: ['astonished', 'astounded', 'awestruck', 'stunned'],
  },
  surprised: {
    name: 'Surprised',
    vad: { valence: 0.2, arousal: 0.7, dominance: 0.0 },
    music: vadToMusicalCharacteristics({ valence: 0.2, arousal: 0.7, dominance: 0.0 }),
    category: 'surprise',
    intensityLevel: 4,
    synonyms: ['startled', 'shocked', 'taken aback', 'caught off guard'],
  },
  curious: {
    name: 'Curious',
    vad: { valence: 0.3, arousal: 0.5, dominance: 0.2 },
    music: vadToMusicalCharacteristics({ valence: 0.3, arousal: 0.5, dominance: 0.2 }),
    category: 'surprise',
    intensityLevel: 3,
    synonyms: ['intrigued', 'inquisitive', 'interested', 'fascinated'],
  },

  // === DISGUST FAMILY ===
  revolted: {
    name: 'Revolted',
    vad: { valence: -0.8, arousal: 0.6, dominance: 0.4 },
    music: vadToMusicalCharacteristics({ valence: -0.8, arousal: 0.6, dominance: 0.4 }),
    category: 'disgust',
    intensityLevel: 6,
    synonyms: ['repulsed', 'nauseated', 'sickened', 'appalled'],
  },
  contemptuous: {
    name: 'Contemptuous',
    vad: { valence: -0.5, arousal: 0.3, dominance: 0.6 },
    music: vadToMusicalCharacteristics({ valence: -0.5, arousal: 0.3, dominance: 0.6 }),
    category: 'disgust',
    intensityLevel: 4,
    synonyms: ['disdainful', 'scornful', 'dismissive', 'derisive'],
  },

  // === NEUTRAL ===
  neutral: {
    name: 'Neutral',
    vad: { valence: 0.0, arousal: 0.0, dominance: 0.0 },
    music: vadToMusicalCharacteristics({ valence: 0.0, arousal: 0.0, dominance: 0.0 }),
    category: 'neutral',
    intensityLevel: 1,
    synonyms: ['indifferent', 'detached', 'unmoved', 'impassive'],
  },
  focused: {
    name: 'Focused',
    vad: { valence: 0.1, arousal: 0.3, dominance: 0.4 },
    music: vadToMusicalCharacteristics({ valence: 0.1, arousal: 0.3, dominance: 0.4 }),
    category: 'neutral',
    intensityLevel: 3,
    synonyms: ['concentrated', 'attentive', 'absorbed', 'engaged'],
  },
};

/**
 * Find emotion node by name (case-insensitive)
 */
export function findEmotionByName(name: string): EmotionNode | undefined {
  const key = name.toLowerCase();
  return EMOTION_NODES[key];
}

/**
 * Find emotion by synonym
 */
export function findEmotionBySynonym(synonym: string): EmotionNode | undefined {
  const searchTerm = synonym.toLowerCase();
  for (const emotion of Object.values(EMOTION_NODES)) {
    if (emotion.synonyms.some(s => s.toLowerCase() === searchTerm)) {
      return emotion;
    }
  }
  return undefined;
}

/**
 * Get emotions by category
 */
export function getEmotionsByCategory(category: EmotionNode['category']): EmotionNode[] {
  return Object.values(EMOTION_NODES).filter(e => e.category === category);
}

/**
 * Get emotions by intensity level
 */
export function getEmotionsByIntensity(level: EmotionNode['intensityLevel']): EmotionNode[] {
  return Object.values(EMOTION_NODES).filter(e => e.intensityLevel === level);
}

/**
 * Find the closest emotion node to given V-A-D coordinates
 */
export function findClosestEmotion(vad: VADCoordinates): EmotionNode {
  let closest: EmotionNode = EMOTION_NODES.neutral;
  let minDistance = Infinity;

  for (const emotion of Object.values(EMOTION_NODES)) {
    const distance = Math.sqrt(
      Math.pow(emotion.vad.valence - vad.valence, 2) +
      Math.pow(emotion.vad.arousal - vad.arousal, 2) +
      Math.pow(emotion.vad.dominance - vad.dominance, 2)
    );

    if (distance < minDistance) {
      minDistance = distance;
      closest = emotion;
    }
  }

  return closest;
}

/**
 * Interpolate between two emotion nodes
 */
export function interpolateEmotions(
  emotion1: EmotionNode,
  emotion2: EmotionNode,
  t: number // 0 to 1, where 0 = emotion1 and 1 = emotion2
): VADCoordinates {
  const clampedT = Math.max(0, Math.min(1, t));
  
  return {
    valence: emotion1.vad.valence + (emotion2.vad.valence - emotion1.vad.valence) * clampedT,
    arousal: emotion1.vad.arousal + (emotion2.vad.arousal - emotion1.vad.arousal) * clampedT,
    dominance: emotion1.vad.dominance + (emotion2.vad.dominance - emotion1.vad.dominance) * clampedT,
  };
}

/**
 * Get all emotion names
 */
export function getAllEmotionNames(): string[] {
  return Object.values(EMOTION_NODES).map(e => e.name);
}

/**
 * Get grid position for V-A-D coordinates (0-5 for each dimension)
 */
export function vadToGridPosition(vad: VADCoordinates): { v: number; a: number; d: number } {
  const normalize = (value: number) => Math.min(5, Math.floor((value + 1) / 2 * 5.99));
  return {
    v: normalize(vad.valence),
    a: normalize(vad.arousal),
    d: normalize(vad.dominance),
  };
}

export default EMOTION_NODES;
