import { motion } from 'framer-motion';
import { clsx } from 'clsx';

const variantMap = {
  passed: 'badge-safe',
  critical: 'badge-critical',
  warning: 'badge-warning',
  running: 'badge-running',
  safe: 'badge-safe',
  failed: 'badge-critical',
};

const labelMap = {
  passed: 'Passed',
  critical: 'Critical Fail',
  warning: 'Warning',
  running: 'Running',
  safe: 'Safe',
  failed: 'Failed',
};

export default function StatusBadge({ status, label, className }) {
  return (
    <motion.span
      initial={{ scale: 0.9, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      className={clsx(
        'inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-label-md font-bold',
        variantMap[status] || 'badge-safe',
        className
      )}
    >
      {status === 'running' && (
        <span className="material-symbols-outlined text-[14px] animate-spin">sync</span>
      )}
      {label || labelMap[status] || status}
    </motion.span>
  );
}
