import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

const roles = [
  {
    value: 'admin',
    title: 'Continue as Admin',
    icon: 'shield_person',
    description:
      'Full access to security protocols, user management, and system-wide evaluation suites. Recommended for Security Operations Center leads.',
    route: '/admin/overview',
  },
  {
    value: 'user',
    title: 'Continue as User',
    icon: 'person',
    description:
      'Standard access to personal dashboards, assigned simulations, and read-only reports. Ideal for analysts and regular team members.',
    route: '/user/dashboard',
  },
];

export default function RoleCard({ role, selected, onSelect }) {
  const isSelected = selected === role.value;

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -6, boxShadow: '0px 12px 32px rgba(11, 37, 69, 0.12)' }}
      whileTap={{ scale: 0.98 }}
      onClick={() => onSelect(role.value)}
      className={`relative cursor-pointer bg-surface rounded-xl border shadow-ice overflow-hidden flex flex-col h-full transition-all duration-300 ${
        isSelected ? 'border-secondary border-2 bg-secondary-fixed/10' : 'border-[#E8F4F8]'
      }`}
    >
      {/* Glacier bar */}
      <motion.div
        className="h-3 w-full"
        animate={{ background: isSelected ? 'linear-gradient(135deg, #13315c 0%, #a1cedc 100%)' : '#e0e3e5' }}
        transition={{ duration: 0.3 }}
      />

      <div className="p-8 flex flex-col items-center text-center flex-grow">
        {/* Icon */}
        <motion.div
          animate={{
            backgroundColor: isSelected ? '#13315c' : '#d1e4ff',
            color: isSelected ? '#ffffff' : '#001d36',
          }}
          transition={{ duration: 0.3 }}
          className="w-16 h-16 rounded-full flex items-center justify-center mb-6"
        >
          <span className="material-symbols-outlined icon-fill text-4xl">{role.icon}</span>
        </motion.div>

        <h2 className="text-headline-md font-bold text-primary mb-3">{role.title}</h2>
        <p className="text-body-md text-on-surface-variant">{role.description}</p>
      </div>

      {/* Selection indicator */}
      <AnimatePresence>
        {isSelected && (
          <motion.div
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.5 }}
            className="absolute top-4 right-4 text-secondary"
          >
            <span className="material-symbols-outlined icon-fill">check_circle</span>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export function RoleSelectionPage() {
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleProceed = () => {
    if (!selected) return;
    setLoading(true);
    const route = roles.find((r) => r.value === selected)?.route;
    setTimeout(() => navigate(route || '/user/dashboard'), 1200);
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-surface-bright text-on-surface">
      {/* Background ambient */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute -top-40 -left-40 w-96 h-96 bg-secondary/5 rounded-full blur-3xl" />
        <div className="absolute -bottom-40 -right-40 w-96 h-96 bg-[#a1cedc]/10 rounded-full blur-3xl" />
      </div>

      <div className="w-full max-w-4xl mx-auto flex flex-col items-center relative z-10">
        {/* Logo / Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-12 text-center"
        >
          <div className="w-24 h-24 mx-auto mb-6 rounded-2xl glacier-gradient flex items-center justify-center shadow-ice-deep">
            <span className="material-symbols-outlined icon-fill text-white text-5xl">security</span>
          </div>
          <h1 className="text-display-lg font-bold text-primary tracking-tight">Select Your Role</h1>
          <p className="text-body-lg text-on-surface-variant mt-2 max-w-lg mx-auto">
            Choose your access level to enter the AegisAI Control Center. Your role determines your permissions and available tools.
          </p>
        </motion.div>

        {/* Role Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 w-full max-w-3xl mb-8">
          {roles.map((role, i) => (
            <motion.div
              key={role.value}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.15 + 0.2 }}
            >
              <RoleCard role={role} selected={selected} onSelect={setSelected} />
            </motion.div>
          ))}
        </div>

        {/* Proceed Button */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="w-full flex justify-center"
        >
          <motion.button
            whileHover={selected ? { scale: 1.02, boxShadow: '0 0 20px rgba(14,97,161,0.4)' } : {}}
            whileTap={selected ? { scale: 0.97 } : {}}
            onClick={handleProceed}
            disabled={!selected || loading}
            className="btn-primary rounded-xl px-10 py-4 text-title-lg font-semibold flex items-center gap-3 min-w-[280px] justify-center"
          >
            {loading ? (
              <>
                <span className="material-symbols-outlined animate-spin">refresh</span>
                Processing...
              </>
            ) : (
              <>
                Proceed to Dashboard
                <motion.span
                  animate={selected ? { x: [0, 4, 0] } : {}}
                  transition={{ repeat: Infinity, duration: 1.5 }}
                  className="material-symbols-outlined"
                >
                  arrow_forward
                </motion.span>
              </>
            )}
          </motion.button>
        </motion.div>
      </div>
    </div>
  );
}
