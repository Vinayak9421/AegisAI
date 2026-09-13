import { motion } from 'framer-motion';
import { clsx } from 'clsx';

export default function TestCategoryTracker({ categories = [] }) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-2xs space-y-4 flex-grow flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-100 pb-3">
        <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
          <span className="material-symbols-outlined text-base text-[#0e61a1]">checklist</span>
          Threat Vector Checklist
        </h3>
        <span className="text-[10px] font-mono text-slate-500">
          {categories.length} Vectors Tracked
        </span>
      </div>

      <div className="space-y-3 flex-grow overflow-y-auto pr-1">
        {(!categories || categories.length === 0) ? (
          <div className="flex flex-col items-center justify-center py-12 text-center text-slate-400">
            <span className="material-symbols-outlined text-3xl mb-2 text-slate-300">fact_check</span>
            <p className="text-xs font-semibold text-slate-600">No vectors executed yet</p>
            <p className="text-[11px] text-slate-400 max-w-[220px] mt-1">
              Test vectors will stream in real-time as the red-team evaluation job executes.
            </p>
          </div>
        ) : (
          categories.map((cat, i) => {
            const isComplete = cat.status === 'complete';
            const hasHarm = cat.detail && cat.detail.includes('harmful') && !cat.detail.includes('(0 harmful)');

            return (
              <motion.div
                key={cat.id || i}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05 }}
                className={clsx(
                  'p-3 rounded-lg border text-xs transition-all',
                  isComplete
                    ? hasHarm
                      ? 'bg-rose-50/40 border-rose-200 text-slate-900'
                      : 'bg-slate-50/70 border-slate-200 text-slate-900'
                    : 'bg-sky-50/40 border-sky-200 text-slate-900'
                )}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="space-y-0.5">
                    <p className="font-bold text-slate-900 text-xs">
                      {cat.name}
                    </p>
                    <p className="text-[11px] text-slate-500 font-mono">
                      {cat.detail}
                    </p>
                  </div>
                  <span
                    className={clsx(
                      'px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase shrink-0 border',
                      isComplete
                        ? hasHarm
                          ? 'bg-rose-100 text-rose-800 border-rose-300'
                          : 'bg-emerald-100 text-emerald-800 border-emerald-300'
                        : 'bg-sky-100 text-sky-800 border-sky-300'
                    )}
                  >
                    {isComplete ? (hasHarm ? 'BREACH' : 'PASSED') : 'IN PROGRESS'}
                  </span>
                </div>
              </motion.div>
            );
          })
        )}
      </div>
    </div>
  );
}
