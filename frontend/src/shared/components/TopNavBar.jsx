import { useNavigate } from 'react-router-dom';
import { clsx } from 'clsx';
import toast from 'react-hot-toast';
import { useAuth } from '../../store/AuthContext';

export default function TopNavBar({ collapsed, onToggleCollapse, onToggleMobile, pageTitle }) {
  const navigate = useNavigate();
  const { user, isAdmin, logout, isAuthenticated } = useAuth();

  const handleLogout = () => {
    logout();
    toast.success('Signed out successfully');
    navigate('/login');
  };

  return (
    <header className="sticky top-0 z-30 flex justify-between items-center px-4 md:px-8 h-16 bg-white/85 backdrop-blur-md border-b border-slate-200/80 shadow-2xs select-none">
      {/* Left: Sidebar Toggle & Page Title */}
      <div className="flex items-center gap-3 md:gap-4">
        {/* Mobile Hamburger Toggle */}
        <button
          onClick={onToggleMobile}
          className="flex md:hidden p-2 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors"
          title="Toggle Navigation Menu"
        >
          <span className="material-symbols-outlined text-2xl">menu</span>
        </button>

        {/* Desktop Quick Toggle */}
        <button
          onClick={onToggleCollapse}
          className="hidden md:flex p-1.5 rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-colors"
          title={collapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
        >
          <span className="material-symbols-outlined text-xl">
            {collapsed ? 'menu_open' : 'menu'}
          </span>
        </button>

        {/* Workspace Brand / Breadcrumb */}
        <div className="flex items-center gap-2">
          <span className="text-sm md:text-base font-bold text-slate-900 tracking-tight">
            {pageTitle || (isAdmin ? 'Admin Console' : 'Fintech Trust & Safety')}
          </span>
          <span className="hidden sm:inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full ml-2">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            Sentinel Online
          </span>
        </div>
      </div>

      {/* Right: Actions & User Info (NO SHIFTING PAGE BUTTONS) */}
      <div className="flex items-center gap-2.5 md:gap-3">
        {isAuthenticated ? (
          <>
            {/* Quick Action */}
            <button
              onClick={() => navigate('/connect')}
              className="hidden sm:flex items-center gap-1.5 bg-[#0e61a1] hover:bg-[#0b4e82] text-white px-3.5 py-1.5 rounded-xl text-xs font-semibold shadow-xs transition-all"
            >
              <span className="material-symbols-outlined text-base">add_circle</span>
              <span>Connect Target</span>
            </button>

            {/* Role Badge */}
            <div className="flex items-center gap-2 pl-2 border-l border-slate-200">
              <span
                className={clsx(
                  'text-[10px] font-bold px-2.5 py-1 rounded-full uppercase tracking-wider border',
                  isAdmin
                    ? 'bg-amber-50 text-amber-800 border-amber-300'
                    : 'bg-sky-50 text-[#0e61a1] border-sky-200'
                )}
              >
                {isAdmin ? '🛡️ Admin' : '👤 User'}
              </span>

              <span className="hidden lg:inline text-xs text-slate-600 font-medium max-w-[140px] truncate" title={user?.email}>
                {user?.email}
              </span>
            </div>

            {/* Logout Button */}
            <button
              onClick={handleLogout}
              title="Sign Out of Aegis"
              className="flex items-center gap-1 text-rose-700 hover:text-white bg-rose-50 hover:bg-rose-600 border border-rose-200 hover:border-rose-600 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all shadow-2xs"
            >
              <span className="material-symbols-outlined text-base">logout</span>
              <span className="hidden sm:inline">Logout</span>
            </button>
          </>
        ) : (
          <div className="flex items-center gap-2">
            <button
              onClick={() => navigate('/login')}
              className="text-xs font-semibold text-slate-600 hover:text-slate-900 px-3 py-1.5"
            >
              Sign In
            </button>
            <button
              onClick={() => navigate('/register')}
              className="bg-[#0e61a1] hover:bg-[#0b4e82] text-white px-3.5 py-1.5 rounded-xl text-xs font-semibold shadow-xs transition-all"
            >
              Register
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
