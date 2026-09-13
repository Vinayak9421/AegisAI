import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import AegisLogo from '../../../shared/components/AegisLogo';

const roles = [
  {
    value: 'admin',
    title: 'SOC Security Administrator',
    badge: 'FULL SYSTEM PRIVILEGES',
    icon: 'shield_person',
    description:
      'Full administrative access to configure threat benchmarks, manage target endpoints, oversee tenant audit logs, and trigger enterprise-wide stress tests.',
    route: '/admin/overview',
  },
  {
    value: 'user',
    title: 'Quantitative Risk Auditor',
    badge: 'EVALUATION & REPORTS',
    icon: 'badge',
    description:
      'Execution of authorized red-teaming evaluations, review of live simulation telemetry traces, and inspection of cryptographic Trust & Safety certificates.',
    route: '/user/dashboard',
  },
];

export function RoleCard({ role, selected, onSelect }) {
  const isSelected = selected === role.value;

  return (
    <div
      onClick={() => onSelect(role.value)}
      className={`relative cursor-pointer bg-white rounded-xl border p-6 transition-all duration-200 flex flex-col justify-between ${
        isSelected
          ? 'border-[#0e61a1] ring-1 ring-[#0e61a1] shadow-xs'
          : 'border-slate-200 hover:border-slate-300 shadow-2xs'
      }`}
    >
      <div>
        <div className="flex items-start justify-between mb-4">
          <div className="w-11 h-11 rounded-lg bg-slate-100 border border-slate-200 flex items-center justify-center text-[#0e61a1]">
            <span className="material-symbols-outlined text-2xl">{role.icon}</span>
          </div>
          <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200">
            {role.badge}
          </span>
        </div>

        <h2 className="text-sm font-bold text-slate-900 mb-1.5">{role.title}</h2>
        <p className="text-xs text-slate-600 leading-relaxed">{role.description}</p>
      </div>

      <div className="mt-5 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
        <span className="text-slate-400 font-mono text-[11px]">
          Target Route: {role.route}
        </span>
        <span
          className={`flex items-center gap-1 font-semibold ${
            isSelected ? 'text-[#0e61a1]' : 'text-slate-400'
          }`}
        >
          {isSelected ? 'Selected' : 'Select'}
          <span className="material-symbols-outlined text-sm">
            {isSelected ? 'check_circle' : 'radio_button_unchecked'}
          </span>
        </span>
      </div>
    </div>
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
    setTimeout(() => navigate(route || '/user/dashboard'), 400);
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-[#f8fafc] text-slate-800 relative select-none">
      {/* Background Architectural Grid */}
      <div className="fixed inset-0 pointer-events-none opacity-40 bg-[radial-gradient(#cbd5e1_1px,transparent_1px)] [background-size:20px_20px]" />

      <div className="w-full max-w-3xl mx-auto flex flex-col items-center relative z-10 py-10">
        {/* Logo / Header */}
        <div className="mb-8 text-center">
          <div className="flex justify-center mb-3">
            <AegisLogo size="xl" showSubtitle={true} subtitleText="OPERATIONAL ROLE SELECTION" />
          </div>
          <h1 className="text-2xl font-serif font-semibold text-slate-900 tracking-tight mt-3">
            Select Workspace Persona
          </h1>
          <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto leading-relaxed">
            Choose your authorized operational profile to configure security benchmarks or review independent model evaluation certificates.
          </p>
        </div>

        {/* Role Cards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full mb-6">
          {roles.map((role) => (
            <RoleCard
              key={role.value}
              role={role}
              selected={selected}
              onSelect={setSelected}
            />
          ))}
        </div>

        {/* Action Button */}
        <div className="w-full flex justify-center">
          <button
            onClick={handleProceed}
            disabled={!selected || loading}
            className={`px-8 py-2.5 rounded-lg text-xs font-semibold flex items-center gap-2 text-white bg-[#0e61a1] hover:bg-[#0b4e82] transition-colors shadow-xs ${
              !selected || loading ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            {loading ? (
              <>
                <div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Redirecting...</span>
              </>
            ) : (
              <>
                <span>Enter Aegis Control Center</span>
                <span className="material-symbols-outlined text-sm">arrow_forward</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

export default RoleSelectionPage;
