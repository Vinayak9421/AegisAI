import { useNavigate, useLocation, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { clsx } from 'clsx';
import toast from 'react-hot-toast';
import { useAuth } from '../../store/AuthContext';
import AegisLogo from './AegisLogo';

export default function SideNavBar({ collapsed, onToggleCollapse, mobileOpen, onCloseMobile }) {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, isAdmin, logout } = useAuth();

  const handleLogout = () => {
    logout();
    toast.success('Signed out successfully');
    navigate('/login');
  };

  // Filter navigation items by role
  const navItems = isAdmin
    ? [
        { label: 'Dashboard', icon: 'dashboard', to: '/admin/overview' },
        { label: 'Threat Benchmarks', icon: 'biotech', to: '/admin/test-suites' },
        { label: 'Live Simulation', icon: 'bug_report', to: '/simulation' },
        { label: 'Safety Reports', icon: 'verified', to: '/report/latest' },
        { label: 'Connect Target', icon: 'add_link', to: '/connect' },
      ]
    : [
        { label: 'Dashboard', icon: 'dashboard', to: '/user/dashboard' },
        { label: 'Connect Target', icon: 'add_link', to: '/connect' },
        { label: 'Live Simulation', icon: 'bug_report', to: '/simulation' },
        { label: 'Safety Reports', icon: 'verified', to: '/report/latest' },
      ];

  // Robust active route detection
  const isNavActive = (item) => {
    const path = location.pathname;
    if (item.to === '/admin/overview' || item.to === '/user/dashboard') {
      return (
        path === '/admin/overview' ||
        path === '/user/dashboard' ||
        path === '/dashboard' ||
        path === '/admin/evaluations' ||
        path === '/'
      );
    }
    if (item.to.startsWith('/report')) {
      return path.startsWith('/report') || path.startsWith('/reports');
    }
    if (item.to === '/simulation') {
      return path.startsWith('/simulation');
    }
    if (item.to === '/connect') {
      return path.startsWith('/connect');
    }
    if (item.to === '/admin/test-suites') {
      return path.startsWith('/admin/test-suites');
    }
    return path === item.to;
  };

  const sidebarContent = (
    <div className="flex flex-col h-full py-5 text-slate-700 select-none">
      {/* Brand Header with AegisLogo */}
      <div className={clsx('flex items-center mb-6 px-4', collapsed ? 'justify-center' : 'justify-between')}>
        <Link
          to="/dashboard"
          className="flex items-center gap-3 overflow-hidden cursor-pointer group"
          title="AegisAI Control Center"
          onClick={() => {
            if (onCloseMobile) onCloseMobile();
          }}
        >
          {collapsed ? (
            <AegisLogo variant="mark" size="sm" />
          ) : (
            <AegisLogo
              variant="full"
              size="md"
              showSubtitle={true}
              subtitleText={isAdmin ? 'SOC ADMIN PORTAL' : 'FINTECH AUDIT'}
            />
          )}
        </Link>

        {/* Collapse Toggle Button on Desktop */}
        <button
          onClick={onToggleCollapse}
          title={collapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
          className={clsx(
            'hidden md:flex w-8 h-8 rounded-lg items-center justify-center text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-colors',
            collapsed && 'mt-3'
          )}
        >
          <span className="material-symbols-outlined text-lg">
            {collapsed ? 'chevron_right' : 'chevron_left'}
          </span>
        </button>
      </div>

      {/* New Evaluation Action Button */}
      <div className={clsx('mb-5', collapsed ? 'px-2' : 'px-4')}>
        <button
          onClick={() => {
            navigate('/connect');
            if (onCloseMobile) onCloseMobile();
          }}
          title="Connect & Evaluate Target"
          className={clsx(
            'w-full bg-[#0e61a1] hover:bg-[#0b4e82] text-white rounded-lg font-semibold shadow-2xs hover:shadow-xs transition-all flex items-center justify-center gap-2',
            collapsed ? 'py-2.5 px-0' : 'py-2 px-3 text-xs'
          )}
        >
          <span className="material-symbols-outlined text-base">add_circle</span>
          {!collapsed && <span>New Target Evaluation</span>}
        </button>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const active = isNavActive(item);

          return (
            <button
              key={item.label}
              onClick={() => {
                navigate(item.to);
                if (onCloseMobile) onCloseMobile();
              }}
              title={collapsed ? item.label : undefined}
              className={clsx(
                'w-full flex items-center gap-3 rounded-lg transition-all duration-150 text-xs font-semibold tracking-wide text-left',
                collapsed ? 'justify-center p-2.5' : 'px-3 py-2',
                active
                  ? 'bg-sky-50 text-[#0e61a1] border border-sky-200/90 font-bold shadow-2xs'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/80 border border-transparent'
              )}
            >
              <span
                className={clsx(
                  'material-symbols-outlined text-lg transition-colors shrink-0',
                  active ? 'text-[#0e61a1]' : 'text-slate-500'
                )}
              >
                {item.icon}
              </span>
              {!collapsed && <span className="truncate">{item.label}</span>}
            </button>
          );
        })}
      </nav>

      {/* Profile & Logout Section */}
      <div className={clsx('mt-auto pt-4 border-t border-slate-200', collapsed ? 'px-2' : 'px-4')}>
        {!collapsed ? (
          <div className="bg-slate-50 rounded-xl p-3 border border-slate-200/80 shadow-2xs">
            <div className="flex items-center gap-2.5 mb-2.5">
              <div className="w-8 h-8 rounded-lg bg-white border border-slate-200 flex items-center justify-center text-[#0e61a1] shrink-0 font-bold text-xs shadow-2xs">
                <span className="material-symbols-outlined text-base">
                  {isAdmin ? 'shield_person' : 'person'}
                </span>
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-xs font-semibold text-slate-800 truncate" title={user?.email}>
                  {user?.email || (isAdmin ? 'admin@aegis.ai' : 'analyst@bank.com')}
                </p>
                <div className="flex items-center gap-1 mt-0.5">
                  <span
                    className={clsx(
                      'text-[9px] font-mono font-bold px-1.5 py-0.2 rounded uppercase tracking-wider border',
                      isAdmin
                        ? 'bg-amber-50 text-amber-800 border-amber-200'
                        : 'bg-sky-50 text-[#0e61a1] border-sky-200'
                    )}
                  >
                    {isAdmin ? 'SOC Admin' : 'Auditor'}
                  </span>
                </div>
              </div>
            </div>

            {/* Logout Button */}
            <button
              onClick={handleLogout}
              className="w-full flex items-center justify-center gap-1.5 py-1.5 px-2 rounded-lg text-xs font-medium text-rose-700 hover:text-white bg-rose-50 hover:bg-rose-600 border border-rose-200 hover:border-rose-600 shadow-2xs transition-colors"
            >
              <span className="material-symbols-outlined text-sm">logout</span>
              <span>Sign Out</span>
            </button>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2">
            <div
              className="w-8 h-8 rounded-lg bg-slate-100 border border-slate-200 flex items-center justify-center text-[#0e61a1]"
              title={user?.email || 'User Profile'}
            >
              <span className="material-symbols-outlined text-base">
                {isAdmin ? 'shield_person' : 'person'}
              </span>
            </div>
            <button
              onClick={handleLogout}
              title="Sign Out"
              className="w-8 h-8 rounded-lg flex items-center justify-center text-rose-600 hover:text-white hover:bg-rose-600 border border-rose-200 hover:border-rose-600 transition-colors"
            >
              <span className="material-symbols-outlined text-sm">logout</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Fixed Sidebar */}
      <aside
        className={clsx(
          'hidden md:block fixed left-0 top-0 h-full bg-white/95 backdrop-blur-xl border-r border-slate-200 shadow-2xs z-40 transition-all duration-300 ease-in-out print:hidden',
          collapsed ? 'w-[76px]' : 'w-[260px]'
        )}
      >
        {sidebarContent}
      </aside>

      {/* Mobile Drawer */}
      <AnimatePresence>
        {mobileOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.5 }}
              exit={{ opacity: 0 }}
              onClick={onCloseMobile}
              className="fixed inset-0 bg-slate-900 z-50 md:hidden print:hidden"
            />
            <motion.aside
              initial={{ x: -280 }}
              animate={{ x: 0 }}
              exit={{ x: -280 }}
              transition={{ duration: 0.25, ease: 'easeOut' }}
              className="fixed left-0 top-0 h-full w-[260px] bg-white border-r border-slate-200 shadow-2xl z-50 md:hidden print:hidden"
            >
              {sidebarContent}
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
