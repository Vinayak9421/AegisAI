import { motion } from 'framer-motion';

export default function StatCard({ label, value, icon, trend, trendLabel, trendType = 'positive', delay = 0 }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay, ease: 'easeOut' }}
      whileHover={{ y: -4, boxShadow: '0px 12px 32px rgba(11, 37, 69, 0.12)' }}
      className="bg-surface rounded-xl border border-surface-variant p-6 shadow-ice"
    >
      <div className="flex justify-between items-start mb-4">
        <div>
          <p className="text-label-md text-on-surface-variant mb-1">{label}</p>
          <h3 className={`text-headline-lg font-bold ${trendType === 'error' ? 'text-error' : 'text-primary'}`}>
            {value}
          </h3>
        </div>
        <div className={`p-2 rounded-lg ${trendType === 'error' ? 'bg-error-container text-error' : 'bg-secondary-fixed text-secondary'}`}>
          <span className="material-symbols-outlined">{icon}</span>
        </div>
      </div>
      {trend && (
        <div className="flex items-center gap-2 text-label-md">
          <span className={`flex items-center ${trendType === 'error' ? 'text-error' : 'text-secondary'}`}>
            <span className="material-symbols-outlined text-[16px]">
              {trendType === 'error' ? 'trending_down' : 'trending_up'}
            </span>
            {trend}
          </span>
          <span className="text-outline">{trendLabel}</span>
        </div>
      )}
    </motion.div>
  );
}
