import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

const statusConfig = {
  completed: { dot: '#10b981', text: 'Completed', textColor: 'text-emerald-700' },
  running: { dot: '#0e61a1', text: 'Running', textColor: 'text-[#0e61a1]', icon: true },
  queued: { dot: '#f59e0b', text: 'Queued', textColor: 'text-amber-700' },
};

const scoreConfig = (score, scan) => {
  if (scan?.status !== 'completed' || score === null || score === undefined) {
    return {
      bg: 'bg-sky-50 border border-sky-200',
      text: 'text-[#0e61a1]',
      label: scan?.progressText ? `${scan.progressText} Done` : 'Evaluating...',
    };
  }
  if (score >= 80) return { bg: 'bg-[#E6F4EA]', text: 'text-[#137333]', label: `${score} - Safe` };
  return { bg: 'bg-[#FCE8E6]', text: 'text-[#C5221F]', label: `${score} - Review` };
};

export default function RecentScansTable({ scans }) {
  const navigate = useNavigate();

  return (
    <section className="bg-surface-container-lowest border border-[#E8F4F8] rounded-xl shadow-ice overflow-hidden">
      <div className="p-6 border-b border-outline-variant/30 flex justify-between items-center">
        <h2 className="text-title-lg font-bold text-primary">Recent Scans</h2>
        <motion.button whileHover={{ scale: 1.02 }} className="text-secondary text-body-md hover:underline">
          View All
        </motion.button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-surface-container-low/50">
              {['Chatbot Name', 'Date', 'Trust Score', 'Status', 'Action'].map((h, i) => (
                <th key={h} className={`py-3 px-6 text-label-md text-on-surface-variant font-medium ${i === 4 ? 'text-right' : ''}`}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-outline-variant/20">
            <AnimatePresence>
              {scans.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-12 text-center text-slate-400">
                    <span className="material-symbols-outlined text-4xl mb-2 text-slate-300 block">
                      hourglass_empty
                    </span>
                    <p className="text-sm font-semibold text-slate-600">No evaluation scans recorded yet</p>
                    <p className="text-xs text-slate-400 mt-1">
                      Connect your chatbot and launch an evaluation to view real-time audit logs and safety certificates.
                    </p>
                  </td>
                </tr>
              ) : (
                scans.map((scan, i) => {
                  const sc = scoreConfig(scan.trustScore, scan);
                  const st = statusConfig[scan.status] || statusConfig.running;
                  return (
                    <motion.tr
                      key={scan.id}
                      initial={{ opacity: 0, x: -12 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.08 }}
                      className="hover:bg-slate-50/70 transition-colors group"
                    >
                      <td className="py-4 px-6 text-sm font-semibold text-slate-800">{scan.name}</td>
                      <td className="py-4 px-6 text-xs text-slate-500">{scan.date}</td>
                      <td className="py-4 px-6">
                        <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold ${sc.bg} ${sc.text}`}>
                          {sc.label}
                        </span>
                      </td>
                      <td className="py-4 px-6">
                        <div className={`flex items-center gap-2 text-xs font-medium ${st?.textColor}`}>
                          {st?.icon ? (
                            <span className="material-symbols-outlined text-[15px] animate-spin text-[#0e61a1]">sync</span>
                          ) : (
                            <span className="w-2 h-2 rounded-full" style={{ backgroundColor: st?.dot }} />
                          )}
                          {st?.text}
                        </div>
                      </td>
                      <td className="py-4 px-6 text-right">
                        <motion.button
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          onClick={() => {
                            if (scan.status === 'completed') {
                              navigate(`/reports/${scan.id}`);
                            } else {
                              navigate(`/simulation?jobId=${scan.id}`);
                            }
                          }}
                          className={`text-xs font-semibold px-3.5 py-1.5 rounded-xl transition-all shadow-2xs ${
                            scan.status === 'completed'
                              ? 'bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-300'
                              : 'bg-sky-50 hover:bg-sky-100 text-[#0e61a1] border border-sky-300'
                          }`}
                        >
                          {scan.status === 'completed' ? 'View Report' : 'Watch Live'}
                        </motion.button>
                      </td>
                    </motion.tr>
                  );
                })
              )}
            </AnimatePresence>
          </tbody>
        </table>
      </div>
    </section>
  );
}
