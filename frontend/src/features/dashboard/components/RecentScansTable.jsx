import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

const statusConfig = {
  completed: { dot: '#137333', text: 'Completed', textColor: 'text-on-surface-variant' },
  running: { dot: '#0e61a1', text: 'Running', textColor: 'text-secondary', icon: true },
};

const scoreConfig = (score) => {
  if (!score) return { bg: 'bg-surface-container-high', text: 'text-on-surface-variant', label: '--' };
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
              {scans.map((scan, i) => {
                const sc = scoreConfig(scan.trustScore);
                const st = statusConfig[scan.status];
                return (
                  <motion.tr
                    key={scan.id}
                    initial={{ opacity: 0, x: -12 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.08 }}
                    className="hover:bg-surface-container-lowest transition-colors group"
                  >
                    <td className="py-4 px-6 text-body-md font-medium text-on-surface">{scan.name}</td>
                    <td className="py-4 px-6 text-body-md text-on-surface-variant">{scan.date}</td>
                    <td className="py-4 px-6">
                      <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-label-md font-bold ${sc.bg} ${sc.text}`}>
                        {sc.label}
                      </span>
                    </td>
                    <td className="py-4 px-6">
                      <div className={`flex items-center gap-2 text-body-md ${st?.textColor}`}>
                        {st?.icon ? (
                          <span className="material-symbols-outlined text-[16px] animate-spin">sync</span>
                        ) : (
                          <span className="w-2 h-2 rounded-full" style={{ backgroundColor: st?.dot }} />
                        )}
                        {st?.text}
                      </div>
                    </td>
                    <td className="py-4 px-6 text-right">
                      {scan.status === 'completed' ? (
                        <motion.button
                          whileHover={{ scale: 1.02 }}
                          onClick={() => navigate('/report/AEGIS-77X-992')}
                          className="text-secondary hover:text-primary transition-colors text-body-md font-medium"
                        >
                          View Report
                        </motion.button>
                      ) : (
                        <span className="text-on-surface-variant/50 text-body-md cursor-not-allowed">Processing...</span>
                      )}
                    </td>
                  </motion.tr>
                );
              })}
            </AnimatePresence>
          </tbody>
        </table>
      </div>
    </section>
  );
}
