import { motion, AnimatePresence } from 'framer-motion';
import StatusBadge from './StatusBadge';

const rowVariants = {
  hidden: { opacity: 0, y: 8 },
  visible: (i) => ({ opacity: 1, y: 0, transition: { delay: i * 0.07, duration: 0.3 } }),
};

function TrustScoreBar({ score }) {
  const color = score >= 90 ? '#10B981' : score >= 75 ? '#F59E0B' : '#ba1a1a';
  return (
    <div className="flex items-center gap-2">
      <span className={`font-medium ${score < 75 ? 'text-error' : 'text-on-surface'}`}>{score}</span>
      <div className="w-16 h-1.5 bg-surface-variant rounded-full overflow-hidden">
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

export default function EvaluationTable({ evaluations }) {
  return (
    <div className="bg-surface rounded-xl border border-surface-variant shadow-ice overflow-hidden">
      {/* Table Header */}
      <div className="p-6 border-b border-surface-variant flex justify-between items-center bg-surface-bright">
        <h3 className="text-title-lg font-bold text-primary">Recent Evaluations</h3>
        <div className="flex gap-2">
          <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
            className="px-4 py-2 border border-outline-variant rounded-lg text-body-md text-on-surface-variant hover:bg-surface-container transition-colors flex items-center gap-2">
            <span className="material-symbols-outlined text-[18px]">filter_list</span> Filter
          </motion.button>
          <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
            className="px-4 py-2 border border-outline-variant rounded-lg text-body-md text-on-surface-variant hover:bg-surface-container transition-colors flex items-center gap-2">
            <span className="material-symbols-outlined text-[18px]">download</span> Export
          </motion.button>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-surface-container-low text-label-md text-on-surface-variant uppercase tracking-wider">
              {['Client / Project', 'Model', 'Trust Score', 'Status', 'Last Run', 'Actions'].map((h, i) => (
                <th key={h} className={`p-4 font-medium border-b border-surface-variant ${i === 5 ? 'text-right' : ''}`}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="text-body-md text-on-surface divide-y divide-surface-variant">
            <AnimatePresence>
              {evaluations.map((row, i) => (
                <motion.tr
                  key={row.id}
                  custom={i}
                  variants={rowVariants}
                  initial="hidden"
                  animate="visible"
                  className={`hover:bg-surface-container-lowest transition-colors ${row.status === 'critical' ? 'bg-error-container/10' : ''}`}
                >
                  <td className="p-4">
                    <div className="font-medium text-primary">{row.client}</div>
                    <div className="text-label-md text-outline">{row.project}</div>
                  </td>
                  <td className="p-4">{row.model}</td>
                  <td className="p-4"><TrustScoreBar score={row.trustScore} /></td>
                  <td className="p-4"><StatusBadge status={row.status} /></td>
                  <td className="p-4 text-outline">{row.lastRun}</td>
                  <td className="p-4 text-right">
                    <motion.button whileHover={{ scale: 1.1 }} className="p-1 text-on-surface-variant hover:text-primary transition-colors">
                      <span className="material-symbols-outlined">more_vert</span>
                    </motion.button>
                  </td>
                </motion.tr>
              ))}
            </AnimatePresence>
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="p-4 border-t border-surface-variant bg-surface-bright flex justify-between items-center text-label-md text-outline">
        <span>Showing 1 to {evaluations.length} of 842 entries</span>
        <div className="flex gap-1">
          {['Prev', '1', '2', '3', 'Next'].map((p) => (
            <button key={p} className={`px-2.5 py-1 border border-outline-variant rounded hover:bg-surface-container transition-colors ${p === '1' ? 'bg-primary text-on-primary border-primary' : ''}`}>{p}</button>
          ))}
        </div>
      </div>
    </div>
  );
}
