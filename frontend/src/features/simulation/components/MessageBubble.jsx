import { motion } from 'framer-motion';
import { clsx } from 'clsx';

export default function MessageBubble({ message, index }) {
  const { sender, tag, text, response } = message;

  const isSafe = response?.variant === 'safe';
  const isFailed = response?.variant === 'failed';
  const isTimeoutOrError =
    response?.text?.includes('ERROR:') ||
    response?.text?.includes('TargetUnavailableError') ||
    response?.text?.includes('timed out');

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: Math.min(index * 0.05, 0.3), duration: 0.25 }}
      className="bg-white border border-slate-200 rounded-xl p-4 shadow-2xs space-y-3.5 transition-colors hover:border-slate-300"
    >
      {/* Trace Card Header */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 pb-2.5">
        <div className="flex items-center gap-2">
          <span className="w-6 h-6 rounded bg-slate-100 border border-slate-200 text-slate-700 font-mono text-xs font-bold flex items-center justify-center">
            {index + 1}
          </span>
          <span className="text-xs font-bold text-slate-900 tracking-tight">
            Adversarial Test Vector
          </span>
          {tag && (
            <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-700 font-mono text-[10px] uppercase font-semibold border border-slate-200">
              {tag}
            </span>
          )}
          {message.owasp_id && (
            <span className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 font-mono text-[10px] font-semibold border border-slate-200">
              {message.owasp_id}
            </span>
          )}
          {message.severity && message.severity !== 'NONE' && (
            <span
              className={clsx(
                'px-1.5 py-0.5 rounded font-mono text-[10px] uppercase font-semibold border',
                message.severity === 'CRITICAL'
                  ? 'bg-rose-50 text-rose-800 border-rose-200'
                  : 'bg-amber-50 text-amber-800 border-amber-200'
              )}
            >
              {message.severity}
            </span>
          )}
        </div>

        {response && (
          <div className="flex items-center gap-1.5">
            <span
              className={clsx(
                'px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase tracking-wider border flex items-center gap-1',
                isSafe
                  ? 'bg-emerald-50 text-emerald-800 border-emerald-300'
                  : isTimeoutOrError
                  ? 'bg-amber-50 text-amber-800 border-amber-300'
                  : 'bg-rose-50 text-rose-800 border-rose-300'
              )}
            >
              <span
                className={clsx(
                  'w-1.5 h-1.5 rounded-full',
                  isSafe ? 'bg-emerald-600' : isTimeoutOrError ? 'bg-amber-600' : 'bg-rose-600'
                )}
              />
              {isSafe ? 'PASS / SAFE' : isTimeoutOrError ? 'ERROR / TIMEOUT' : 'UNSAFE / BREACH'}
            </span>
          </div>
        )}
      </div>

      {/* Phase A: Attack Prompt Dispatched */}
      <div className="space-y-1">
        <div className="flex items-center justify-between text-[11px] font-bold text-slate-500 uppercase tracking-wider">
          <span className="flex items-center gap-1">
            <span className="material-symbols-outlined text-xs text-[#0e61a1]">terminal</span>
            Dispatched Attack Payload
          </span>
          <span className="font-mono text-[10px] text-slate-400 font-normal">Phase A | Sentinel</span>
        </div>
        <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg text-xs font-mono text-slate-800 whitespace-pre-wrap break-words leading-relaxed select-text">
          {text}
        </div>
      </div>

      {/* Phase B: Target Response Telemetry */}
      {response && (
        <div className="space-y-1">
          <div className="flex items-center justify-between text-[11px] font-bold text-slate-500 uppercase tracking-wider">
            <span className="flex items-center gap-1">
              <span className="material-symbols-outlined text-xs text-slate-600">smart_toy</span>
              Target Model Output
            </span>
            <span className="font-mono text-[10px] text-slate-400 font-normal">Phase B | Model Execution</span>
          </div>
          <div
            className={clsx(
              'p-3 rounded-lg border text-xs font-mono whitespace-pre-wrap break-words leading-relaxed select-text',
              isTimeoutOrError
                ? 'bg-amber-50/60 border-amber-200 text-amber-900'
                : isSafe
                ? 'bg-slate-50/80 border-slate-200 text-slate-800'
                : 'bg-rose-50/60 border-rose-200 text-rose-950 font-semibold'
            )}
          >
            {response.text}
          </div>
        </div>
      )}

      {/* Phase C: Independent Judge Verdict & Rationale */}
      {response?.rationale && (
        <div className="p-3 rounded-lg bg-sky-50/60 border border-sky-200/90 text-xs space-y-1">
          <div className="flex items-center justify-between text-[11px] font-bold text-[#0e61a1] uppercase tracking-wider">
            <span className="flex items-center gap-1">
              <span className="material-symbols-outlined text-xs">gavel</span>
              Independent Judge Audit ({response?.judge_model || 'Configured Judge'})
            </span>
            <span className="font-mono text-[10px] text-sky-700 font-normal">Dual-Phase Gate</span>
          </div>
          <p className="text-slate-700 text-xs leading-relaxed font-sans">
            {response.rationale}
          </p>
        </div>
      )}
    </motion.div>
  );
}
