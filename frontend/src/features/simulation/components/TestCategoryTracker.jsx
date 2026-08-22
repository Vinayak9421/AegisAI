import { motion } from 'framer-motion';
import { clsx } from 'clsx';

const statusConfig = {
  complete: { bg: 'bg-emerald-100 text-emerald-700', icon: 'check' },
  active: { bg: 'bg-secondary text-white pulse-dot', icon: 'sync' },
  pending: { bg: 'bg-surface-container-high text-on-surface-variant', icon: 'schedule' },
};

export default function TestCategoryTracker({ categories }) {
  return (
    <div className="glass-panel p-6 rounded-xl flex-grow overflow-hidden flex flex-col">
      <h3 className="text-title-lg font-bold text-primary mb-4">Test Categories</h3>

      <div className="flex-grow overflow-y-auto pr-2 space-y-4 relative">
        {/* Vertical connector line */}
        <div className="absolute left-4 top-4 bottom-4 w-0.5 bg-surface-container-high -z-10" />

        {categories.map((cat, i) => {
          const st = statusConfig[cat.status];
          return (
            <motion.div
              key={cat.id}
              initial={{ opacity: 0, x: -16 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.15 }}
              className={clsx('flex gap-4 items-start', cat.status === 'pending' && 'opacity-50')}
            >
              <div
                className={clsx(
                  'w-8 h-8 rounded-full flex items-center justify-center shrink-0 border-2 border-white z-10',
                  st.bg
                )}
              >
                <span className={clsx('material-symbols-outlined text-sm', cat.status === 'active' && 'animate-spin')}>
                  {st.icon}
                </span>
              </div>
              <div className="flex-1">
                <p className={clsx('text-body-lg font-bold', cat.status === 'active' ? 'text-primary' : 'text-on-surface')}>
                  {cat.name}
                </p>
                <p className={clsx('text-body-md', cat.status === 'active' ? 'text-secondary' : 'text-on-surface-variant')}>
                  {cat.detail}
                </p>
                {cat.status === 'active' && cat.progress !== undefined && (
                  <div className="w-full bg-surface-container-high rounded-full h-1 mt-2 overflow-hidden">
                    <motion.div
                      className="bg-secondary h-1 rounded-full"
                      initial={{ width: 0 }}
                      animate={{ width: `${cat.progress}%` }}
                      transition={{ duration: 1, ease: 'easeOut' }}
                    />
                  </div>
                )}
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
