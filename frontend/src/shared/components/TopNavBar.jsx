import { Link, useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { clsx } from 'clsx';

const navLinks = [
  { label: 'Dashboard', to: '/user/dashboard' },
  { label: 'Simulation', to: '/simulation' },
  { label: 'Reports', to: '/report/AEGIS-77X-992' },
  { label: 'Help', to: '#' },
];

export default function TopNavBar() {
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <motion.nav
      initial={{ y: -64, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      className="fixed top-0 left-0 w-full z-50 flex justify-between items-center px-6 h-16 bg-surface/70 backdrop-blur-xl border-b border-outline-variant shadow-sm"
    >
      {/* Brand + Nav Links */}
      <div className="flex items-center gap-6">
        <Link to="/" className="text-headline-md font-bold text-primary tracking-tight hover:opacity-80 transition-opacity">
          AegisAI
        </Link>
        <div className="hidden md:flex items-center h-full gap-6">
          {navLinks.map((link) => {
            const isActive = location.pathname === link.to;
            return (
              <Link
                key={link.label}
                to={link.to}
                className={clsx(
                  'text-label-md font-medium transition-all duration-200 relative pb-1',
                  isActive
                    ? 'text-primary font-bold border-b-2 border-primary'
                    : 'text-on-surface-variant hover:text-primary'
                )}
              >
                {link.label}
              </Link>
            );
          })}
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-4">
        <motion.button
          whileHover={{ scale: 1.03 }}
          whileTap={{ scale: 0.97 }}
          onClick={() => navigate('/connect')}
          className="btn-primary hidden sm:flex px-4 py-2 rounded-lg text-label-md font-bold shadow-glow"
        >
          Connect Chatbot
        </motion.button>
        <button className="text-on-surface-variant hover:text-primary transition-colors relative">
          <span className="material-symbols-outlined">notifications</span>
          <span className="absolute top-0 right-0 w-2 h-2 bg-error rounded-full border-2 border-surface" />
        </button>
        <button className="text-on-surface-variant hover:text-primary transition-colors">
          <span className="material-symbols-outlined">account_circle</span>
        </button>
      </div>
    </motion.nav>
  );
}
