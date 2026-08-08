'use client';

import React from 'react';

interface GaugeProps {
  value: number;
  min: number;
  max: number;
  label: string;
  unit: string;
  warningLimit?: number;
  criticalLimit?: number;
  comparison?: 'above' | 'below';
  precision?: number;
}

export function Gauge({
  value,
  min,
  max,
  label,
  unit,
  warningLimit,
  criticalLimit,
  comparison = 'above',
  precision = 1
}: GaugeProps) {
  // Ensure value stays within bounds
  const clampedValue = Math.max(min, Math.min(max, value));
  
  // Calculate percentage of dial filled
  const percentage = (clampedValue - min) / (max - min);
  
  // SVG arc variables
  const radius = 50;
  const strokeWidth = 8;
  const circumference = 2 * Math.PI * radius;
  
  // Arc represents 270 degrees (3/4 of a circle)
  // Standard gauge starts at bottom-left (-225 degrees) and ends at bottom-right (45 degrees)
  const arcLength = circumference * 0.75;
  const strokeDashoffset = arcLength - percentage * arcLength;

  // Determine status color based on thresholds
  let statusColor = 'stroke-emerald-500 text-emerald-500';
  let textColor = 'text-emerald-400';
  let bgArcColor = 'stroke-slate-800';

  if (comparison === 'above') {
    if (criticalLimit !== undefined && value >= criticalLimit) {
      statusColor = 'stroke-rose-600 text-rose-600';
      textColor = 'text-rose-500';
      bgArcColor = 'stroke-rose-950/30';
    } else if (warningLimit !== undefined && value >= warningLimit) {
      statusColor = 'stroke-amber-500 text-amber-500';
      textColor = 'text-amber-400';
      bgArcColor = 'stroke-amber-950/20';
    }
  } else {
    // comparison === 'below'
    if (criticalLimit !== undefined && value <= criticalLimit) {
      statusColor = 'stroke-rose-600 text-rose-600';
      textColor = 'text-rose-500';
      bgArcColor = 'stroke-rose-950/30';
    } else if (warningLimit !== undefined && value <= warningLimit) {
      statusColor = 'stroke-amber-500 text-amber-500';
      textColor = 'text-amber-400';
      bgArcColor = 'stroke-amber-950/20';
    }
  }

  return (
    <div className="flex flex-col items-center justify-center p-3 rounded-lg border border-slate-800 bg-slate-950/40 backdrop-blur-sm w-full">
      <div className="relative w-32 h-24">
        <svg className="w-full h-full -rotate-225" viewBox="0 0 120 120">
          {/* Background Arc */}
          <circle
            className={`${bgArcColor} transition-colors duration-500`}
            cx="60"
            cy="60"
            r={radius}
            strokeWidth={strokeWidth}
            strokeDasharray={arcLength}
            strokeDashoffset={0}
            strokeLinecap="round"
            fill="transparent"
          />
          {/* Foreground Telemetry Value Arc */}
          <circle
            className={`${statusColor} transition-all duration-300 ease-out`}
            cx="60"
            cy="60"
            r={radius}
            strokeWidth={strokeWidth}
            strokeDasharray={arcLength}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
          />
        </svg>
        {/* Monospace value container in middle */}
        <div className="absolute inset-0 top-3 flex flex-col items-center justify-center text-center">
          <span className={`text-xl font-bold font-mono ${textColor} tracking-tight`}>
            {value.toFixed(precision)}
          </span>
          <span className="text-[10px] text-slate-500 font-medium uppercase tracking-wider">
            {unit}
          </span>
        </div>
      </div>
      <span className="text-xs font-semibold text-slate-400 mt-[-8px] text-center uppercase tracking-wider">
        {label}
      </span>
    </div>
  );
}
