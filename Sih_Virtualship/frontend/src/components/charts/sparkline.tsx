import React from 'react';

interface SparklineProps {
  data: number[];
  width?: number;
  height?: number;
  className?: string;
  color?: string;
}

export function Sparkline({
  data,
  width = 100,
  height = 24,
  className = '',
  color = 'stroke-sky-500'
}: SparklineProps) {
  // Graceful fallback for insufficient arrays
  if (!data || data.length < 2) {
    return (
      <div className="text-[9px] text-slate-700 font-mono tracking-wider">
        CALIBRATING...
      </div>
    );
  }

  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min === 0 ? 1 : max - min;

  // Calculate coordinates mapping for each point
  const points = data.map((val, idx) => {
    const x = (idx / (data.length - 1)) * width;
    const y = height - ((val - min) / range) * height;
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  });

  const pathData = `M ${points.join(' L ')}`;

  return (
    <svg className={className} width={width} height={height} viewBox={`0 0 ${width} ${height}`} fill="none">
      <path
        d={pathData}
        className={`${color} transition-all duration-300`}
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
