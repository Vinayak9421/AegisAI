import { motion } from 'framer-motion';
import AdminLayout from '../../../shared/components/AdminLayout';
import StatCard from '../components/StatCard';
import EvaluationTable from '../components/EvaluationTable';
import { mockEvaluations } from '../../../store/mockData';

const pageVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { duration: 0.4 } },
};

export default function AdminOverviewPage() {
  return (
    <AdminLayout>
      {/* Header */}
      <header className="h-20 flex items-center justify-between px-6 border-b border-surface-variant bg-surface/70 backdrop-blur-xl z-30 flex-shrink-0">
        <motion.h2
          initial={{ opacity: 0, x: -16 }}
          animate={{ opacity: 1, x: 0 }}
          className="text-headline-md font-bold text-primary"
        >
          System Overview
        </motion.h2>
        <div className="flex items-center gap-4">
          <div className="relative">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-outline text-[18px]">search</span>
            <input
              className="pl-10 pr-4 py-2 bg-surface-container-low border border-outline-variant rounded-lg text-body-md focus:outline-none focus:border-secondary focus:ring-1 focus:ring-secondary transition-colors w-64"
              placeholder="Search evaluations, users..."
              type="text"
            />
          </div>
          <motion.button whileHover={{ scale: 1.05 }} className="p-2 text-on-surface-variant hover:bg-surface-container rounded-full transition-colors relative">
            <span className="material-symbols-outlined">notifications</span>
            <span className="absolute top-2 right-2 w-2 h-2 bg-error rounded-full" />
          </motion.button>
        </div>
      </header>

      {/* Scrollable Canvas */}
      <motion.div
        variants={pageVariants}
        initial="hidden"
        animate="visible"
        className="flex-1 overflow-y-auto p-6"
      >
        <div className="max-w-[1440px] mx-auto space-y-6">
          {/* Stat Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard label="Total Scanned" value="124.5M" icon="data_usage" trend="12%" trendLabel="vs last month" delay={0} />
            <StatCard label="Active Evals" value="842" icon="model_training" trend="5%" trendLabel="vs last month" delay={0.08} />
            <StatCard label="Avg Trust Score" value="94.2" icon="verified_user" trendLabel="Across all active models" delay={0.16} />
            <StatCard label="Critical Issues" value="12" icon="warning" trend="-2" trendLabel="needs immediate action" trendType="error" delay={0.24} />
          </div>

          {/* Evaluations Table */}
          <EvaluationTable evaluations={mockEvaluations} />
        </div>
      </motion.div>
    </AdminLayout>
  );
}
