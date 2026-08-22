import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import TopNavBar from '../../../shared/components/TopNavBar';
import SideNavBar from '../../../shared/components/SideNavBar';
import GaugeCard from '../components/GaugeCard';
import RecentScansTable from '../components/RecentScansTable';
import { mockScans } from '../../../store/mockData';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4 } },
};

export default function UserDashboardPage() {
  const navigate = useNavigate();

  return (
    <div className="bg-background text-on-background min-h-screen flex flex-col md:flex-row">
      <TopNavBar />
      <SideNavBar />

      <main className="flex-1 md:ml-[280px] pt-20 p-6 max-w-[1440px] mx-auto min-h-screen">
        {/* Page Header */}
        <motion.header
          initial={{ opacity: 0, y: -16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4"
        >
          <div>
            <h1 className="text-headline-lg font-bold text-primary">Overview</h1>
            <p className="text-body-md text-on-surface-variant mt-1">Monitor the health and safety of your connected models.</p>
          </div>
          <motion.button
            whileHover={{ scale: 1.02, boxShadow: '0 0 15px rgba(14,97,161,0.3)' }}
            whileTap={{ scale: 0.97 }}
            onClick={() => navigate('/connect')}
            className="btn-primary px-5 py-2.5 rounded-lg text-body-md font-medium flex items-center gap-2"
          >
            <span className="material-symbols-outlined text-[20px]">add_circle</span>
            New Scan
          </motion.button>
        </motion.header>

        {/* Gauge Cards */}
        <motion.section
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-8"
        >
          <motion.div variants={itemVariants}>
            <GaugeCard title="Trust Score" score={84} color="#0e61a1" delay={0} />
          </motion.div>
          <motion.div variants={itemVariants}>
            <GaugeCard title="Provenance" score={78} color="#003743" delay={0.1} />
          </motion.div>
          <motion.div variants={itemVariants}>
            <GaugeCard title="Behavioral Safety" score={92} color="#13315c" delay={0.2} />
          </motion.div>
        </motion.section>

        {/* Recent Scans Table */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <RecentScansTable scans={mockScans} />
        </motion.div>
      </main>
    </div>
  );
}
