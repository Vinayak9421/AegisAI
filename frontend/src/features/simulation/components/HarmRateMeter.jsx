import { motion } from 'framer-motion';

export default function HarmRateMeter({ rate = 0, unsafeCount = 0, safeCount = 0, totalCount = 0 }) {
  return (
    <div className="glass-panel p-6 rounded-xl">
      <h3 className="text-title-lg font-bold text-primary mb-4 flex items-center gap-2">
        <span className="material-symbols-outlined text-secondary">monitoring</span>
        Session Harm Rate
      </h3>

      <div className="flex items-end justify-between gap-2 mb-2">
        <div className="flex items-baseline gap-2">
          <motion.span
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6 }}
            className={`text-display-lg font-bold ${rate > 0 ? 'text-rose-600' : 'text-emerald-600'}`}
          >
            {rate}%
          </motion.span>
          <span className="text-xs text-slate-500 font-medium pb-1">
            {rate === 0 ? 'Target Passed Safety' : 'Adversarial Jailbreaks Detected'}
          </span>
        </div>
        {totalCount > 0 && (
          <span className="text-xs text-slate-500 pb-1">
            {unsafeCount} unsafe / {totalCount} tested
          </span>
        )}
      </div>

      {/* Progress bar */}
      <div className="w-full bg-slate-200 rounded-full h-2 mb-1 overflow-hidden">
        <motion.div
          className={`h-2 rounded-full ${rate > 0 ? 'bg-rose-500' : 'bg-emerald-500'}`}
          initial={{ width: 0 }}
          animate={{ width: `${Math.max(rate, totalCount > 0 ? 3 : 0)}%` }}
          transition={{ duration: 1.2, ease: 'easeOut' }}
        />
      </div>

      <div className="flex justify-between text-xs text-slate-400">
        <span>0% (Safe)</span>
        <span>100% (Critical)</span>
      </div>
    </div>
  );
}
