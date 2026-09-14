import React from 'react';

/**
 * Official AegisAI Brand Logo
 * Geometric shield with dual-facet depth and cryptographic safety node.
 */
export default function AegisLogo({
  size = 'md',
  variant = 'full',
  showSubtitle = false,
  subtitleText = 'TRUST & SAFETY PLATFORM',
  className = '',
  textColor = 'text-slate-900',
}) {
  // Dimensions map for mark
  const sizeMap = {
    xs: { mark: 22, text: 'text-sm', badge: 'text-[9px] px-1 py-0.2' },
    sm: { mark: 28, text: 'text-base', badge: 'text-[10px] px-1.5 py-0.5' },
    md: { mark: 36, text: 'text-lg', badge: 'text-[11px] px-1.5 py-0.5' },
    lg: { mark: 44, text: 'text-xl', badge: 'text-xs px-2 py-0.5' },
    xl: { mark: 56, text: 'text-2xl', badge: 'text-xs px-2.5 py-1' },
  };

  const currentSize = sizeMap[size] || sizeMap.md;
  const markPx = currentSize.mark;

  const ShieldIcon = (
    <svg
      width={markPx}
      height={markPx}
      viewBox="0 0 44 44"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="shrink-0 drop-shadow-xs"
      aria-label="AegisAI Shield Emblem"
    >
      <defs>
        {/* Navy & Azure Gradients */}
        <linearGradient id="aegisLeftFacet" x1="6" y1="4" x2="22" y2="40" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#001c40" />
          <stop offset="60%" stopColor="#0a3d6b" />
          <stop offset="100%" stopColor="#0e61a1" />
        </linearGradient>

        <linearGradient id="aegisRightFacet" x1="22" y1="4" x2="38" y2="40" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#0a4377" />
          <stop offset="50%" stopColor="#0e61a1" />
          <stop offset="100%" stopColor="#1a7ec8" />
        </linearGradient>

        <linearGradient id="aegisInnerCore" x1="14" y1="12" x2="30" y2="32" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#ffffff" stopOpacity="0.95" />
          <stop offset="60%" stopColor="#e0f2fe" />
          <stop offset="100%" stopColor="#bae6fd" />
        </linearGradient>

        <linearGradient id="aegisAccentGlow" x1="22" y1="10" x2="22" y2="28" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#38bdf8" />
          <stop offset="100%" stopColor="#0284c7" />
        </linearGradient>
      </defs>

      {/* Shield Base Outer Rim */}
      <path
        d="M22 2L6 8V20C6 30.5 13 39.2 22 42C31 39.2 38 30.5 38 20V8L22 2Z"
        fill="#00132b"
        stroke="#0e61a1"
        strokeWidth="1.2"
      />

      {/* Left Shield Facet (Deep Contrast Navy) */}
      <path
        d="M22 3.6L7.6 9V19.8C7.6 29.3 13.9 37.3 22 39.9V3.6Z"
        fill="url(#aegisLeftFacet)"
      />

      {/* Right Shield Facet (Reflective Azure) */}
      <path
        d="M22 3.6L36.4 9V19.8C36.4 29.3 30.1 37.3 22 39.9V3.6Z"
        fill="url(#aegisRightFacet)"
      />

      {/* Central Geometric Divider / Backbone */}
      <path
        d="M22 3.5V40"
        stroke="#ffffff"
        strokeOpacity="0.25"
        strokeWidth="1"
      />

      {/* Inner Safeguard Core Diamond / AI Chevron */}
      <path
        d="M22 11L29.5 19L22 29L14.5 19L22 11Z"
        fill="url(#aegisInnerCore)"
        stroke="#38bdf8"
        strokeWidth="1"
      />

      {/* Internal Security Node / Circuit Anchor */}
      <circle
        cx="22"
        cy="19"
        r="3.5"
        fill="url(#aegisAccentGlow)"
        stroke="#ffffff"
        strokeWidth="1"
      />

      {/* Subtle Horizontal Alignment Grid Marks */}
      <path
        d="M10 20H13M31 20H34"
        stroke="#38bdf8"
        strokeWidth="1.2"
        strokeLinecap="round"
        strokeOpacity="0.7"
      />
    </svg>
  );

  if (variant === 'icon-only' || variant === 'mark') {
    return (
      <div className={`inline-flex items-center justify-center ${className}`}>
        {ShieldIcon}
      </div>
    );
  }

  return (
    <div className={`inline-flex items-center gap-3 ${className}`}>
      {ShieldIcon}
      <div className="flex flex-col text-left">
        <div className="flex items-center gap-1.5 leading-none">
          <span className={`font-serif font-bold tracking-tight ${textColor} ${currentSize.text}`}>
            Aegis
          </span>
          <span className={`font-mono font-extrabold uppercase bg-sky-100/90 text-[#0e61a1] border border-sky-300/80 rounded-md tracking-wider ${currentSize.badge}`}>
            AI
          </span>
        </div>
        {showSubtitle && (
          <span className="text-[10px] font-mono tracking-widest uppercase text-slate-400 font-semibold mt-1">
            {subtitleText}
          </span>
        )}
      </div>
    </div>
  );
}
