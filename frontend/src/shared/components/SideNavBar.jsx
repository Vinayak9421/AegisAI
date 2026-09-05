import { NavLink, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { clsx } from 'clsx';
import toast from 'react-hot-toast';
import { useAuth } from '../../store/AuthContext';

export default function SideNavBar({ collapsed, onToggleCollapse, mobileOpen, onCloseMobile }) {
  const navigate = useNavigate();
  const { user, isAdmin, logout } = useAuth();

  const handleLogout = () => {
    logout();
    toast.success('Signed out successfully');
    navigate('/login');
  };

  // Strictly filter navigation items by role
  // Normal users do NOT see Threat Benchmarks/Catalog or Admin configuration tools
  const navItems = isAdmin
    ? [
        { label: 'Overview', icon: 'dashboard', to: '/admin/overview' },
        { label: 'Threat Benchmarks', icon: 'biotech', to: '/admin/test-suites' },
        { label: 'Live Simulation', icon: 'bug_report', to: '/simulation' },
        { label: 'Connect Target', icon: 'add_link', to: '/connect' },
      ]
    : [
        { label: 'Dashboard', icon: 'dashboard', to: '/user/dashboard' },
        { label: 'Connect Bot', icon: 'add_link', to: '/connect' },
        { label: 'Live Simulation', icon: 'bug_report', to: '/simulation' },
        { label: 'Safety Reports', icon: 'verified', to: '/report/AEGIS-77X-992' },
      ];

  const sidebarContent = (
    <div className="flex flex-col h-full py-5 text-slate-700 select-none">
      {/* Brand Header */}
      <div className={clsx('flex items-center mb-6 px-4', collapsed ? 'justify-center' : 'justify-between')}>
        <div className="flex items-center gap-3 overflow-hidden">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-[#001c40] via-[#0e61a1] to-[#38bdf8] flex items-center justify-center text-white shadow-md shadow-sky-900/20 shrink-0">
            <span className="material-symbols-outlined text-xl">security</span>
          </div>
          {!collapsed && (
            <motion.div
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -10 }}
              className="min-w-0"
            >
              <h1 className="text-lg font-bold text-slate-900 tracking-tight leading-tight">
                AegisAI
              </h1>
              <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                {isAdmin ? 'SOC Admin Portal' : 'Trust & Safety'}
              </p>
            </motion.div>
          )}
        </div>

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

      {/* New Evaluation CTA */}
      <div className={clsx('mb-6', collapsed ? 'px-2' : 'px-4')}>
        <button
          onClick={() => {
            navigate('/connect');
            if (onCloseMobile) onCloseMobile();
          }}
          title="New Bot Evaluation"
          className={clsx(
            'w-full bg-[#0e61a1] hover:bg-[#0b4e82] text-white rounded-xl font-semibold shadow-sm hover:shadow transition-all flex items-center justify-center gap-2',
            collapsed ? 'py-3 px-0' : 'py-2.5 px-4 text-xs'
          )}
        >
          <span className="material-symbols-outlined text-lg">add_circle</span>
          {!collapsed && <span>New Bot Evaluation</span>}
        </button>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 space-y-1.5 overflow-y-auto">
        {navItems.map((item) => (
          <NavLink
            key={item.label}
            to={item.to}
            onClick={() => {
              if (onCloseMobile) onCloseMobile();
            }}
            title={collapsed ? item.label : undefined}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 rounded-xl transition-all duration-150 text-xs font-semibold tracking-wide',
                collapsed ? 'justify-center p-3' : 'px-3.5 py-2.5',
                isActive
                  ? 'bg-sky-50 text-[#0e61a1] shadow-xs border border-sky-200/70 font-bold'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/80'
              )
            }
          >
            {({ isActive }) => (
              <>
                <span
                  className={clsx(
                    'material-symbols-outlined text-xl transition-colors shrink-0',
                    isActive ? 'text-[#0e61a1]' : 'text-slate-500'
                  )}
                >
                  {item.icon}
                </span>
                {!collapsed && <span className="truncate">{item.label}</span>}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Profile & Logout Section */}
      <div className={clsx('mt-auto pt-4 border-t border-slate-200', collapsed ? 'px-2' : 'px-4')}>
        {!collapsed ? (
          <div className="bg-slate-50 rounded-2xl p-3.5 border border-slate-200/80 shadow-xs">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-slate-200 to-sky-100 border border-sky-300/40 flex items-center justify-center text-[#0e61a1] shrink-0 font-bold text-xs shadow-xs">
                <span className="material-symbols-outlined text-lg">
                  {isAdmin ? 'shield_person' : 'person'}
                </span>
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-xs font-bold text-slate-800 truncate" title={user?.email}>
                  {user?.email || (isAdmin ? 'admin@aegis.ai' : 'analyst@bank.com')}
                </p>
                <div className="flex items-center gap-1.5 mt-0.5">
                  <span
                    className={clsx(
                      'text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider',
                      isAdmin
                        ? 'bg-amber-100 text-amber-800 border border-amber-300'
                        : 'bg-sky-100 text-sky-800 border border-sky-300'
                    )}
                  >
                    {isAdmin ? 'Admin' : 'Analyst'}
                  </span>
                </div>
              </div>
            </div>

            {/* Logout Button */}
            <button
              onClick={handleLogout}
              className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-xl text-xs font-semibold text-rose-700 hover:text-white bg-rose-50 hover:bg-rose-600 border border-rose-200 hover:border-rose-600 shadow-2xs transition-all duration-200"
            >
              <span className="material-symbols-outlined text-base">logout</span>
              <span>Sign Out</span>
            </button>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2">
            <div
              className="w-10 h-10 rounded-xl bg-slate-100 border border-slate-200 flex items-center justify-center text-[#0e61a1] font-bold text-xs"
              title={user?.email || 'User'}
            >
              <span className="material-symbols-outlined text-lg">
                {isAdmin ? 'shield_person' : 'person'}
              </span>
            </div>
            <button
              onClick={handleLogout}
              title="Sign Out"
              className="w-10 h-10 rounded-xl flex items-center justify-center text-rose-600 hover:text-white hover:bg-rose-600 border border-rose-200 hover:border-rose-600 transition-colors"
            >
              <span className="material-symbols-outlined text-base">logout</span>
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
          'hidden md:block fixed left-0 top-0 h-full bg-white/95 backdrop-blur-xl border-r border-slate-200 shadow-sm z-40 transition-all duration-300 ease-in-out',
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
              className="fixed inset-0 bg-slate-900 z-50 md:hidden"
            />
            <motion.aside
              initial={{ x: -280 }}
              animate={{ x: 0 }}
              exit={{ x: -280 }}
              transition={{ duration: 0.25, ease: 'easeOut' }}
              className="fixed left-0 top-0 h-full w-[260px] bg-white border-r border-slate-200 shadow-2xl z-50 md:hidden"
            >
              {sidebarContent}
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
