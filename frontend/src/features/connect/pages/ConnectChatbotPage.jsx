import { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import TopNavBar from '../../../shared/components/TopNavBar';
import toast from 'react-hot-toast';

const steps = ['Connect', 'Configure', 'Scan', 'Report'];

export default function ConnectChatbotPage() {
  const navigate = useNavigate();
  const [showKey, setShowKey] = useState(false);
  const [apiUrl, setApiUrl] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [testing, setTesting] = useState(false);
  const [hfRepo, setHfRepo] = useState('');

  const handleTest = () => {
    if (!apiUrl) {
      toast.error('Please enter an endpoint URL');
      return;
    }
    setTesting(true);
    setTimeout(() => {
      setTesting(false);
      toast.success('Connection established! ✅');
    }, 1800);
  };

  const canStart = apiUrl && apiKey;

  return (
    <div className="bg-background text-on-surface min-h-screen flex flex-col">
      <TopNavBar />

      <main className="flex-grow pt-24 pb-12 px-4 md:px-6 flex flex-col items-center max-w-[1440px] mx-auto w-full">
        <div className="w-full max-w-4xl">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-12"
          >
            <h1 className="text-headline-lg font-bold text-primary mb-2">Connect Your Chatbot</h1>
            <p className="text-body-lg text-on-surface-variant">
              Configure your environment to begin trust & safety evaluations.
            </p>
          </motion.div>

          {/* Step Wizard */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.15 }}
            className="mb-12"
          >
            <div className="flex items-center justify-between relative">
              <div className="absolute left-0 top-1/2 -translate-y-1/2 w-full h-0.5 bg-surface-variant -z-10" />
              {steps.map((step, i) => (
                <div key={step} className="flex flex-col items-center gap-2">
                  <motion.div
                    initial={{ scale: 0.8 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: i * 0.1 }}
                    className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-label-md border-2 border-background ${
                      i === 0 ? 'bg-primary text-on-primary' : 'bg-surface-variant text-on-surface-variant'
                    }`}
                  >
                    {i + 1}
                  </motion.div>
                  <span className={`text-label-md font-medium px-2 bg-background ${i === 0 ? 'text-primary font-bold' : 'text-on-surface-variant'}`}>
                    {step}
                  </span>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Connection Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-12">
            {/* API Connection */}
            <motion.div
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              whileHover={{ borderColor: '#13315c' }}
              className="bg-surface-container-lowest rounded-xl p-6 border border-[#E8F4F8] shadow-ice relative overflow-hidden group transition-colors"
            >
              <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                <span className="material-symbols-outlined text-[64px]">api</span>
              </div>
              <div className="flex items-center gap-3 mb-6 relative z-10">
                <div className="p-2 bg-primary-container text-on-primary-container rounded-lg">
                  <span className="material-symbols-outlined">link</span>
                </div>
                <h2 className="text-title-lg font-bold text-primary">Connect via API</h2>
              </div>
              <div className="space-y-4 relative z-10">
                <div>
                  <label className="block text-label-md text-on-surface-variant mb-1">Endpoint URL</label>
                  <input
                    value={apiUrl}
                    onChange={(e) => setApiUrl(e.target.value)}
                    className="w-full bg-background border border-outline-variant rounded-lg px-3 py-2 text-body-md focus:border-secondary focus:ring-1 focus:ring-secondary outline-none transition-colors"
                    placeholder="https://api.yourbot.com/v1/chat"
                    type="text"
                  />
                </div>
                <div>
                  <label className="block text-label-md text-on-surface-variant mb-1">API Key</label>
                  <div className="relative">
                    <input
                      value={apiKey}
                      onChange={(e) => setApiKey(e.target.value)}
                      className="w-full bg-background border border-outline-variant rounded-lg px-3 py-2 text-body-md focus:border-secondary focus:ring-1 focus:ring-secondary outline-none transition-colors pr-10"
                      placeholder="sk-..."
                      type={showKey ? 'text' : 'password'}
                    />
                    <button
                      onClick={() => setShowKey(!showKey)}
                      className="absolute right-2 top-1/2 -translate-y-1/2 text-on-surface-variant hover:text-primary"
                    >
                      <span className="material-symbols-outlined text-body-lg">
                        {showKey ? 'visibility' : 'visibility_off'}
                      </span>
                    </button>
                  </div>
                </div>
                <div>
                  <label className="block text-label-md text-on-surface-variant mb-1">Auth Header</label>
                  <select className="w-full bg-background border border-outline-variant rounded-lg px-3 py-2 text-body-md focus:border-secondary outline-none appearance-none">
                    <option>Bearer Token</option>
                    <option>x-api-key</option>
                    <option>Basic Auth</option>
                  </select>
                </div>
                <motion.button
                  whileHover={{ scale: 1.01 }}
                  whileTap={{ scale: 0.99 }}
                  onClick={handleTest}
                  disabled={testing}
                  className="mt-4 w-full py-2 px-4 bg-background border border-[#1B4F8C] text-[#1B4F8C] hover:bg-surface-container-low rounded-lg text-label-md font-bold transition-colors flex items-center justify-center gap-2"
                >
                  {testing ? (
                    <><span className="material-symbols-outlined animate-spin text-[18px]">sync</span> Testing...</>
                  ) : (
                    <><span>Test Connection</span><span className="w-2 h-2 rounded-full bg-secondary pulse-dot" /></>
                  )}
                </motion.button>
              </div>
            </motion.div>

            {/* Local / HuggingFace */}
            <motion.div
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              whileHover={{ borderColor: '#13315c' }}
              className="bg-surface-container-lowest rounded-xl p-6 border border-[#E8F4F8] shadow-ice relative overflow-hidden group transition-colors"
            >
              <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                <span className="material-symbols-outlined text-[64px]">memory</span>
              </div>
              <div className="flex items-center gap-3 mb-6 relative z-10">
                <div className="p-2 bg-tertiary-container text-on-tertiary-container rounded-lg">
                  <span className="material-symbols-outlined">terminal</span>
                </div>
                <h2 className="text-title-lg font-bold text-primary">Local / Hugging Face</h2>
              </div>
              <div className="space-y-4 relative z-10">
                <div className="bg-surface p-4 rounded-lg border border-outline-variant">
                  <h3 className="text-label-md text-primary font-bold mb-2">Prerequisites Checklist</h3>
                  <ul className="space-y-2">
                    <li className="flex items-start gap-2 text-body-md text-on-surface-variant">
                      <span className="material-symbols-outlined text-[16px] text-secondary mt-0.5">check_circle</span>
                      Aegis CLI installed (v2.1+)
                    </li>
                    <li className="flex items-start gap-2 text-body-md text-on-surface-variant">
                      <span className="material-symbols-outlined text-[16px] text-outline mt-0.5">radio_button_unchecked</span>
                      Local agent running on port 8080
                    </li>
                  </ul>
                </div>
                <div>
                  <label className="block text-label-md text-on-surface-variant mb-1">Hugging Face Repo ID (Optional)</label>
                  <input
                    value={hfRepo}
                    onChange={(e) => setHfRepo(e.target.value)}
                    className="w-full bg-background border border-outline-variant rounded-lg px-3 py-2 text-body-md focus:border-secondary focus:ring-1 focus:ring-secondary outline-none transition-colors"
                    placeholder="organization/model-name"
                    type="text"
                  />
                </div>
                <motion.button
                  whileHover={{ scale: 1.01 }}
                  className="w-full py-2 px-4 bg-background border border-[#1B4F8C] text-[#1B4F8C] hover:bg-surface-container-low rounded-lg text-label-md font-bold transition-colors flex items-center justify-center gap-2"
                >
                  <span className="material-symbols-outlined text-[18px]">search</span> Detect Local Agent
                </motion.button>
                <div className="flex justify-center">
                  <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-surface-container text-on-surface-variant text-[10px] uppercase font-bold tracking-wider">
                    <span className="w-1.5 h-1.5 rounded-full bg-outline" /> Not Detected
                  </span>
                </div>
              </div>
            </motion.div>
          </div>

          {/* Start Scan CTA */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: canStart ? 1 : 0.5 }}
            transition={{ duration: 0.3 }}
            className="flex flex-col items-center gap-3"
          >
            <motion.button
              whileHover={canStart ? { scale: 1.02, boxShadow: '0 4px 20px rgba(11,37,69,0.3)' } : {}}
              whileTap={canStart ? { scale: 0.97 } : {}}
              disabled={!canStart}
              onClick={() => navigate('/simulation')}
              className="btn-primary px-8 py-4 rounded-xl text-title-lg font-bold flex items-center gap-3 shadow-ice-deep"
            >
              <span className="material-symbols-outlined">security</span>
              Start Trust & Safety Scan
            </motion.button>
            {!canStart && (
              <p className="text-label-md text-on-surface-variant">Connect an agent to proceed</p>
            )}
          </motion.div>
        </div>
      </main>
    </div>
  );
}
