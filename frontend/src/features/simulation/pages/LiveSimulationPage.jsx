import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useSearchParams } from 'react-router-dom';
import AppLayout from '../../../shared/components/AppLayout';
import MessageBubble from '../components/MessageBubble';
import HarmRateMeter from '../components/HarmRateMeter';
import TestCategoryTracker from '../components/TestCategoryTracker';
import jobService from '../../../services/jobService';
import toast from 'react-hot-toast';

export default function LiveSimulationPage() {
  const [searchParams] = useSearchParams();
  const jobId = searchParams.get('jobId');

  const [job, setJob] = useState(null);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    async function loadJobData() {
      if (!jobId) {
        // Find most recent job if no param supplied
        try {
          const jobs = await jobService.listJobs({ limit: 1 });
          if (jobs && jobs.length > 0) {
            setJob(jobs[0]);
            loadResults(jobs[0].id);
          }
        } catch {
          // ignore error
        }
        return;
      }

      try {
        setLoading(true);
        const j = await jobService.getJob(jobId);
        setJob(j);
        await loadResults(jobId);
      } catch (err) {
        toast.error('Could not load job details: ' + err.message);
      } finally {
        setLoading(false);
      }
    }

    loadJobData();
  }, [jobId]);

  const loadResults = async (id) => {
    try {
      const res = await jobService.getJobResults(id);
      setResults(res || []);
    } catch {
      // ignore
    }
  };

  const handleRunJob = async () => {
    if (!job) return;
    setRunning(true);
    try {
      toast('Starting evaluation worker runner...', { icon: '⚡' });
      const updatedJob = await jobService.runJob(job.id);
      setJob(updatedJob);
      await loadResults(job.id);
      toast.success('Evaluation job finished successfully!');
    } catch (err) {
      toast.error('Execution error: ' + err.message);
    } finally {
      setRunning(false);
    }
  };

  // Convert real results to MessageBubble format if available
  const displayMessages =
    results.length > 0
      ? results.map((r, i) => {
          const isSafe = r.verdict === 'SAFE';
          return {
            id: r.id || i,
            sender: 'sentinel',
            tag: r.category || 'FINTECH_SECURITY',
            text: r.attack_prompt || `Adversarial test prompt #${i + 1}`,
            response: {
              variant: isSafe ? 'safe' : 'failed',
              label: r.verdict || (isSafe ? 'SAFE' : 'UNSAFE'),
              text: r.target_response || 'Model refused request due to security constraints.',
              rationale: r.rationale,
            },
          };
        })
      : [];

  const unsafeCount = results.filter((r) => r.verdict === 'UNSAFE').length;
  const safeCount = results.filter((r) => r.verdict === 'SAFE').length;
  const totalCount = results.length;
  const currentHarmRate = totalCount > 0 ? Math.round((unsafeCount / totalCount) * 100) : 0;

  const categoryLabels = {
    CYBERSECURITY_AUTH: 'Cybersecurity & Auth Exploitation',
    FRAUD_FACILITATION: 'Fraud Facilitation & Social Engineering',
    MARKET_MANIPULATION: 'Market Manipulation & Predatory Steering',
    CONSUMER_HARM: 'Consumer Harm & Vulnerable Protection',
    REGULATORY_EVASION: 'Regulatory Evasion & Audit Bypass',
    BENIGN_CALIBRATION: 'Benign Baseline Calibration',
    PROMPT_INJECTION: 'Prompt Injection Defense',
    JAILBREAK: 'Jailbreak Resistance',
  };

  const dynamicCategories =
    results.length > 0
      ? Object.entries(
          results.reduce((acc, r) => {
            const cat = r.category || 'FINTECH_SAFETY';
            if (!acc[cat]) {
              acc[cat] = { total: 0, completed: 0, unsafe: 0 };
            }
            acc[cat].total += 1;
            if (r.verdict) acc[cat].completed += 1;
            if (r.verdict === 'UNSAFE') acc[cat].unsafe += 1;
            return acc;
          }, {})
        ).map(([key, data]) => {
          const isDone = data.completed === data.total;
          const pct = Math.round((data.completed / data.total) * 100);
          return {
            id: key,
            name: categoryLabels[key] || key.replace(/_/g, ' '),
            detail: isDone
              ? `${data.completed}/${data.total} payloads delivered (${data.unsafe} harmful)`
              : `In progress... (${data.completed}/${data.total})`,
            status: isDone ? 'complete' : 'active',
            progress: pct,
          };
        })
      : [];

  return (
    <AppLayout pageTitle="Sentinel Live Simulation">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Live Chat / Payload Runner Panel */}
        <motion.section
          initial={{ opacity: 0, x: -16 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4 }}
          className="lg:col-span-8 flex flex-col bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden h-[calc(100vh-140px)] min-h-[600px]"
        >
          {/* Chat Header */}
          <div className="bg-slate-50 border-b border-slate-200 px-5 py-4 flex justify-between items-center">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-[#001c40] via-[#0e61a1] to-[#38bdf8] flex items-center justify-center text-white shadow-xs">
                <span className="material-symbols-outlined text-xl">bug_report</span>
              </div>
              <div>
                <h2 className="text-sm md:text-base font-bold text-slate-900 leading-tight">
                  Sentinel Payload Runner
                </h2>
                <p className="text-xs text-slate-500">
                  Target: <strong className="text-slate-700">{job?.target?.name || 'Financial Model Endpoint'}</strong> • Mode: {job?.mode || 'QUICK'}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              {job && job.state !== 'COMPLETED' && (
                <button
                  onClick={handleRunJob}
                  disabled={running}
                  className="px-3.5 py-1.5 bg-[#0e61a1] hover:bg-[#0b4e82] disabled:opacity-50 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 shadow-xs transition-all"
                >
                  <span className={`material-symbols-outlined text-sm ${running ? 'animate-spin' : ''}`}>
                    {running ? 'sync' : 'play_arrow'}
                  </span>
                  {running ? 'Testing...' : 'Run Prompts'}
                </button>
              )}

              <div className="flex items-center gap-2 bg-white px-3 py-1.5 rounded-xl border border-slate-200 shadow-2xs">
                <span
                  className={`w-2 h-2 rounded-full ${
                    job?.state === 'COMPLETED' ? 'bg-emerald-500' : 'bg-[#0e61a1] animate-ping'
                  }`}
                />
                <span className="text-xs font-medium text-slate-700">
                  {job?.state === 'COMPLETED'
                    ? `Finished (${job.completed_items}/${job.total_items})`
                    : running
                    ? 'Testing in progress...'
                    : 'Ready'}
                </span>
              </div>
            </div>
          </div>

          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50/40">
            {displayMessages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center py-16 px-4">
                <div className="w-16 h-16 rounded-2xl bg-sky-50 border border-sky-200 flex items-center justify-center text-[#0e61a1] mb-4 shadow-sm">
                  <span className="material-symbols-outlined text-3xl">terminal</span>
                </div>
                <h3 className="text-base font-bold text-slate-800 mb-1">
                  {job ? 'No Payloads Executed Yet' : 'No Evaluation Job Selected'}
                </h3>
                <p className="text-xs text-slate-500 max-w-md leading-relaxed mb-5">
                  {job
                    ? `Job #${job.id.slice(0, 8)} (${job.target?.name || 'Target Bot'}) has not executed any test cases yet. Click "Run Prompts" to dispatch adversarial prompts and capture live responses.`
                    : 'Select or start an evaluation job to stream real-time adversarial prompts, bot responses, and judge verdicts.'}
                </p>
                {job && job.state !== 'COMPLETED' && (
                  <button
                    onClick={handleRunJob}
                    disabled={running}
                    className="px-4 py-2 bg-[#0e61a1] hover:bg-[#0b4e82] disabled:opacity-50 text-white rounded-xl text-xs font-semibold flex items-center gap-2 shadow-xs transition-all"
                  >
                    <span className={`material-symbols-outlined text-sm ${running ? 'animate-spin' : ''}`}>
                      {running ? 'sync' : 'play_arrow'}
                    </span>
                    {running ? 'Testing in progress...' : 'Start Execution'}
                  </button>
                )}
              </div>
            ) : (
              displayMessages.map((msg, i) => (
                <MessageBubble key={msg.id || i} message={msg} index={i} />
              ))
            )}

            {running && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex items-center gap-3 p-3.5 bg-sky-50 border border-sky-200 rounded-xl text-xs text-sky-800"
              >
                <span className="material-symbols-outlined animate-spin text-base text-[#0e61a1]">sync</span>
                <span>Dispatching adversarial prompt to target & evaluating with Groq Llama Guard 3 Judge...</span>
              </motion.div>
            )}
          </div>
        </motion.section>

        {/* Right: Metrics & Category Trackers */}
        <aside className="lg:col-span-4 flex flex-col gap-6">
          <HarmRateMeter
            rate={currentHarmRate}
            safeCount={safeCount}
            unsafeCount={unsafeCount}
            totalCount={results.length}
          />
          <TestCategoryTracker categories={dynamicCategories} />
        </aside>
      </div>
    </AppLayout>
  );
}
