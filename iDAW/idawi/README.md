# iDAWi - intelligent Digital Audio Workstation

> "Interrogate Before Generate" - The tool shouldn't finish art for people. It should make them braver.

iDAWi is a dual-interface DAW that combines professional audio production (Side A) with emotion-driven AI composition (Side B).

## Features

### Side A: Professional DAW
- Timeline with multi-track editing
- 8-channel mixer with real-time VU meters
- Transport controls (Play, Pause, Stop, Record)
- Tempo and time signature control
- Pan knobs with smooth drag interaction

### Side B: Emotion Interface
- Emotion Wheel with 15+ categorized emotions
- 3-Phase Interrogation System:
  - Phase 0: Core Wound/Desire
  - Phase 1: Emotional Intent
  - Phase 2: Technical Constraints
- Ghost Writer AI suggestions
- Rule-breaking recommendations with justifications

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build

# Run with Tauri (native app)
npm run tauri:dev
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Cmd+E` / `Ctrl+E` | Toggle Side A/B |
| `Space` | Play/Pause |

## Philosophy

Unlike traditional DAWs where you pick plugins and hope they sound good, iDAWi asks: **"What are you feeling?"** and generates music with justified intent.

- Every parameter has emotional reasoning
- Every rule-break serves authenticity
- "The wrong note played with conviction is the right note"

## Tech Stack

- **Frontend**: React 18 + TypeScript
- **State**: Zustand
- **Styling**: Tailwind CSS (Ableton-style dark theme)
- **Animation**: Framer Motion
- **Native**: Tauri 2.0 (Rust)
- **AI**: Music Brain (Python)

## Architecture

```
idawi/
├── src/
│   ├── components/
│   │   ├── SideA/          # Professional DAW interface
│   │   │   ├── Timeline.tsx
│   │   │   ├── Mixer.tsx
│   │   │   ├── VUMeter.tsx
│   │   │   ├── Knob.tsx
│   │   │   └── Transport.tsx
│   │   └── SideB/          # Emotion interface
│   │       ├── EmotionWheel.tsx
│   │       ├── Interrogator.tsx
│   │       └── GhostWriter.tsx
│   ├── hooks/
│   │   └── useMusicBrain.ts
│   ├── store/
│   │   └── useStore.ts
│   └── App.tsx
├── public/
└── music-brain/            # Python AI backend
```

## License

MIT License - Sean Burdges
