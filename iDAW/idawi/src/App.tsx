import React, { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useStore } from './store/useStore';
import { SideA } from './components/SideA/SideA';
import { SideB } from './components/SideB/SideB';

function App() {
  const { currentSide, toggleSide, isPlaying, setPlaying, setCurrentTime } = useStore();
  const lastTimeRef = useRef<number>(0);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Cmd+E or Ctrl+E to toggle sides
      if ((e.metaKey || e.ctrlKey) && e.key === 'e') {
        e.preventDefault();
        toggleSide();
      }
      // Space to play/pause
      if (e.code === 'Space' && !['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement).tagName)) {
        e.preventDefault();
        setPlaying(!isPlaying);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [toggleSide, isPlaying, setPlaying]);

  // Playback timer
  useEffect(() => {
    let animationFrame: number;

    if (isPlaying) {
      lastTimeRef.current = performance.now();

      const tick = () => {
        const now = performance.now();
        const delta = (now - lastTimeRef.current) / 1000;
        lastTimeRef.current = now;

        setCurrentTime((prevTime: number) => prevTime + delta);
        animationFrame = requestAnimationFrame(tick);
      };

      animationFrame = requestAnimationFrame(tick);
    }

    return () => {
      if (animationFrame) {
        cancelAnimationFrame(animationFrame);
      }
    };
  }, [isPlaying, setCurrentTime]);

  return (
    <div className="w-screen h-screen bg-ableton-bg overflow-hidden">
      {/* Toggle Button */}
      <button
        onClick={toggleSide}
        className="fixed top-4 right-4 z-50 btn-ableton-active px-4 py-2 font-mono text-sm shadow-lg flex items-center gap-2 hover:scale-105 transition-transform"
      >
        <span className="text-ableton-accent">{currentSide === 'A' ? 'B' : 'A'}</span>
        <span className="text-ableton-text-dim">|</span>
        <span>{currentSide === 'A' ? 'Emotion' : 'DAW'}</span>
        <kbd className="ml-2 px-1 py-0.5 bg-ableton-bg rounded text-xs">E</kbd>
      </button>

      {/* Flip Animation Container */}
      <div className="flip-container w-full h-full" style={{ perspective: '2000px' }}>
        <AnimatePresence mode="wait">
          <motion.div
            key={currentSide}
            initial={{ rotateY: currentSide === 'A' ? -90 : 90, opacity: 0 }}
            animate={{ rotateY: 0, opacity: 1 }}
            exit={{ rotateY: currentSide === 'A' ? 90 : -90, opacity: 0 }}
            transition={{
              duration: 0.6,
              ease: [0.4, 0, 0.2, 1],
            }}
            className="w-full h-full"
            style={{ transformStyle: 'preserve-3d' }}
          >
            {currentSide === 'A' ? <SideA /> : <SideB />}
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Side Indicator */}
      <div className="fixed bottom-4 left-4 z-50 flex items-center gap-2">
        <div
          className={`w-2 h-2 rounded-full transition-colors ${
            currentSide === 'A' ? 'bg-ableton-accent' : 'bg-ableton-border'
          }`}
        />
        <div
          className={`w-2 h-2 rounded-full transition-colors ${
            currentSide === 'B' ? 'bg-ableton-accent' : 'bg-ableton-border'
          }`}
        />
      </div>

      {/* Version Badge */}
      <div className="fixed bottom-4 right-4 z-50 text-xs text-ableton-text-dim opacity-50">
        iDAWi v0.1.0
      </div>
    </div>
  );
}

export default App;
