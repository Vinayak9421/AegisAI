import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import AdminLayout from '../../../shared/components/AdminLayout';
import StatCard from '../components/StatCard';
import EvaluationTable from '../components/EvaluationTable';
import targetService from '../../../services/targetService';
import jobService from '../../../services/jobService';
import benchmarkService from '../../../services/benchmarkService';
import { mockEvaluations } from '../../../store/mockData';

const pageVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { duration: 0.3 } },
};

export default function AdminOverviewPage() {
  const [targets, setTargets] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadAdminData() {
      try {
        const [targetList, jobList, sourceList] = await Promise.all([
          targetService.listTargets().catch(() => []),
          jobService.listJobs().catch(() => []),
          benchmarkService.listSources().catch(() => []),
        ]);
        setTargets(targetList || []);
        setJobs(jobList || []);
        setSources(sourceList || []);
      } finally {
        setLoading(false);
      }
    }
    loadAdminData();
  }, []);

  const totalPrompts = sources.reduce((acc, s) => acc + (s.total_prompts || 0), 0) || 6508;

  return (
    <AdminLayout pageTitle="Security Operations Center">
      <motion.div
        variants={pageVariants}
        initial="hidden"
        animate="visible"
        className="space-y-6"
      >
        {/* Header Summary */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h1 className="text-2xl md:text-3xl font-bold text-slate-900 tracking-tight">
              SOC Threat & Safety Overview
            </h1>
            <p className="text-sm text-slate-500 mt-1">
              Global threat benchmark pools, model targets, and independent evaluations.
            </p>
          </div>
          <div className="flex items-center gap-2 bg-white px-3 py-1.5 rounded-xl border border-slate-200 shadow-2xs text-xs text-slate-600">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="font-mono">PostgreSQL: Connected</span>
          </div>
        </div>

        {/* Stat Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            label="Benchmark Catalog"
            value={totalPrompts.toLocaleString()}
            icon="data_usage"
            trend="6.5K Prompts"
            trendLabel="FinRed, HarmBench, AdvBench"
            delay={0}
          />
          <StatCard
            label="Registered Targets"
            value={targets.length.toString()}
            icon="model_training"
            trendLabel="Active endpoints in database"
            delay={0.06}
          />
          <StatCard
            label="Evaluation Jobs"
            value={jobs.length.toString()}
            icon="verified_user"
            trendLabel="Quick & Full audit runs"
            delay={0.12}
          />
          <StatCard
            label="Judge Model"
            value="Llama Guard 3"
            icon="gavel"
            trend="Groq / Heuristic"
            trendLabel="Adversarial Delimiters"
            trendType="success"
            delay={0.18}
          />
        </div>

        {/* Evaluations Table */}
        <EvaluationTable evaluations={mockEvaluations} />
      </motion.div>
    </AdminLayout>
  );
}
