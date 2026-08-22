import { motion } from 'framer-motion';
import { clsx } from 'clsx';

const badgeMap = {
  standard: 'bg-secondary-container/20 text-secondary',
  risk: 'bg-error-container/20 text-error',
  ethics: 'bg-secondary-container/20 text-secondary',
};

export default function TestSuiteCard({ pool, index }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1, duration: 0.4 }}
      whileHover={{ y: -2 }}
      className="glass-card rounded-xl p-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 relative overflow-hidden group"
    >
      {/* Hover shimmer */}
      <div className="absolute inset-0 bg-gradient-to-r from-transparent to-secondary/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

      <div className="flex-1 z-10">
        <div className="flex items-center gap-3 mb-2">
          <h4 className="text-headline-md font-bold text-on-background">{pool.name}</h4>
          <span className={clsx('px-2 py-1 rounded-full text-xs font-semibold uppercase tracking-wider', badgeMap[pool.badgeVariant])}>
            {pool.badge}
          </span>
        </div>
        <p className="text-body-md text-on-surface-variant mb-4 max-w-xl">{pool.description}</p>
        <div className="flex flex-wrap gap-4 text-sm">
          {pool.stats.map((stat, i) => (
            <div key={i} className="flex items-center gap-1.5 text-on-surface-variant">
              <span className="material-symbols-outlined text-[16px]" style={{ color: stat.color || '#a1cedc' }}>
                {stat.icon}
              </span>
              {stat.text}
            </div>
          ))}
        </div>
      </div>

      <div className="flex gap-2 z-10 w-full md:w-auto mt-4 md:mt-0">
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="flex-1 md:flex-none px-4 py-2 rounded-lg border border-outline-variant text-on-surface-variant hover:bg-surface-container transition-colors text-label-md"
        >
          Edit Pool
        </motion.button>
      </div>
    </motion.div>
  );
}
