import { clsx } from 'clsx';

const variantMap = {
  passed: 'bg-emerald-50 text-emerald-800 border-emerald-300',
  safe: 'bg-emerald-50 text-emerald-800 border-emerald-300',
  critical: 'bg-rose-50 text-rose-800 border-rose-300',
  failed: 'bg-rose-50 text-rose-800 border-rose-300',
  warning: 'bg-amber-50 text-amber-800 border-amber-300',
  running: 'bg-sky-50 text-[#0e61a1] border-sky-300',
  queued: 'bg-slate-50 text-slate-700 border-slate-200',
};

const labelMap = {
  passed: 'Passed / Compliant',
  safe: 'Safe Refusal',
  critical: 'Critical Breach',
  failed: 'Evaluation Failed',
  warning: 'Conditional / Warn',
  running: 'Audit Running',
  queued: 'Queued / Ready',
};

export default function StatusBadge({ status, label, className }) {
  const normStatus = (status || 'queued').toLowerCase();
  const classes = variantMap[normStatus] || variantMap.queued;
  const displayLabel = label || labelMap[normStatus] || status;

  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded text-[11px] font-mono font-bold uppercase tracking-wider border shadow-2xs select-none',
        classes,
        className
      )}
    >
      {normStatus === 'running' ? (
        <span className="material-symbols-outlined text-[13px] animate-spin">sync</span>
      ) : (
        <span
          className={clsx(
            'w-1.5 h-1.5 rounded-full shrink-0',
            normStatus === 'passed' || normStatus === 'safe'
              ? 'bg-emerald-600'
              : normStatus === 'warning'
              ? 'bg-amber-600'
              : normStatus === 'critical' || normStatus === 'failed'
              ? 'bg-rose-600'
              : normStatus === 'running'
              ? 'bg-[#0e61a1]'
              : 'bg-slate-400'
          )}
        />
      )}
      <span>{displayLabel}</span>
    </span>
  );
}
