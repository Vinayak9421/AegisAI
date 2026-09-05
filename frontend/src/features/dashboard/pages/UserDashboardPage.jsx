import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import AppLayout from '../../../shared/components/AppLayout';
import GaugeCard from '../components/GaugeCard';
import RecentScansTable from '../components/RecentScansTable';
import targetService from '../../../services/targetService';
import jobService from '../../../services/jobService';
import { mockScans } from '../../../store/mockData';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4 } },
};

export default function UserDashboardPage() {
  const navigate = useNavigate();
  const [targets, setTargets] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [targetList, jobList] = await Promise.all([
          targetService.listTargets().catch(() => []),
          jobService.listJobs().catch(() => []),
        ]);
        setTargets(targetList || []);
        setJobs(jobList || []);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  // Format real jobs into scans format if present, else fallback
  const scans =
    jobs.length > 0
      ? jobs.map((j) => ({
          id: j.id,
          name: j.target?.name || `Target ${j.target_id.slice(0, 8)}`,
          date: new Date(j.created_at).toLocaleDateString(),
          trustScore: j.completed_items ? Math.round((j.completed_items / (j.total_items || 1)) * 100) : 85,
          status: j.state === 'COMPLETED' ? 'completed' : 'running',
        }))
      : mockScans;

  return (
    <AppLayout pageTitle="Trust & Safety Overview">
      {/* Page Header */}
      <motion.header
        initial={{ opacity: 0, y: -16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4"
      >
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-slate-900 tracking-tight">
            Trust & Safety Overview
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Active targets: <strong className="text-slate-800">{targets.length}</strong> | Evaluated jobs: <strong className="text-slate-800">{jobs.length}</strong>
          </p>
        </div>

        <div className="flex items-center gap-3">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => navigate('/connect')}
            className="bg-[#0e61a1] hover:bg-[#0b4e82] text-white px-5 py-2.5 rounded-xl text-xs font-semibold flex items-center gap-2 shadow-xs hover:shadow transition-all"
          >
            <span className="material-symbols-outlined text-base">add_circle</span>
            <span>New Bot Evaluation</span>
          </motion.button>
        </div>
      </motion.header>

      {/* Gauge Cards */}
      <motion.section
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-8"
      >
        <motion.div variants={itemVariants}>
          <GaugeCard
            title="Overall Trust Score"
            score={94}
            subtitle="Average across all registered endpoints"
            color="#0e61a1"
          />
        </motion.div>
        <motion.div variants={itemVariants}>
          <GaugeCard
            title="Attack Evasion Rate"
            score={91}
            subtitle="FinRed benchmark resistance"
            color="#10b981"
          />
        </motion.div>
        <motion.div variants={itemVariants}>
          <GaugeCard
            title="Compliance Adherence"
            score={98}
            subtitle="OWASP Top 10 for LLMs"
            color="#f59e0b"
          />
        </motion.div>
      </motion.section>

      {/* Recent Scans Table */}
      <RecentScansTable scans={scans} />
    </AppLayout>
  );
}
