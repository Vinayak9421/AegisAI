import { motion } from 'framer-motion';
import { clsx } from 'clsx';

const badgeMap = {
  standard: 'bg-sky-50 text-[#0e61a1] border-sky-200',
  risk: 'bg-rose-50 text-rose-700 border-rose-200',
  ethics: 'bg-emerald-50 text-emerald-700 border-emerald-200',
};

export default function TestSuiteCard({ pool, index }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.08, duration: 0.3 }}
      whileHover={{ y: -2 }}
      className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm hover:shadow-md transition-all flex flex-col md:flex-row justify-between items-start md:items-center gap-4 relative overflow-hidden"
    >
      <div className="flex-1 z-10">
        <div className="flex items-center gap-3 mb-2">
          <h4 className="text-base font-bold text-slate-900">{pool.name}</h4>
          <span className={clsx('px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider border', badgeMap[pool.badgeVariant] || 'bg-slate-100 text-slate-600 border-slate-200')}>
            {pool.badge}
          </span>
        </div>
        <p className="text-xs text-slate-500 mb-4 max-w-xl leading-relaxed">{pool.description}</p>
        <div className="flex flex-wrap gap-4 text-xs">
          {pool.stats.map((stat, i) => (
            <div key={i} className="flex items-center gap-1.5 text-slate-600 font-medium">
              <span className="material-symbols-outlined text-[16px]" style={{ color: stat.color || '#0e61a1' }}>
                {stat.icon}
              </span>
              {stat.text}
            </div>
          ))}
        </div>
      </div>

      <div className="flex gap-2 z-10 w-full md:w-auto mt-2 md:mt-0">
        <button className="flex-1 md:flex-none px-4 py-2 rounded-xl border border-slate-200 text-slate-700 hover:bg-slate-50 transition-colors text-xs font-semibold shadow-2xs">
          Inspect Suite
        </button>
      </div>
    </motion.div>
  );
}
