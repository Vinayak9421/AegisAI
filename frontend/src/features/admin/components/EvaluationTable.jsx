import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import StatusBadge from './StatusBadge';

const rowVariants = {
  hidden: { opacity: 0, y: 8 },
  visible: (i) => ({ opacity: 1, y: 0, transition: { delay: i * 0.05, duration: 0.25 } }),
};

function TrustScoreBar({ score }) {
  if (score === null || score === undefined) {
    return (
      <span className="text-[11px] text-slate-400 font-medium">Pending Run</span>
    );
  }
  const color = score >= 90 ? '#10B981' : score >= 75 ? '#F59E0B' : '#ef4444';
  return (
    <div className="flex items-center gap-2.5">
      <span className={`text-xs font-bold ${score < 75 ? 'text-rose-600' : 'text-slate-800'}`}>{score}%</span>
      <div className="w-16 h-2 bg-slate-100 border border-slate-200 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${score}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          className="h-full rounded-full"
          style={{ backgroundColor: color }}
        />
      </div>
    </div>
  );
}

export default function EvaluationTable({ evaluations = [] }) {
  const navigate = useNavigate();

  return (
    <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden text-slate-800">
      {/* Table Header */}
      <div className="p-5 border-b border-slate-200 flex justify-between items-center bg-slate-50/60">
        <h3 className="text-sm md:text-base font-bold text-slate-900 flex items-center gap-2">
          <span className="material-symbols-outlined text-[#0e61a1]">shield</span>
          Recent Threat Evaluations ({evaluations.length})
        </h3>
        <div className="flex gap-2">
          <button className="px-3 py-1.5 border border-slate-200 bg-white rounded-xl text-xs font-semibold text-slate-600 hover:text-slate-900 hover:bg-slate-50 transition-colors flex items-center gap-1.5 shadow-2xs">
            <span className="material-symbols-outlined text-[15px]">filter_list</span> Filter
          </button>
          <button className="px-3 py-1.5 border border-slate-200 bg-white rounded-xl text-xs font-semibold text-slate-600 hover:text-slate-900 hover:bg-slate-50 transition-colors flex items-center gap-1.5 shadow-2xs">
            <span className="material-symbols-outlined text-[15px]">download</span> Export
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-50 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
              {['Client / Project', 'Model Target', 'Trust Score', 'Security Status', 'Last Audit', 'Actions'].map((h, i) => (
                <th key={h} className={`p-4 border-b border-slate-200 ${i === 5 ? 'text-right' : ''}`}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="text-xs divide-y divide-slate-100">
            <AnimatePresence>
              {evaluations.length === 0 ? (
                <tr>
                  <td colSpan={6} className="p-12 text-center text-slate-400">
                    <span className="material-symbols-outlined text-4xl mb-2 text-slate-300 block">
                      assignment_late
                    </span>
                    <p className="text-sm font-semibold text-slate-600">No threat evaluations recorded yet</p>
                    <p className="text-xs text-slate-400 mt-1">
                      Connect a chatbot target and trigger an evaluation job to view audit results.
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
                    className={`hover:bg-slate-50/80 transition-colors ${row.status === 'critical' ? 'bg-rose-50/30' : ''}`}
                  >
                    <td className="p-4">
                      <div className="font-bold text-slate-900 hover:text-[#0e61a1] cursor-pointer" onClick={() => navigate(`/report/${row.id}`)}>{row.client}</div>
                      <div className="text-[11px] text-slate-500">{row.project}</div>
                    </td>
                    <td className="p-4 text-slate-600 font-mono text-[11px]">{row.model}</td>
                    <td className="p-4"><TrustScoreBar score={row.trustScore} /></td>
                    <td className="p-4"><StatusBadge status={row.status} /></td>
                    <td className="p-4 text-slate-500">{row.lastRun}</td>
                    <td className="p-4 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        <button
                          onClick={() => navigate(`/report/${row.id}`)}
                          className="px-2.5 py-1.5 bg-sky-50 hover:bg-sky-100 text-[#0e61a1] border border-sky-200 rounded-xl text-xs font-bold flex items-center gap-1.5 transition-all shadow-2xs hover:shadow-xs"
                          title="View Trust & Safety Certificate Report"
                        >
                          <span className="material-symbols-outlined text-[15px]">verified</span>
                          View Report
                        </button>
                        <button
                          onClick={() => navigate('/simulation')}
                          className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
                          title="View Live Simulation"
                        >
                          <span className="material-symbols-outlined text-base">play_circle</span>
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

      {/* Pagination */}
      <div className="p-4 border-t border-slate-200 bg-slate-50/60 flex justify-between items-center text-xs text-slate-500">
        <span>Showing {evaluations.length > 0 ? 1 : 0} to {evaluations.length} of {evaluations.length} entries</span>
        <div className="flex gap-1">
          {['Prev', '1', 'Next'].map((p) => (
            <button
              key={p}
              disabled={evaluations.length === 0}
              className={`px-2.5 py-1 border rounded-lg transition-colors text-xs font-semibold ${
                p === '1' 
                  ? 'bg-[#0e61a1] text-white border-[#0e61a1]' 
                  : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-100 disabled:opacity-40'
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

    </div>
  );
}
