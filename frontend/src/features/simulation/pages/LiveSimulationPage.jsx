import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useSearchParams, useNavigate } from 'react-router-dom';
import AppLayout from '../../../shared/components/AppLayout';
import MessageBubble from '../components/MessageBubble';
import HarmRateMeter from '../components/HarmRateMeter';
import TestCategoryTracker from '../components/TestCategoryTracker';
import jobService from '../../../services/jobService';
import systemService from '../../../services/systemService';
import toast from 'react-hot-toast';

export default function LiveSimulationPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const jobId = searchParams.get('jobId');

  const [job, setJob] = useState(null);
  const [results, setResults] = useState([]);
  const [systemConfig, setSystemConfig] = useState(null);
  const [loading, setLoading] = useState(false);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    async function loadConfig() {
      try {
        const cfg = await systemService.getConfig();
        if (cfg) setSystemConfig(cfg);
      } catch {
        // ignore error
      }
    }
    loadConfig();
  }, []);

  useEffect(() => {
    let intervalId = null;

    async function loadJobData() {
      const activeJobId = jobId || (job ? job.id : null);
      let targetId = activeJobId;

      if (!targetId) {
        try {
          const jobs = await jobService.listJobs({ limit: 1 });
          if (jobs && jobs.length > 0) {
            targetId = jobs[0].id;
            setJob(jobs[0]);
          }
        } catch {
          // ignore error
        }
      }

      if (!targetId) return;

      try {
        const [jobData, resultData] = await Promise.all([
          jobService.getJob(targetId).catch(() => null),
          jobService.getJobResults(targetId, { limit: 50 }).catch(() => []),
        ]);

        if (jobData) {
          setJob(jobData);
          if (jobData.state === 'RUNNING') {
            setRunning(true);
          } else if (jobData.state === 'COMPLETED' || jobData.state === 'FAILED' || jobData.state === 'CANCELLED') {
            setRunning(false);
          }
        }

        if (resultData) {
          setResults(resultData);
        }
      } catch (err) {
        console.error('Error fetching job state:', err);
      }
    }

    loadJobData();

    // Auto-poll job status and stream results every 2.5 seconds
    intervalId = setInterval(loadJobData, 2500);

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [jobId]);

  const handleRunJob = async () => {
    if (!job) return;
    setRunning(true);
    toast.success('Dispatched execution run across configured adversarial test suite');
    try {
      await jobService.runJob(job.id);
      const updated = await jobService.getJob(job.id);
      setJob(updated);
    } catch (err) {
      toast.error(err.message || 'Execution runner failed');
      setRunning(false);
    }
  };

  const safeCount = results.filter((r) => r.verdict === 'SAFE').length;
  const unsafeCount = results.filter((r) => r.verdict === 'UNSAFE').length;
  const evaluableCount = safeCount + unsafeCount;
  const currentHarmRate = evaluableCount > 0 ? Math.round((unsafeCount / evaluableCount) * 100) : 0;

  const displayMessages = results.map((r, i) => {
    const rawResponse = r.target_response || r.response_text;
    const rawPrompt = r.attack_prompt || r.test_case?.prompt_template || r.prompt;
    const isError = r.target_status === 'ERROR' || (rawResponse && rawResponse.startsWith('ERROR:'));
    const isSafe = r.verdict === 'SAFE';

    let variant = 'safe';
    let label = 'SAFE';

    if (isError) {
      variant = 'failed';
      label = 'TARGET TIMEOUT / ERROR';
    } else if (r.verdict === 'UNSAFE') {
      variant = 'failed';
      label = 'UNSAFE BREACH';
    } else if (r.verdict === 'SAFE') {
      variant = 'safe';
      label = 'REFUSED / SAFE';
    } else {
      variant = 'safe';
      label = r.verdict || 'EVALUATED';
    }

    const activeJudgeModel =
      r.judge_evaluation?.model ||
      job?.judge_config?.model ||
      (systemConfig?.judge_provider ? `${systemConfig.judge_provider.toUpperCase()} ${systemConfig.judge_model}` : systemConfig?.judge_model) ||
      'Independent Judge';

    return {
      id: r.id || i,
      sender: 'sentinel',
      tag: r.category || 'FINRISK',
      owasp_id: r.owasp_id,
      severity: r.severity,
      verdict: r.verdict,
      text: rawPrompt || 'Adversarial prompt vector',
      response: {
        text: rawResponse || 'No response returned by target application.',
        variant,
        label,
        rationale: r.rationale,
        judge_model: activeJudgeModel,
      },
    };
  });

  const categoryLabels = {
    FINRISK: 'Financial Crime & Fraud Resistance',
    COMPLIANCE: 'Regulatory Compliance & Evasion Defense',
    SECURITY: 'Adversarial Robustness & Jailbreak',
    GROUNDING: 'Factual Integrity & Hallucination',
    SESSION: 'Conversational Session Resilience',
    PROVENANCE: 'Provenance & Lineage Governance',
    CYBERSECURITY_AUTH: 'Cybersecurity & Authentication Exploitation',
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
              ? `${data.completed}/${data.total} vectors evaluated (${data.unsafe} breaches)`
              : `Evaluation in progress... (${data.completed}/${data.total})`,
            status: isDone ? 'complete' : 'active',
            progress: pct,
          };
        })
      : [];

  return (
    <AppLayout pageTitle="Live Adversarial Simulation">
      <div className="space-y-5">
        {/* Section Header */}
        <div className="border-b border-slate-200 pb-4">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="px-2 py-0.5 bg-slate-100 text-slate-700 text-[11px] font-mono uppercase tracking-wider rounded border border-slate-200">
                  Execution Telemetry
                </span>
                <span className="text-xs text-slate-500 font-mono">
                  Job ID: {job ? job.id.slice(0, 8) : 'Pending'}
                </span>
              </div>
              <h1 className="font-serif text-2xl md:text-3xl font-bold text-slate-900 tracking-tight">
                Live Adversarial Red-Team Pipeline Trace
              </h1>
              <p className="text-xs md:text-sm text-slate-600 mt-0.5">
                Real-time dispatch of standardized financial threat vectors, target model response logging, and dual-phase independent judge classifications.
              </p>
            </div>

            {/* Status Metadata Bar */}
            <div className="flex flex-wrap items-center gap-2 text-xs font-mono">
              <span className="px-2.5 py-1 bg-white border border-slate-200 rounded text-slate-700 shadow-2xs">
                Pacing: <strong className="text-slate-900">6.0s (10 RPM)</strong>
              </span>
              <span className="px-2.5 py-1 bg-white border border-slate-200 rounded text-slate-700 shadow-2xs">
                Seed: <strong className="text-slate-900">42 (Deterministic)</strong>
              </span>
              <span
                className={`px-2.5 py-1 rounded font-bold border uppercase flex items-center gap-1.5 ${
                  job?.state === 'COMPLETED'
                    ? 'bg-emerald-50 text-emerald-800 border-emerald-300'
                    : running
                    ? 'bg-sky-50 text-[#0e61a1] border-sky-300'
                    : 'bg-slate-100 text-slate-700 border-slate-300'
                }`}
              >
                <span
                  className={`w-2 h-2 rounded-full ${
                    job?.state === 'COMPLETED'
                      ? 'bg-emerald-600'
                      : running
                      ? 'bg-[#0e61a1] animate-ping'
                      : 'bg-slate-500'
                  }`}
                />
                {job?.state || 'READY'}
              </span>
            </div>
          </div>
        </div>

        {/* Main Observability Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left: Stream Console Panel */}
          <section className="lg:col-span-8 flex flex-col bg-white rounded-xl border border-slate-200 shadow-2xs overflow-hidden h-[calc(100vh-210px)] min-h-[640px]">
            {/* Stream Header */}
            <div className="bg-slate-50/80 border-b border-slate-200 px-5 py-3.5 flex justify-between items-center">
              <div>
                <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                  <span className="material-symbols-outlined text-base text-[#0e61a1]">terminal</span>
                  Active Execution Log
                </h2>
                <p className="text-[11px] text-slate-500 font-mono mt-0.5">
                  Target: {job?.target?.name || 'Financial Model Endpoint'} | Mode: {job?.mode || 'QUICK'}
                </p>
              </div>

              <div className="flex items-center gap-2.5">
                {job?.state === 'COMPLETED' && (
                  <button
                    onClick={() => navigate(`/report/${job.id}`)}
                    className="px-3 py-1.5 bg-emerald-700 hover:bg-emerald-800 text-white rounded-lg text-xs font-bold flex items-center gap-1.5 shadow-2xs transition-all"
                  >
                    <span className="material-symbols-outlined text-sm">verified</span>
                    View Final Certificate
                  </button>
                )}

                {job && job.state !== 'COMPLETED' && (
                  <button
                    onClick={handleRunJob}
                    disabled={running}
                    className="px-3 py-1.5 bg-[#0e61a1] hover:bg-[#0b4e82] disabled:opacity-50 text-white rounded-lg text-xs font-bold flex items-center gap-1.5 shadow-2xs transition-all"
                  >
                    <span className={`material-symbols-outlined text-sm ${running ? 'animate-spin' : ''}`}>
                      {running ? 'sync' : 'play_arrow'}
                    </span>
                    {running ? 'Testing Active...' : 'Dispatch Prompts'}
                  </button>
                )}

                <span className="text-xs font-mono text-slate-600 bg-white px-2 py-1 rounded border border-slate-200">
                  {results.length} / {job?.total_items || 25} Items
                </span>
              </div>
            </div>

            {/* Stream List */}
            <div className="flex-1 overflow-y-auto p-5 space-y-4 bg-slate-50/30">
              {displayMessages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center py-20 px-4">
                  <span className="material-symbols-outlined text-4xl text-slate-300 mb-2">
                    data_exploration
                  </span>
                  <h3 className="text-sm font-bold text-slate-800 mb-1">
                    {job ? 'No Payloads Dispatched Yet' : 'No Evaluation Run Selected'}
                  </h3>
                  <p className="text-xs text-slate-500 max-w-md leading-relaxed mb-4">
                    {job
                      ? `Job #${job.id.slice(0, 8)} is ready. Click "Dispatch Prompts" to initiate adversarial test vectors across all 6 financial security pillars.`
                      : 'Navigate to Connect Target to register an endpoint and initialize an evaluation job.'}
                  </p>
                  {job && job.state !== 'COMPLETED' && (
                    <button
                      onClick={handleRunJob}
                      disabled={running}
                      className="px-4 py-2 bg-[#0e61a1] hover:bg-[#0b4e82] disabled:opacity-50 text-white rounded-lg text-xs font-bold flex items-center gap-2 shadow-2xs transition-all"
                    >
                      <span className="material-symbols-outlined text-sm">play_arrow</span>
                      Start Red-Team Execution
                    </button>
                  )}
                </div>
              ) : (
                displayMessages.map((msg, i) => (
                  <MessageBubble key={msg.id || i} message={msg} index={i} />
                ))
              )}

              {/* Completion Banner */}
              {job?.state === 'COMPLETED' && (
                <div className="p-4 bg-white border border-emerald-300 rounded-xl flex flex-col sm:flex-row items-center justify-between gap-4 shadow-2xs">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-200 flex items-center justify-center shrink-0">
                      <span className="material-symbols-outlined text-2xl text-emerald-600">verified</span>
                    </div>
                    <div>
                      <h4 className="text-xs font-bold text-slate-900 flex items-center gap-2">
                        Evaluation Run Completed Successfully
                        <span className="px-1.5 py-0.2 bg-emerald-100 text-emerald-800 text-[10px] font-mono rounded">
                          Audit Ready
                        </span>
                      </h4>
                      <p className="text-[11px] text-slate-500 mt-0.5">
                        Completed {job.completed_items || results.length} vectors. Multi-pillar scores, AER, and cryptographic SHA-256 certificate are finalized.
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => navigate(`/report/${job.id}`)}
                    className="px-4 py-2 bg-[#0e61a1] hover:bg-[#0b4e82] text-white text-xs font-bold rounded-lg flex items-center gap-1.5 shadow-2xs transition-all whitespace-nowrap"
                  >
                    <span className="material-symbols-outlined text-base">assessment</span>
                    Open Full Audit Certificate
                  </button>
                </div>
              )}

              {running && (
                <div className="flex items-center gap-2.5 p-3 bg-sky-50 border border-sky-200 rounded-lg text-xs text-sky-900 font-mono">
                  <span className="material-symbols-outlined animate-spin text-sm text-[#0e61a1]">sync</span>
                  <span>Dispatching attack payload to model & awaiting dual-phase judge evaluation...</span>
                </div>
              )}
            </div>
          </section>

          {/* Right: Telemetry & Checklist */}
          <aside className="lg:col-span-4 flex flex-col gap-5">
            <HarmRateMeter
              rate={currentHarmRate}
              safeCount={safeCount}
              unsafeCount={unsafeCount}
              totalCount={results.length}
            />
            <TestCategoryTracker categories={dynamicCategories} />
          </aside>
        </div>
      </div>
    </AppLayout>
  );
}
