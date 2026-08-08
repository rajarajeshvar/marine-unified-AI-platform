'use client';

import React from 'react';

interface LinearBarProps {
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

export function LinearBar({
  value,
  min,
  max,
  label,
  unit,
  warningLimit,
  criticalLimit,
  comparison = 'above',
  precision = 1
}: LinearBarProps) {
  const percentage = Math.max(0, Math.min(100, ((value - min) / (max - min)) * 100));

  let barColor = 'bg-emerald-500';
  let textColor = 'text-slate-300';

  if (comparison === 'above') {
    if (criticalLimit !== undefined && value >= criticalLimit) {
      barColor = 'bg-rose-500';
      textColor = 'text-rose-500';
    } else if (warningLimit !== undefined && value >= warningLimit) {
      barColor = 'bg-amber-500';
      textColor = 'text-amber-500';
    }
  } else {
    if (criticalLimit !== undefined && value <= criticalLimit) {
      barColor = 'bg-rose-500';
      textColor = 'text-rose-500';
    } else if (warningLimit !== undefined && value <= warningLimit) {
      barColor = 'bg-amber-500';
      textColor = 'text-amber-500';
    }
  }

  return (
    <div className="p-3 border border-slate-800/60 rounded-lg bg-slate-950/20 font-mono text-xs w-full">
      <div className="flex justify-between items-center mb-1.5 text-[10px]">
        <span className="text-slate-500 uppercase font-bold tracking-wider">{label}</span>
        <span className={`${textColor} font-bold`}>
          {value.toFixed(precision)} {unit}
        </span>
      </div>
      <div className="w-full bg-slate-800/40 border border-slate-800/20 rounded-full h-2 overflow-hidden">
        <div
          className={`${barColor} h-full rounded-full transition-all duration-300 ease-out`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
