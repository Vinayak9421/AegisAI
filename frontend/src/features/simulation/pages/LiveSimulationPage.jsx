import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useSearchParams } from 'react-router-dom';
import AppLayout from '../../../shared/components/AppLayout';
import MessageBubble from '../components/MessageBubble';
import HarmRateMeter from '../components/HarmRateMeter';
import TestCategoryTracker from '../components/TestCategoryTracker';
import jobService from '../../../services/jobService';
import toast from 'react-hot-toast';
import { mockSimulationMessages, mockTestCategories } from '../../../store/mockData';

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
          // fallback to mock data
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
      : mockSimulationMessages;

  const unsafeCount = results.filter((r) => r.verdict === 'UNSAFE').length;
  const safeCount = results.filter((r) => r.verdict === 'SAFE').length;
  const totalCount = results.length || 1;
  const currentHarmRate = Math.round((unsafeCount / totalCount) * 100);

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
            {displayMessages.map((msg, i) => (
              <MessageBubble key={msg.id || i} message={msg} index={i} />
            ))}

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
          <HarmRateMeter rate={currentHarmRate} />
          <TestCategoryTracker categories={mockTestCategories} />
        </aside>
      </div>
    </AppLayout>
  );
}
