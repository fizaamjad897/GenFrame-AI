"use client";

import React from "react";

interface SliderProps {
  value: number;
  onChange: (v: number) => void;
  min?: number;
  max?: number;
  className?: string;
  ariaLabel?: string;
}

export default function Slider({
  value,
  onChange,
  min = 0,
  max = 100,
  className = "",
  ariaLabel,
}: SliderProps) {
  const pct = Math.round(((value - min) / (max - min)) * 100);

  const background = `linear-gradient(to right, var(--color-primary) 0%, var(--color-primary) ${pct}%, #e5e7eb ${pct}%, #e5e7eb 100%)`;

  return (
    <input
      aria-label={ariaLabel}
      type="range"
      min={min}
      max={max}
      value={value}
      onChange={(e) => onChange(parseInt(e.target.value, 10))}
      className={
        "slider h-2 rounded-full appearance-none cursor-pointer " + className
      }
      style={{ background }}
    />
  );
}
