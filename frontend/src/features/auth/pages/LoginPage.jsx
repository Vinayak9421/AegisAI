import { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate, Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useAuth } from '../../../store/AuthContext';
import AegisLogo from '../../../shared/components/AegisLogo';

export default function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [activeTab, setActiveTab] = useState('user'); // 'user' | 'admin'
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Quick helper to fill demo credentials
  const fillDemoUser = () => {
    setActiveTab('user');
    setEmail('user@aegis.ai');
    setPassword('User@1234');
    toast.success('Loaded Auditor credentials (user@aegis.ai)');
  };

  const fillDemoAdmin = () => {
    setActiveTab('admin');
    setEmail('admin@aegis.ai');
    setPassword('123456');
    toast.success('Loaded SOC Admin credentials (admin@aegis.ai)');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      toast.error('Please provide both email and password');
      return;
    }

    setSubmitting(true);
    try {
      const res = await login(email, password);
      const user = res?.user || res;
      toast.success(`Authenticated as ${user?.email || email}`);

      if (user?.role === 'ADMIN') {
        navigate('/admin/overview');
      } else {
        navigate('/user/dashboard');
      }
    } catch (err) {
      toast.error(err.message || 'Authentication failed. Please verify credentials.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-[#f8fafc] text-slate-800 relative select-none">
      {/* Subtle Background Architectural Grid */}
      <div className="fixed inset-0 pointer-events-none opacity-40 bg-[radial-gradient(#cbd5e1_1px,transparent_1px)] [background-size:20px_20px]" />

      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, ease: 'easeOut' }}
        className="w-full max-w-md bg-white border border-slate-200/90 rounded-2xl shadow-xs relative z-10 overflow-hidden"
      >
        {/* Security Status Indicator Line */}
        <div className="h-1 w-full bg-[#0e61a1]" />

        <div className="p-7 sm:p-9">
          {/* Official Institutional Brand Header */}
          <div className="text-center mb-7">
            <div className="flex justify-center mb-3">
              <AegisLogo size="xl" showSubtitle={true} subtitleText="FINTECH TRUST & SAFETY GATEWAY" />
            </div>
            <h1 className="text-xl font-serif font-semibold text-slate-900 tracking-tight mt-3">
              Institutional Security Login
            </h1>
            <p className="text-xs text-slate-500 mt-1 leading-relaxed">
              Sign in to access adversarial simulation runs, audit registers, and cryptographic attestation certificates.
            </p>
          </div>

          {/* Role Segmented Selector */}
          <div className="flex bg-slate-100/90 rounded-lg p-1 mb-5 border border-slate-200/80">
            <button
              type="button"
              onClick={() => setActiveTab('user')}
              className={`flex-1 py-2 text-xs font-semibold rounded-md flex items-center justify-center gap-1.5 transition-all ${
                activeTab === 'user'
                  ? 'bg-white text-[#0e61a1] shadow-2xs border border-slate-200/80 font-bold'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <span className="material-symbols-outlined text-sm">badge</span>
              <span>Auditor Portal</span>
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('admin')}
              className={`flex-1 py-2 text-xs font-semibold rounded-md flex items-center justify-center gap-1.5 transition-all ${
                activeTab === 'admin'
                  ? 'bg-white text-[#0e61a1] shadow-2xs border border-slate-200/80 font-bold'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <span className="material-symbols-outlined text-sm">security</span>
              <span>SOC Admin</span>
            </button>
          </div>

          {/* Quick Demo Credentials Bar */}
          <div className="flex items-center justify-between bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 mb-5 text-xs">
            <span className="text-[11px] font-mono text-slate-500 uppercase font-semibold">Demo Fill:</span>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={fillDemoUser}
                className="text-[11px] px-2 py-0.5 rounded bg-white text-slate-700 border border-slate-200 hover:border-slate-300 font-medium transition-colors"
              >
                Auditor
              </button>
              <button
                type="button"
                onClick={fillDemoAdmin}
                className="text-[11px] px-2 py-0.5 rounded bg-white text-slate-700 border border-slate-200 hover:border-slate-300 font-medium transition-colors"
              >
                SOC Admin
              </button>
            </div>
          </div>

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-[11px] font-bold text-slate-700 uppercase tracking-wider mb-1">
                Authorized Email Address
              </label>
              <div className="relative">
                <span className="material-symbols-outlined absolute left-3 top-2.5 text-slate-400 text-lg">
                  mail
                </span>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder={activeTab === 'admin' ? 'admin@aegis.ai' : 'user@aegis.ai'}
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg pl-9 pr-3.5 py-2.5 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:bg-white focus:border-[#0e61a1] focus:ring-1 focus:ring-[#0e61a1] transition-all font-mono"
                />
              </div>
            </div>

            <div>
              <label className="block text-[11px] font-bold text-slate-700 uppercase tracking-wider mb-1">
                Credential Key / Password
              </label>
              <div className="relative">
                <span className="material-symbols-outlined absolute left-3 top-2.5 text-slate-400 text-lg">
                  lock
                </span>
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg pl-9 pr-10 py-2.5 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:bg-white focus:border-[#0e61a1] focus:ring-1 focus:ring-[#0e61a1] transition-all font-mono"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-2.5 text-slate-400 hover:text-slate-600 transition-colors"
                  title={showPassword ? 'Mask Password' : 'Show Password'}
                >
                  <span className="material-symbols-outlined text-base">
                    {showPassword ? 'visibility_off' : 'visibility'}
                  </span>
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={submitting}
              className={`w-full mt-2 py-2.5 rounded-lg font-semibold text-xs flex items-center justify-center gap-2 text-white bg-[#0e61a1] hover:bg-[#0b4e82] shadow-xs transition-colors ${
                submitting ? 'opacity-70 cursor-not-allowed' : ''
              }`}
            >
              {submitting ? (
                <>
                  <div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Verifying Credentials...</span>
                </>
              ) : (
                <>
                  <span>Sign In as {activeTab === 'admin' ? 'SOC Security Admin' : 'Quantitative Auditor'}</span>
                  <span className="material-symbols-outlined text-base">arrow_forward</span>
                </>
              )}
            </button>
          </form>

          {/* Footer Registration & Compliance Note */}
          <div className="mt-6 pt-5 border-t border-slate-100 flex flex-col gap-3 text-center text-xs text-slate-500">
            <div>
              Need enterprise organization access?{' '}
              <Link to="/register" className="text-[#0e61a1] hover:text-[#0b4e82] font-semibold transition-colors">
                Register Workspace
              </Link>
            </div>

            <div className="text-[10px] font-mono text-slate-400">
              NIST AI RMF 1.0 • FINRA Regulatory Notice 21-25 • SEC Rule 10b-5
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
