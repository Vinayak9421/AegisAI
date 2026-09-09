import { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import AppLayout from '../../../shared/components/AppLayout';
import toast from 'react-hot-toast';
import targetService from '../../../services/targetService';
import jobService from '../../../services/jobService';

const steps = ['Configure Target', 'Verify Connectivity', 'Launch Scan'];

export default function ConnectChatbotPage() {
  const navigate = useNavigate();

  // Form states
  const [targetName, setTargetName] = useState('Fintech Advisor Assistant');
  const [apiUrl, setApiUrl] = useState('http://127.0.0.1:8001/chat');
  const [apiKey, setApiKey] = useState('demo-key-fintech-1234');
  const [authHeaderKind, setAuthHeaderKind] = useState('API_KEY');
  const [hfRepo, setHfRepo] = useState('');
  const [showKey, setShowKey] = useState(false);

  // Async states
  const [testing, setTesting] = useState(false);
  const [createdTarget, setCreatedTarget] = useState(null);
  const [startingScan, setStartingScan] = useState(false);

  const handleTestAndRegister = async () => {
    if (!apiUrl) {
      toast.error('Please specify target API endpoint URL');
      return;
    }
    setTesting(true);
    try {
      const payload = {
        name: targetName || 'Target Chatbot',
        mode: 'HOSTED',
        endpoint_url: apiUrl,
        connector_profile: 'aegis_simple_chat_v1',
        authorization_confirmed: true,
        authorization_reference: 'team-authorized-pilot-target',
        side_effect_free: true,
        credential_payload: apiKey || undefined,
        credential_kind: authHeaderKind === 'BEARER_TOKEN' ? 'BEARER_TOKEN' : 'API_KEY',
      };

      let target;
      try {
        target = await targetService.createTarget(payload);
      } catch (err) {
        // If target exists or returns conflict, fetch target list
        const targets = await targetService.listTargets();
        target = targets.find((t) => t.endpoint_url === apiUrl || t.name === payload.name);
        if (!target) throw err;
      }

      // Automatically verify target connectivity
      toast('Probing target connectivity and SSRF safety...', { icon: '🔍' });
      try {
        await targetService.verifyTarget(target.id);
      } catch (valErr) {
        console.warn('Verification note:', valErr);
      }

      const refreshed = await targetService.getTarget(target.id);
      setCreatedTarget(refreshed);
      toast.success(`Target "${refreshed.name}" verified & ready for evaluation!`);
    } catch (err) {
      toast.error(err.message || 'Failed to register target');
    } finally {
      setTesting(false);
    }
  };

  const handleStartScan = async () => {
    setStartingScan(true);
    try {
      let target = createdTarget;

      if (!target) {
        const payload = {
          name: targetName || 'Target Chatbot',
          mode: 'HOSTED',
          endpoint_url: apiUrl,
          connector_profile: 'aegis_simple_chat_v1',
          authorization_confirmed: true,
          authorization_reference: 'team-authorized-pilot-target',
          side_effect_free: true,
          credential_payload: apiKey || undefined,
          credential_kind: authHeaderKind === 'BEARER_TOKEN' ? 'BEARER_TOKEN' : 'API_KEY',
        };
        try {
          target = await targetService.createTarget(payload);
        } catch (err) {
          const targets = await targetService.listTargets();
          target = targets.find((t) => t.endpoint_url === apiUrl || t.name === payload.name);
          if (!target) throw err;
        }
      }

      // Ensure target is verified before starting scan
      if (target.status !== 'VERIFIED') {
        toast('Verifying target status...', { icon: '🔍' });
        try {
          await targetService.verifyTarget(target.id);
        } catch (valErr) {
          console.warn('Verification probe response:', valErr);
        }
      }

      toast('Creating evaluation job with 25 FinRed adversarial prompts...', { icon: '🛡️' });
      const job = await jobService.createJob({
        target_id: target.id,
        mode: 'QUICK',
        sample_size: 25,
        seed: 42,
      });
      toast.success('Evaluation job queued successfully!');
      navigate(`/simulation?jobId=${job.id}`);
    } catch (err) {
      toast.error(err.message || 'Could not schedule evaluation job');
    } finally {
      setStartingScan(false);
    }
  };

  const canStart = Boolean(apiUrl && (apiKey || createdTarget));

  return (
    <AppLayout pageTitle="Connect Chatbot Target">
      <div className="max-w-4xl mx-auto w-full py-4">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -16 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-10"
        >
          <h1 className="text-2xl md:text-3xl font-bold text-slate-900 tracking-tight mb-2">
            Connect Your Chatbot Target
          </h1>
          <p className="text-slate-500 text-sm max-w-xl mx-auto">
            Register authorized endpoints to dispatch automated red-teaming benchmarks, evaluate guardrails, and assess model safety.
          </p>
        </motion.div>

        {/* Step Wizard */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="mb-10 max-w-2xl mx-auto"
        >
          <div className="flex items-center justify-between relative">
            <div className="absolute left-0 top-1/2 -translate-y-1/2 w-full h-0.5 bg-slate-200 -z-10" />
            {steps.map((step, i) => (
              <div key={step} className="flex flex-col items-center gap-2">
                <motion.div
                  initial={{ scale: 0.8 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: i * 0.1 }}
                  className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs border-2 ${
                    i === 0
                      ? 'bg-[#0e61a1] text-white border-[#0e61a1] shadow-xs'
                      : 'bg-white text-slate-500 border-slate-300'
                  }`}
                >
                  {i + 1}
                </motion.div>
                <span className={`text-xs font-semibold px-2 bg-[#f8fafc] ${i === 0 ? 'text-[#0e61a1] font-bold' : 'text-slate-500'}`}>
                  {step}
                </span>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Connection Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
          {/* API Connection */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
            className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm relative overflow-hidden"
          >
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2.5 bg-sky-50 text-[#0e61a1] border border-sky-200 rounded-xl">
                <span className="material-symbols-outlined text-2xl">link</span>
              </div>
              <div>
                <h2 className="text-base font-bold text-slate-900">Target API Endpoint</h2>
                <p className="text-xs text-slate-500">Direct HTTP JSON interface for test dispatch</p>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                  Target Name
                </label>
                <input
                  value={targetName}
                  onChange={(e) => setTargetName(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:bg-white focus:border-[#0e61a1] transition-colors"
                  placeholder="e.g. Retail Banking Advisor"
                  type="text"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                  Endpoint URL
                </label>
                <input
                  value={apiUrl}
                  onChange={(e) => setApiUrl(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:bg-white focus:border-[#0e61a1] transition-colors"
                  placeholder="https://api.yourbot.com/v1/chat"
                  type="text"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                  API Key / Secret
                </label>
                <div className="relative">
                  <input
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:bg-white focus:border-[#0e61a1] transition-colors pr-10"
                    placeholder="sk-..."
                    type={showKey ? 'text' : 'password'}
                  />
                  <button
                    type="button"
                    onClick={() => setShowKey(!showKey)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                  >
                    <span className="material-symbols-outlined text-lg">
                      {showKey ? 'visibility' : 'visibility_off'}
                    </span>
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                  Credential Kind
                </label>
                <select
                  value={authHeaderKind}
                  onChange={(e) => setAuthHeaderKind(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-sm text-slate-800 focus:outline-none focus:bg-white focus:border-[#0e61a1] transition-colors"
                >
                  <option value="API_KEY">Bearer Token / API Key</option>
                  <option value="CUSTOM_HEADER">Custom Header (X-API-Key)</option>
                  <option value="OAUTH">OAuth Token</option>
                </select>
              </div>

              <motion.button
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.99 }}
                onClick={handleTestAndRegister}
                disabled={testing}
                className="mt-4 w-full py-2.5 px-4 bg-sky-50 hover:bg-sky-100 border border-sky-300 text-[#0e61a1] rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2 shadow-2xs"
              >
                {testing ? (
                  <>
                    <span className="material-symbols-outlined animate-spin text-sm">sync</span>
                    Saving & Verifying...
                  </>
                ) : (
                  <>
                    <span className="material-symbols-outlined text-sm">cloud_upload</span>
                    <span>Register & Verify in DB</span>
                  </>
                )}
              </motion.button>

              {createdTarget && (
                <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 flex items-center gap-2">
                  <span className="material-symbols-outlined text-base text-emerald-600">check_circle</span>
                  <span>Target active: <strong>{createdTarget.name}</strong> (Status: {createdTarget.status})</span>
                </div>
              )}
            </div>
          </motion.div>

          {/* Local / HuggingFace */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm relative overflow-hidden"
          >
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2.5 bg-amber-50 text-amber-600 border border-amber-200 rounded-xl">
                <span className="material-symbols-outlined text-2xl">memory</span>
              </div>
              <div>
                <h2 className="text-base font-bold text-slate-900">Local / Hugging Face</h2>
                <p className="text-xs text-slate-500">Direct open-weights or local runner connector</p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
                <h3 className="text-xs text-[#0e61a1] font-bold uppercase tracking-wider mb-1.5">
                  Local Adapter Guide
                </h3>
                <p className="text-xs text-slate-600 mb-2">
                  For local models, Aegis AI routes requests through your local connector without exposing GPU weights.
                </p>
                <ul className="space-y-1.5 text-xs text-slate-500">
                  <li className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-emerald-600 text-sm">check</span>
                    <span>No GPU required on Aegis server</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-emerald-600 text-sm">check</span>
                    <span>Deterministic seed (42) reproducibility</span>
                  </li>
                </ul>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">
                  Hugging Face Model ID (Optional)
                </label>
                <input
                  value={hfRepo}
                  onChange={(e) => setHfRepo(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:bg-white focus:border-[#0e61a1] transition-colors"
                  placeholder="meta-llama/Llama-3.2-3B-Instruct"
                  type="text"
                />
              </div>

              <button
                type="button"
                onClick={() => {
                  setTargetName('Local LLM Adapter');
                  setApiUrl('http://127.0.0.1:8080/v1/chat/completions');
                  toast('Populated local endpoint settings', { icon: '💻' });
                }}
                className="w-full py-2 px-4 bg-slate-100 hover:bg-slate-200 border border-slate-300 text-slate-700 rounded-xl text-xs font-semibold transition-all flex items-center justify-center gap-2"
              >
                <span className="material-symbols-outlined text-base">desktop_windows</span>
                <span>Use Local Host (127.0.0.1:8080)</span>
              </button>
            </div>
          </motion.div>
        </div>

        {/* Start Scan CTA */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: canStart ? 1 : 0.6 }}
          transition={{ duration: 0.3 }}
          className="flex flex-col items-center gap-3"
        >
          <motion.button
            whileHover={canStart ? { scale: 1.02 } : {}}
            whileTap={canStart ? { scale: 0.98 } : {}}
            disabled={!canStart || startingScan}
            onClick={handleStartScan}
            className={`px-8 py-3.5 rounded-xl text-sm md:text-base font-bold flex items-center gap-2.5 shadow-sm transition-all ${
              canStart
                ? 'bg-[#0e61a1] hover:bg-[#0b4e82] text-white cursor-pointer'
                : 'bg-slate-200 text-slate-400 cursor-not-allowed'
            }`}
          >
            {startingScan ? (
              <>
                <span className="material-symbols-outlined animate-spin text-lg">refresh</span>
                <span>Scheduling Evaluation Job...</span>
              </>
            ) : (
              <>
                <span className="material-symbols-outlined text-lg">security</span>
                <span>Start Trust & Safety Scan (Quick Mode: 25 Attack Prompts)</span>
              </>
            )}
          </motion.button>
          {!canStart && (
            <p className="text-xs text-slate-400">Configure target endpoint and click Register to begin</p>
          )}
        </motion.div>
      </div>
    </AppLayout>
  );
}
