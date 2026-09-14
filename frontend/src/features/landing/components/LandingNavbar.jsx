import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../../store/AuthContext';
import AegisLogo from '../../../shared/components/AegisLogo';

export default function LandingNavbar() {
  const { isAuthenticated, isAdmin, user } = useAuth();

  const scrollToSection = (id) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white/90 backdrop-blur-md border-b border-slate-200/80 transition-all shadow-2xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-5 flex items-center justify-between">
        {/* Brand Logo */}
        <Link to="/" className="flex items-center gap-2 group">
          <AegisLogo size="md" textColor="text-slate-900" showSubtitle={false} />
          <span className="hidden sm:inline-block text-[10px] font-mono uppercase bg-sky-50 text-[#0e61a1] border border-sky-200 px-2 py-0.5 rounded tracking-widest font-semibold ml-1">
            Fintech Gateway
          </span>
        </Link>

        {/* Navigation Links (Desktop) */}
        <nav className="hidden md:flex items-center gap-7 text-xs font-medium text-slate-600 tracking-wide">
          <button
            onClick={() => scrollToSection('threat-pillars')}
            className="hover:text-[#0e61a1] transition-colors cursor-pointer"
          >
            6 Threat Pillars
          </button>
          <button
            onClick={() => scrollToSection('live-demo')}
            className="hover:text-[#0e61a1] transition-colors cursor-pointer flex items-center gap-1.5"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            <span>Interactive Probe</span>
          </button>
          <button
            onClick={() => scrollToSection('capabilities')}
            className="hover:text-[#0e61a1] transition-colors cursor-pointer"
          >
            Capabilities
          </button>
          <button
            onClick={() => scrollToSection('architecture')}
            className="hover:text-[#0e61a1] transition-colors cursor-pointer"
          >
            Dual-Judge Engine
          </button>
          <button
            onClick={() => scrollToSection('workflow')}
            className="hover:text-[#0e61a1] transition-colors cursor-pointer"
          >
            How It Works
          </button>
        </nav>

        {/* Action Buttons */}
        <div className="flex items-center gap-3">
          {isAuthenticated ? (
            <Link
              to={isAdmin ? '/admin/overview' : '/user/dashboard'}
              className="px-4 py-2 bg-[#0e61a1] hover:bg-[#0b4e82] text-white text-xs font-bold rounded-lg shadow-2xs flex items-center gap-1.5 transition-all"
            >
              <span className="material-symbols-outlined text-base">dashboard</span>
              <span>Open Dashboard</span>
            </Link>
          ) : (
            <>
              <Link
                to="/login"
                className="text-xs font-semibold text-slate-700 hover:text-slate-900 px-3 py-1.5 transition-colors"
              >
                Sign In
              </Link>
              <Link
                to="/register"
                className="px-4 py-2 bg-[#0e61a1] hover:bg-[#0b4e82] text-white text-xs font-bold rounded-lg shadow-2xs flex items-center gap-1.5 transition-all"
              >
                <span>Start Free Audit</span>
                <span className="material-symbols-outlined text-sm">arrow_forward</span>
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
