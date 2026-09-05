import { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate, Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useAuth } from '../../../store/AuthContext';

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
    toast.success('Filled Demo User credentials');
  };

  const fillDemoAdmin = () => {
    setActiveTab('admin');
    setEmail('admin@aegis.ai');
    setPassword('123456');
    toast.success('Filled Demo Admin credentials (123456)');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      toast.error('Please enter both email and password');
      return;
    }

    setSubmitting(true);
    try {
      const user = await login(email, password);
      toast.success(`Welcome back, ${user.email}!`);

      if (user.role === 'ADMIN') {
        navigate('/admin/overview');
      } else {
        navigate('/user/dashboard');
      }
    } catch (err) {
      toast.error(err.message || 'Authentication failed');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-[#f8fafc] text-slate-800 relative overflow-hidden">
      {/* Background Soft Accents */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute -top-40 -left-40 w-[450px] h-[450px] bg-sky-200/40 rounded-full blur-[100px]" />
        <div className="absolute top-1/2 -right-32 w-[400px] h-[400px] bg-blue-100/50 rounded-full blur-[100px]" />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
        className="w-full max-w-md bg-white border border-slate-200/90 rounded-2xl shadow-xl relative z-10 overflow-hidden"
      >
        {/* Top Glacier Gradient Accent Bar */}
        <div className="h-1.5 w-full bg-gradient-to-r from-[#001c40] via-[#0e61a1] to-[#38bdf8]" />

        <div className="p-8">
          {/* Logo & Header */}
          <div className="text-center mb-8">
            <motion.div
              whileHover={{ scale: 1.05 }}
              className="relative w-14 h-14 mx-auto mb-4"
            >
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-[#001c40] via-[#0e61a1] to-[#38bdf8] flex items-center justify-center text-white shadow-md shadow-sky-900/20">
                <span className="material-symbols-outlined text-white text-3xl">security</span>
              </div>
            </motion.div>
            
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">
              AegisAI Control Center
            </h1>
            <p className="text-xs text-slate-500 mt-1 font-medium tracking-wide uppercase">
              Autonomous Fintech Trust & Safety Platform
            </p>
          </div>

          {/* Role Segment Tabs */}
          <div className="flex bg-slate-100 rounded-xl p-1 mb-6 border border-slate-200">
            <button
              type="button"
              onClick={() => setActiveTab('user')}
              className={`flex-1 py-2 text-xs font-bold rounded-lg flex items-center justify-center gap-1.5 transition-all duration-150 ${
                activeTab === 'user'
                  ? 'bg-white text-[#0e61a1] shadow-xs border border-slate-200/80'
                  : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              <span className="material-symbols-outlined text-base">person</span>
              User Portal
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('admin')}
              className={`flex-1 py-2 text-xs font-bold rounded-lg flex items-center justify-center gap-1.5 transition-all duration-150 ${
                activeTab === 'admin'
                  ? 'bg-white text-[#0e61a1] shadow-xs border border-slate-200/80'
                  : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              <span className="material-symbols-outlined text-base">shield_person</span>
              Admin Portal
            </button>
          </div>

          {/* Quick Demo Autofill helper */}
          <div className="flex items-center justify-between mb-6 px-1">
            <span className="text-xs text-slate-500 font-medium">Quick autofill:</span>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={fillDemoUser}
                className="text-xs px-2.5 py-1 rounded-lg bg-sky-50 text-[#0e61a1] border border-sky-200 hover:bg-sky-100 transition-all font-semibold"
              >
                Demo User
              </button>
              <button
                type="button"
                onClick={fillDemoAdmin}
                className="text-xs px-2.5 py-1 rounded-lg bg-amber-50 text-amber-800 border border-amber-200 hover:bg-amber-100 transition-all font-semibold"
              >
                Demo Admin (123456)
              </button>
            </div>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                Email Address
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
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl pl-10 pr-4 py-2.5 text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:bg-white focus:border-[#0e61a1] transition-all"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                Password
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
                  placeholder="••••••••"
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl pl-10 pr-10 py-2.5 text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:bg-white focus:border-[#0e61a1] transition-all"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-2.5 text-slate-400 hover:text-slate-600 transition-colors"
                >
                  <span className="material-symbols-outlined text-lg">
                    {showPassword ? 'visibility_off' : 'visibility'}
                  </span>
                </button>
              </div>
            </div>

            <motion.button
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.99 }}
              type="submit"
              disabled={submitting}
              className={`w-full mt-2 py-3 rounded-xl font-bold text-sm flex items-center justify-center gap-2 text-white bg-[#0e61a1] hover:bg-[#0b4e82] shadow-sm hover:shadow transition-all ${
                submitting ? 'opacity-70 cursor-not-allowed' : ''
              }`}
            >
              {submitting ? (
                <>
                  <span className="material-symbols-outlined animate-spin text-lg">refresh</span>
                  <span>Authenticating...</span>
                </>
              ) : (
                <>
                  <span>Sign In as {activeTab === 'admin' ? 'Security Admin' : 'Workspace User'}</span>
                  <span className="material-symbols-outlined text-lg">arrow_forward</span>
                </>
              )}
            </motion.button>
          </form>

          {/* Footer links */}
          <div className="mt-6 pt-6 border-t border-slate-100 text-center text-xs text-slate-500">
            Don't have an enterprise account?{' '}
            <Link to="/register" className="text-[#0e61a1] hover:underline font-semibold transition-colors">
              Register your team
            </Link>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
