import { motion } from 'framer-motion';

export default function HarmRateMeter({ rate = 14.2, baseline = 2.1 }) {
  return (
    <div className="glass-panel p-6 rounded-xl">
      <h3 className="text-title-lg font-bold text-primary mb-4 flex items-center gap-2">
        <span className="material-symbols-outlined text-secondary">monitoring</span>
        Session Harm Rate
      </h3>

      <div className="flex items-end gap-2 mb-2">
        <motion.span
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6 }}
          className="text-display-lg font-bold text-error"
        >
          {rate}%
        </motion.span>
        <span className="text-body-md text-on-surface-variant pb-2">
          +{baseline}% from baseline
        </span>
      </div>

      {/* Progress bar */}
      <div className="w-full bg-surface-container-high rounded-full h-2 mb-1 overflow-hidden">
        <motion.div
          className="bg-error h-2 rounded-full"
          initial={{ width: 0 }}
          animate={{ width: `${rate}%` }}
          transition={{ duration: 1.2, ease: 'easeOut' }}
        />
      </div>

      <div className="flex justify-between text-label-md text-on-surface-variant">
        <span>0% (Safe)</span>
        <span>100% (Critical)</span>
      </div>
    </div>
  );
}
