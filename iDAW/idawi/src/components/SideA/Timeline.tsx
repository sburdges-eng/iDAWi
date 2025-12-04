import React, { useRef, useEffect } from 'react';
import { useStore } from '../../store/useStore';

export const Timeline: React.FC = () => {
  const { tracks, currentTime, isPlaying, tempo, timeSignature } = useStore();
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Calculate grid based on tempo and time signature
  const beatsPerBar = timeSignature[0];
  const pixelsPerBeat = 50;
  const pixelsPerBar = pixelsPerBeat * beatsPerBar;

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;

    // Draw background
    ctx.fillStyle = '#1a1a1a';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw grid lines
    const bars = Math.ceil(canvas.width / pixelsPerBar);
    for (let i = 0; i <= bars * beatsPerBar; i++) {
      const x = i * pixelsPerBeat;
      const isBar = i % beatsPerBar === 0;

      ctx.strokeStyle = isBar ? '#444' : '#2a2a2a';
      ctx.lineWidth = isBar ? 2 : 1;
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, canvas.height);
      ctx.stroke();

      // Bar numbers
      if (isBar) {
        ctx.fillStyle = '#666';
        ctx.font = '10px monospace';
        ctx.fillText(`${Math.floor(i / beatsPerBar) + 1}`, x + 4, 12);
      }
    }

    // Draw playhead
    const playheadX = (currentTime / 60) * tempo * pixelsPerBeat;
    ctx.strokeStyle = '#ff5500';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(playheadX, 0);
    ctx.lineTo(playheadX, canvas.height);
    ctx.stroke();

    // Draw tracks
    const trackHeight = Math.min(80, (canvas.height - 20) / Math.max(tracks.length, 1));
    tracks.forEach((track, index) => {
      const y = 20 + index * trackHeight;

      // Track background
      ctx.fillStyle = track.color + '40';
      ctx.fillRect(0, y, canvas.width, trackHeight - 2);

      // Track name
      ctx.fillStyle = '#fff';
      ctx.font = '11px sans-serif';
      ctx.fillText(track.name, 8, y + 16);

      // Draw clips (placeholder)
      track.clips.forEach(clip => {
        const clipX = clip.startTime * pixelsPerBeat;
        const clipWidth = clip.duration * pixelsPerBeat;

        ctx.fillStyle = track.color;
        ctx.fillRect(clipX, y + 4, clipWidth, trackHeight - 10);

        ctx.fillStyle = '#fff';
        ctx.font = '10px sans-serif';
        ctx.fillText(clip.name, clipX + 4, y + 18);
      });
    });

  }, [tracks, currentTime, tempo, beatsPerBar, pixelsPerBeat, pixelsPerBar]);

  return (
    <div className="flex-1 bg-ableton-bg overflow-hidden">
      <canvas
        ref={canvasRef}
        className="w-full h-full"
        style={{ display: 'block' }}
      />
    </div>
  );
};
