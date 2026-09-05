import { motion } from 'framer-motion';

export default function StatCard({ label, value, icon, trend, trendLabel, trendType = 'positive', delay = 0 }) {
  const isError = trendType === 'error';

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay, ease: 'easeOut' }}
      whileHover={{ y: -2 }}
      className="bg-white rounded-2xl border border-slate-200/80 p-5 shadow-sm text-slate-800"
    >
      <div className="flex justify-between items-start mb-3">
        <div>
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">{label}</p>
          <h3 className={`text-2xl md:text-3xl font-bold ${isError ? 'text-rose-600' : 'text-slate-900'}`}>
            {value}
          </h3>
        </div>
        <div className={`p-2.5 rounded-xl border ${
          isError 
            ? 'bg-rose-50 text-rose-600 border-rose-200' 
            : 'bg-sky-50 text-[#0e61a1] border-sky-200'
        }`}>
          <span className="material-symbols-outlined text-xl">{icon}</span>
        </div>
      </div>
      {trend && (
        <div className="flex items-center gap-2 text-xs">
          <span className={`flex items-center font-semibold ${isError ? 'text-rose-600' : 'text-[#0e61a1]'}`}>
            <span className="material-symbols-outlined text-[15px] mr-0.5">
              {isError ? 'trending_down' : 'trending_up'}
            </span>
            {trend}
          </span>
          <span className="text-slate-500 truncate">{trendLabel}</span>
        </div>
      )}
      {!trend && trendLabel && (
        <p className="text-xs text-slate-400 truncate">{trendLabel}</p>
      )}
    </motion.div>
  );
}
