import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

export default function RecentScansTable({ scans }) {
  const navigate = useNavigate();

  return (
    <section className="bg-white border border-slate-200/90 rounded-xl shadow-xs overflow-hidden">
      <div className="p-5 border-b border-slate-200/80 flex justify-between items-center bg-slate-50/50">
        <div>
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-800 flex items-center gap-2">
            <span className="material-symbols-outlined text-[#0e61a1] text-lg">assessment</span>
            Recent Target Evaluation Register
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Audit history of executed adversarial safety scans and certificate issuance records.
          </p>
        </div>
        <button
          onClick={() => navigate('/connect')}
          className="text-xs font-semibold text-[#0e61a1] hover:text-[#0b4e82] flex items-center gap-1 transition-colors"
        >
          <span>Connect New Bot</span>
          <span className="material-symbols-outlined text-sm">arrow_forward</span>
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-50/70 border-b border-slate-200/80 text-[11px] font-bold uppercase tracking-wider text-slate-500 font-mono">
              <th className="py-3 px-5">Target System</th>
              <th className="py-3 px-5">Evaluation Date</th>
              <th className="py-3 px-5">Trust Score</th>
              <th className="py-3 px-5">Pipeline Status</th>
              <th className="py-3 px-5 text-right">Audit Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-xs">
            {scans.length === 0 ? (
              <tr>
                <td colSpan={5} className="py-12 text-center text-slate-400">
                  <span className="material-symbols-outlined text-3xl mb-2 text-slate-300 block">
                    inventory_2
                  </span>
                  <p className="text-xs font-semibold text-slate-600">No evaluation audits recorded yet</p>
                  <p className="text-[11px] text-slate-400 mt-0.5">
                    Connect an authorized chatbot endpoint and launch an evaluation to generate safety certificates.
                  </p>
                </td>
              </tr>
            ) : (
              scans.map((scan, i) => {
                const isCompleted = scan.status === 'completed' || scan.state === 'COMPLETED';
                const isRunning = scan.status === 'running' || scan.state === 'RUNNING';

                const score = scan.trustScore;
                let scoreBadge = (
                  <span className="text-slate-400 font-mono text-[11px]">Pending Run</span>
                );

                if (score !== null && score !== undefined) {
                  const isSafe = score >= 80;
                  scoreBadge = (
                    <span
                      className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-xs font-bold font-sans tabular-nums border ${
                        isSafe
                          ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                          : 'bg-amber-50 text-amber-800 border-amber-200'
                      }`}
                    >
                      <span>{score}%</span>
                      <span className="text-[10px] font-medium opacity-80">
                        {isSafe ? 'Compliant' : 'Review'}
                      </span>
                    </span>
                  );
                }

                return (
                  <motion.tr
                    key={scan.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: i * 0.04 }}
                    className="hover:bg-slate-50/80 transition-colors"
                  >
                    <td className="py-3.5 px-5">
                      <div className="font-semibold text-slate-900">{scan.name}</div>
                      <div className="text-[10px] font-mono text-slate-400">{scan.id.slice(0, 8)}</div>
                    </td>
                    <td className="py-3.5 px-5 text-slate-600 font-mono text-[11px]">
                      {scan.date}
                    </td>
                    <td className="py-3.5 px-5">
                      {scoreBadge}
                    </td>
                    <td className="py-3.5 px-5">
                      <div className="flex items-center gap-1.5">
                        {isRunning ? (
                          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-[#0e61a1] bg-sky-50 border border-sky-200 px-2 py-0.5 rounded">
                            <span className="w-1.5 h-1.5 rounded-full bg-[#0e61a1] animate-pulse" />
                            Running ({scan.progressText})
                          </span>
                        ) : isCompleted ? (
                          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-800 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded">
                            <span className="material-symbols-outlined text-xs text-emerald-600">check</span>
                            Completed
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-slate-600 bg-slate-100 border border-slate-200 px-2 py-0.5 rounded">
                            {scan.state || 'Queued'}
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="py-3.5 px-5 text-right">
                      <div className="flex items-center justify-end gap-2">
                        {isCompleted ? (
                          <button
                            onClick={() => navigate(`/report/${scan.id}`)}
                            className="text-xs font-semibold px-3 py-1 bg-white hover:bg-slate-50 text-slate-800 border border-slate-200 rounded-lg transition-all shadow-2xs flex items-center gap-1"
                          >
                            <span className="material-symbols-outlined text-xs text-[#0e61a1]">verified</span>
                            <span>Certificate</span>
                          </button>
                        ) : (
                          <button
                            onClick={() => navigate(`/simulation?jobId=${scan.id}`)}
                            className="text-xs font-semibold px-3 py-1 bg-[#0e61a1] hover:bg-[#0b4e82] text-white rounded-lg transition-all shadow-xs flex items-center gap-1"
                          >
                            <span className="material-symbols-outlined text-xs">play_arrow</span>
                            <span>Telemetry</span>
                          </button>
                        )}
                      </div>
                    </td>
                  </motion.tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
