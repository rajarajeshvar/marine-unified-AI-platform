'use client';

import React from 'react';

interface DialGaugeProps {
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

export function DialGauge({
  value,
  min,
  max,
  label,
  unit,
  warningLimit,
  criticalLimit,
  comparison = 'above',
  precision = 1
}: DialGaugeProps) {
  const clampedValue = Math.max(min, Math.min(max, value));
  const percentage = (clampedValue - min) / (max - min);
  
  const radius = 50;
  const strokeWidth = 6;
  const circumference = 2 * Math.PI * radius;
  const arcLength = circumference * 0.75;
  const strokeDashoffset = arcLength - percentage * arcLength;

  let statusColor = 'stroke-emerald-500 text-emerald-500';
  let textColor = 'text-emerald-450';
  let bgArcColor = 'stroke-slate-800';

  if (comparison === 'above') {
    if (criticalLimit !== undefined && value >= criticalLimit) {
      statusColor = 'stroke-rose-600 text-rose-600';
      textColor = 'text-rose-500';
      bgArcColor = 'stroke-rose-950/20';
    } else if (warningLimit !== undefined && value >= warningLimit) {
      statusColor = 'stroke-amber-500 text-amber-500';
      textColor = 'text-amber-450';
      bgArcColor = 'stroke-amber-950/20';
    }
  } else {
    if (criticalLimit !== undefined && value <= criticalLimit) {
      statusColor = 'stroke-rose-600 text-rose-600';
      textColor = 'text-rose-500';
      bgArcColor = 'stroke-rose-950/20';
    } else if (warningLimit !== undefined && value <= warningLimit) {
      statusColor = 'stroke-amber-500 text-amber-500';
      textColor = 'text-amber-450';
      bgArcColor = 'stroke-amber-950/20';
    }
  }

  return (
    <div className="flex flex-col items-center justify-center p-3 rounded-lg border border-slate-800/60 bg-slate-950/30 backdrop-blur-sm w-full">
      <div className="relative w-28 h-20">
        <svg className="w-full h-full -rotate-225" viewBox="0 0 120 120">
          {/* Outer dial ring */}
          <circle cx="60" cy="60" r={radius + 4} fill="none" stroke="#1e293b" strokeWidth="1" strokeDasharray="4 4" className="opacity-40" />
          
          {/* Background track */}
          <circle
            className={`${bgArcColor} transition-colors duration-300`}
            cx="60"
            cy="60"
            r={radius}
            strokeWidth={strokeWidth}
            strokeDasharray={arcLength}
            strokeDashoffset={0}
            strokeLinecap="round"
            fill="transparent"
          />
          {/* Telemetry dial track */}
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
        {/* Monospace values box */}
        <div className="absolute inset-0 top-2 flex flex-col items-center justify-center text-center">
          <span className={`text-lg font-bold font-mono ${textColor} tracking-tight`}>
            {value.toFixed(precision)}
          </span>
          <span className="text-[9px] text-slate-500 uppercase tracking-wider font-semibold">
            {unit}
          </span>
        </div>
      </div>
      <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider text-center block mt-[-4px]">
        {label}
      </span>
    </div>
  );
}
