import { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';

export default function GaugeCard({ title, score, color = '#0e61a1', delay = 0 }) {
  const hasScore = score !== null && score !== undefined;
  const numericScore = hasScore ? Math.min(Math.max(score, 0), 100) : 0;
  const circumference = 2 * Math.PI * 40; // r=40
  const offset = hasScore ? circumference - (numericScore / 100) * circumference : circumference;

  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay, ease: 'easeOut' }}
      whileHover={{ y: -4, boxShadow: '0px 8px 32px rgba(11, 37, 69, 0.08)' }}
      className="bg-surface-container-lowest border border-[#E8F4F8] rounded-xl shadow-ice p-6 flex flex-col items-center justify-center relative overflow-hidden group transition-shadow"
    >
      {/* Hover shimmer */}
      <div className="absolute inset-0 bg-gradient-to-br from-[#bceaf9]/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

      <h3 className="text-title-lg font-bold text-primary mb-6 z-10">{title}</h3>

      {/* SVG Gauge */}
      <div className="relative w-32 h-32 flex items-center justify-center z-10">
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
          {/* Track */}
          <circle cx="50" cy="50" r="40" fill="none" stroke="#e5e9eb" strokeWidth="8" />
          {/* Progress */}
          <motion.circle
            cx="50" cy="50" r="40"
            fill="none"
            stroke={hasScore ? color : '#cbd5e1'}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1.5, ease: 'easeOut', delay }}
          />
        </svg>
        <div className="absolute flex flex-col items-center">
          <motion.span
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: delay + 0.5 }}
            className={`text-headline-md font-bold ${hasScore ? 'text-primary' : 'text-slate-400'}`}
          >
            {hasScore ? `${numericScore}%` : '--'}
          </motion.span>
          <span className="text-label-md text-on-surface-variant">
            {hasScore ? '/100' : 'Pending Audit'}
          </span>
        </div>
      </div>
    </motion.div>
  );
}

