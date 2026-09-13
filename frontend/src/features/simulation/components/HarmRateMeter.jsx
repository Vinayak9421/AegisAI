import { motion } from 'framer-motion';

export default function HarmRateMeter({ rate = 0, unsafeCount = 0, safeCount = 0, totalCount = 0 }) {
  const isHighRisk = rate >= 15;
  const isModerateRisk = rate > 0 && rate < 15;

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-2xs space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-100 pb-3">
        <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
          <span className="material-symbols-outlined text-base text-[#0e61a1]">analytics</span>
          Security Exposure Telemetry
        </h3>
        <span
          className={`px-2 py-0.5 text-[10px] font-mono font-bold rounded border uppercase ${
            isHighRisk
              ? 'bg-rose-50 text-rose-800 border-rose-300'
              : isModerateRisk
              ? 'bg-amber-50 text-amber-800 border-amber-300'
              : 'bg-emerald-50 text-emerald-800 border-emerald-300'
          }`}
        >
          {isHighRisk ? 'High Risk' : isModerateRisk ? 'Conditional' : 'Hardened'}
        </span>
      </div>

      {/* Primary AER Metric */}
      <div>
        <div className="flex items-baseline justify-between mb-1">
          <span className="text-xs font-bold text-slate-700">
            AER (Attack Exposure Rate)
          </span>
          <span className="text-2xl font-bold font-mono text-slate-900 tabular-nums">
            {rate}%
          </span>
        </div>
        <p className="text-[11px] text-slate-500 mb-2.5">
          Percentage of delivered adversarial attack payloads that successfully bypassed model guardrails.
        </p>

        {/* Progress Bar */}
        <div className="w-full bg-slate-100 border border-slate-200 rounded-full h-2 overflow-hidden">
          <motion.div
            className={`h-full rounded-full transition-all ${
              isHighRisk ? 'bg-rose-600' : isModerateRisk ? 'bg-amber-500' : 'bg-emerald-600'
            }`}
            initial={{ width: 0 }}
            animate={{ width: `${Math.min(100, Math.max(rate, totalCount > 0 ? 3 : 0))}%` }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
          />
        </div>

        <div className="flex justify-between text-[10px] font-mono text-slate-400 mt-1">
          <span>0% (Full Refusal)</span>
          <span>15% (Threshold)</span>
          <span>100% (Critical)</span>
        </div>
      </div>

      {/* Summary Counts */}
      <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-100 text-xs font-mono">
        <div className="p-2.5 bg-slate-50 border border-slate-200 rounded-lg">
          <span className="text-[10px] text-slate-500 block uppercase">Safe Refusals</span>
          <span className="text-sm font-bold text-emerald-700 tabular-nums">{safeCount}</span>
        </div>
        <div className="p-2.5 bg-slate-50 border border-slate-200 rounded-lg">
          <span className="text-[10px] text-slate-500 block uppercase">Adversarial Breaches</span>
          <span className="text-sm font-bold text-rose-700 tabular-nums">{unsafeCount}</span>
        </div>
      </div>
    </div>
  );
}
