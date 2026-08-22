import { NavLink, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { clsx } from 'clsx';

const navItems = [
  { label: 'Overview', icon: 'dashboard', to: '/admin/overview' },
  { label: 'Evaluations', icon: 'security', to: '/admin/evaluations' },
  { label: 'Test Suites', icon: 'biotech', to: '/admin/test-suites' },
  { label: 'Users', icon: 'group', to: '/admin/users' },
  { label: 'Settings', icon: 'settings', to: '/admin/settings' },
];

export default function SideNavBar() {
  const navigate = useNavigate();

  return (
    <motion.aside
      initial={{ x: -280, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      className="hidden md:flex fixed left-0 top-0 h-full w-[280px] bg-surface border-r border-outline-variant shadow-sm flex-col py-6 z-40"
    >
      {/* Brand */}
      <div className="px-6 mb-8">
        <h1 className="text-title-lg font-bold text-primary">AegisAI</h1>
        <p className="text-label-md text-on-surface-variant mt-1">Admin Control Center</p>
      </div>

      {/* New Evaluation CTA */}
      <div className="px-4 mb-6">
        <motion.button
          whileHover={{ scale: 1.02, boxShadow: '0 0 15px rgba(14,97,161,0.5)' }}
          whileTap={{ scale: 0.98 }}
          onClick={() => navigate('/connect')}
          className="w-full btn-primary rounded-lg py-3 px-4 flex items-center justify-center gap-2 text-label-md font-bold"
        >
          <span className="material-symbols-outlined text-[18px]">add</span>
          New Evaluation
        </motion.button>
      </div>

      {/* Nav Links */}
      <nav className="flex-1 px-4 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.label}
            to={item.to}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 text-body-md font-medium',
                isActive
                  ? 'text-primary font-bold bg-surface-container-high border-r-4 border-primary scale-95'
                  : 'text-on-surface-variant hover:text-primary hover:bg-surface-container'
              )
            }
          >
            {({ isActive }) => (
              <>
                <span className={clsx('material-symbols-outlined', isActive && 'icon-fill')}>
                  {item.icon}
                </span>
                <span>{item.label}</span>
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Admin Profile */}
      <div className="px-6 mt-auto pt-6 border-t border-outline-variant">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-primary-container flex items-center justify-center text-on-primary-container">
            <span className="material-symbols-outlined icon-fill">person</span>
          </div>
          <div>
            <p className="text-body-md font-medium text-on-surface">Admin User</p>
            <p className="text-label-md text-on-surface-variant">System Admin</p>
          </div>
        </div>
      </div>
    </motion.aside>
  );
}
