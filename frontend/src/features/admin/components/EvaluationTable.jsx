import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import StatusBadge from './StatusBadge';

const rowVariants = {
  hidden: { opacity: 0, y: 6 },
  visible: (i) => ({ opacity: 1, y: 0, transition: { delay: i * 0.04, duration: 0.2 } }),
};

function TrustScoreBar({ score }) {
  if (score === null || score === undefined) {
    return (
      <span className="text-[11px] font-mono text-slate-400 font-medium">PENDING RUN</span>
    );
  }
  const isHigh = score >= 90;
  const isModerate = score >= 75 && score < 90;

  return (
    <div className="flex items-center gap-2.5">
      <span
        className={`text-xs font-mono font-bold tabular-nums ${
          isHigh ? 'text-emerald-700' : isModerate ? 'text-amber-700' : 'text-rose-700'
        }`}
      >
        {score}%
      </span>
      <div className="w-20 h-1.5 bg-slate-100 border border-slate-200 rounded overflow-hidden">
        <div
          className={`h-full transition-all duration-500 ${
            isHigh ? 'bg-emerald-600' : isModerate ? 'bg-amber-500' : 'bg-rose-600'
          }`}
          style={{ width: `${Math.max(score, 5)}%` }}
        />
      </div>
    </div>
  );
}

export default function EvaluationTable({ evaluations = [] }) {
  const navigate = useNavigate();

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-2xs overflow-hidden text-slate-800">
      {/* Table Header Controls */}
      <div className="p-4 border-b border-slate-200 flex justify-between items-center bg-slate-50/70">
        <div className="flex items-center gap-2.5">
          <span className="material-symbols-outlined text-[#0e61a1] text-lg">shield</span>
          <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
            Verified Threat Evaluations ({evaluations.length})
          </h3>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[11px] font-mono text-slate-500">
            Real-Time Audit Register
          </span>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-100/60 text-[10px] font-mono font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200">
              <th className="p-3.5 pl-4">Target Application</th>
              <th className="p-3.5">Model Architecture</th>
              <th className="p-3.5">Composite Trust Score</th>
              <th className="p-3.5">Audit Verdict</th>
              <th className="p-3.5">Last Audit (UTC)</th>
              <th className="p-3.5 pr-4 text-right">Audit Actions</th>
            </tr>
          </thead>
          <tbody className="text-xs divide-y divide-slate-100">
            <AnimatePresence>
              {evaluations.length === 0 ? (
                <tr>
                  <td colSpan={6} className="p-12 text-center text-slate-400">
                    <span className="material-symbols-outlined text-4xl mb-2 text-slate-300 block">
                      inventory_2
                    </span>
                    <p className="text-xs font-bold text-slate-700">No Threat Evaluations Recorded</p>
                    <p className="text-[11px] text-slate-500 mt-1 max-w-sm mx-auto">
                      Connect a target LLM endpoint and execute an adversarial scan to generate verified Trust & Safety records.
                    </p>
                  </td>
                </tr>
              ) : (
                evaluations.map((row, i) => (
                  <motion.tr
                    key={row.id}
                    custom={i}
                    variants={rowVariants}
                    initial="hidden"
                    animate="visible"
                    className="hover:bg-slate-50/80 transition-colors"
                  >
                    <td className="p-3.5 pl-4">
                      <div
                        onClick={() => navigate(`/report/${row.id}`)}
                        className="font-bold text-slate-900 hover:text-[#0e61a1] cursor-pointer transition-colors"
                      >
                        {row.project || row.client}
                      </div>
                      <div className="text-[10px] font-mono text-slate-400 mt-0.5">
                        ID: {row.id.slice(0, 8)}
                      </div>
                    </td>
                    <td className="p-3.5 font-mono text-[11px] text-slate-700">
                      {row.model}
                    </td>
                    <td className="p-3.5">
                      <TrustScoreBar score={row.trustScore} />
                    </td>
                    <td className="p-3.5">
                      <StatusBadge status={row.status} />
                    </td>
                    <td className="p-3.5 font-mono text-[11px] text-slate-500">
                      {row.lastRun}
                    </td>
                    <td className="p-3.5 pr-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => navigate(`/report/${row.id}`)}
                          className="px-2.5 py-1 bg-white hover:bg-slate-50 text-[#0e61a1] border border-slate-300 hover:border-[#0e61a1] rounded text-[11px] font-bold flex items-center gap-1 transition-all shadow-2xs"
                          title="Open Verified Audit Certificate"
                        >
                          <span className="material-symbols-outlined text-[13px]">verified</span>
                          <span>Certificate</span>
                        </button>
                        <button
                          onClick={() => navigate(`/simulation?jobId=${row.id}`)}
                          className="p-1 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded transition-colors"
                          title="Open Pipeline Trace Logs"
                        >
                          <span className="material-symbols-outlined text-[16px]">timeline</span>
                        </button>
                      </div>
                    </td>
                  </motion.tr>
                ))
              )}
            </AnimatePresence>
          </tbody>
        </table>
      </div>

      {/* Pagination / Status footer */}
      <div className="p-3.5 border-t border-slate-200 bg-slate-50/60 flex justify-between items-center text-xs font-mono text-slate-500">
        <span>Displaying {evaluations.length} evaluation record{evaluations.length !== 1 ? 's' : ''}</span>
        <div className="flex items-center gap-1">
          <span className="px-2 py-0.5 bg-white border border-slate-200 rounded text-[11px]">
            Page 1 of 1
          </span>
        </div>
      </div>
    </div>
  );
}
