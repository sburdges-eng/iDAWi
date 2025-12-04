import { useEffect } from 'react';
import { useStore } from './store/useStore';
import { SideA } from './components/SideA';
import { SideB } from './components/SideB';
import { FlipIndicator } from './components/shared/FlipIndicator';

function App() {
  const { currentSide, toggleSide } = useStore();

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // ⌘E or Ctrl+E to flip sides
      if ((e.metaKey || e.ctrlKey) && e.key === 'e') {
        e.preventDefault();
        toggleSide();
      }

      // Space for play/pause (when not in input)
      if (e.key === ' ' && e.target === document.body) {
        e.preventDefault();
        // Will be handled by transport controls
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [toggleSide]);

  return (
    <div className="w-screen h-screen overflow-hidden bg-ableton-bg">
      {/* Flip Container */}
      <div className="flip-container">
        <div className={`flip-card ${currentSide === 'B' ? 'flipped' : ''}`}>
          {/* Side A - DAW Interface */}
          <div className="flip-card-face">
            <SideA />
          </div>

          {/* Side B - Emotion Interface */}
          <div className="flip-card-face flip-card-back">
            <SideB />
          </div>
        </div>
      </div>

      {/* Flip Indicator */}
      <FlipIndicator />
    </div>
  );
}

export default App;
