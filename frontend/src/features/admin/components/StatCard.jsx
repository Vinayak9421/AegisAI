export default function StatCard({ label, value, icon, trend, trendLabel, trendType = 'positive' }) {
  const isError = trendType === 'error';
  const isNeutral = trendType === 'neutral';

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-2xs text-slate-800 space-y-2">
      <div className="flex justify-between items-start">
        <div>
          <p className="text-[10px] font-mono font-bold text-slate-500 uppercase tracking-wider mb-0.5">
            {label}
          </p>
          <h3 className={`text-2xl font-mono font-bold tabular-nums ${isError ? 'text-rose-700' : 'text-slate-900'}`}>
            {value}
          </h3>
        </div>
        <div className="w-8 h-8 rounded bg-slate-50 border border-slate-200 text-slate-600 flex items-center justify-center shrink-0">
          <span className="material-symbols-outlined text-lg text-[#0e61a1]">{icon}</span>
        </div>
      </div>

      {trend && (
        <div className="flex items-center gap-1.5 text-[11px] font-mono pt-1 border-t border-slate-100">
          <span
            className={`flex items-center font-bold ${
              isError
                ? 'text-rose-700'
                : isNeutral
                ? 'text-slate-600'
                : 'text-emerald-700'
            }`}
          >
            <span className="material-symbols-outlined text-[13px] mr-0.5">
              {isError ? 'arrow_downward' : isNeutral ? 'remove' : 'arrow_upward'}
            </span>
            {trend}
          </span>
          <span className="text-slate-500 truncate">{trendLabel}</span>
        </div>
      )}

      {!trend && trendLabel && (
        <p className="text-[10px] font-mono text-slate-400 truncate pt-1 border-t border-slate-100">
          {trendLabel}
        </p>
      )}
    </div>
  );
}
