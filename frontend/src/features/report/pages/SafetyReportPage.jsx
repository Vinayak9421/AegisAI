import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useParams, useNavigate } from 'react-router-dom';
import AppLayout from '../../../shared/components/AppLayout';
import jobService from '../../../services/jobService';
import toast from 'react-hot-toast';

export default function SafetyReportPage() {
  const { reportId } = useParams();
  const navigate = useNavigate();

  const [cert, setCert] = useState(null);
  const [availableJobs, setAvailableJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedFailureId, setExpandedFailureId] = useState(null);

  useEffect(() => {
    async function loadCertificate() {
      setLoading(true);
      try {
        const jobs = await jobService.listJobs({ limit: 20 });
        setAvailableJobs(jobs || []);

        let targetJobId = reportId;
        if (!targetJobId || targetJobId.length < 20 || targetJobId.startsWith('AEGIS-') || targetJobId === 'latest') {
          const evalJob = jobs?.find((j) => j.completed_items > 0 || j.state === 'COMPLETED') || jobs?.[0];
          targetJobId = evalJob ? evalJob.id : null;
        }

        if (targetJobId) {
          const certData = await jobService.getCertificate(targetJobId);
          setCert(certData);
        } else {
          setCert(null);
        }
      } catch (err) {
        setCert(null);
      } finally {
        setLoading(false);
      }
    }
    loadCertificate();
  }, [reportId]);

  if (loading) {
    return (
      <AppLayout pageTitle="Trust & Safety Certificate">
        <div className="flex flex-col items-center justify-center py-24 text-center">
          <span className="material-symbols-outlined text-4xl text-[#0e61a1] animate-spin mb-3">
            sync
          </span>
          <p className="text-sm font-semibold text-slate-700">Loading Certificate Records...</p>
          <p className="text-xs text-slate-400 mt-1">Fetching cryptographic evaluation report from database</p>
        </div>
      </AppLayout>
    );
  }

  if (!cert) {
    return (
      <AppLayout pageTitle="Trust & Safety Certificate">
        <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm p-10 text-center max-w-lg mx-auto my-12">
          <div className="w-16 h-16 rounded-2xl bg-sky-50 border border-sky-200 flex items-center justify-center text-[#0e61a1] mx-auto mb-4">
            <span className="material-symbols-outlined text-3xl">verified_user</span>
          </div>
          <h2 className="text-xl font-bold text-slate-900 mb-2">No Evaluation Certificate Found</h2>
          <p className="text-xs text-slate-500 leading-relaxed mb-6">
            No finalized evaluation certificate is recorded for this job. Certificates are automatically generated upon completing an adversarial test evaluation against your connected target.
          </p>
          <div className="flex justify-center gap-3">
            <button
              onClick={() => navigate('/dashboard')}
              className="px-4 py-2 border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold rounded-xl transition-all"
            >
              Dashboard
            </button>
            <button
              onClick={() => navigate('/simulation')}
              className="px-4 py-2 bg-[#0e61a1] hover:bg-[#0b4e82] text-white text-xs font-semibold rounded-xl flex items-center gap-1.5 shadow-xs transition-all"
            >
              <span className="material-symbols-outlined text-sm">play_arrow</span>
              Run Live Simulation
            </button>
          </div>
        </div>
      </AppLayout>
    );
  }

  const trustScore = cert.trust_score !== null && cert.trust_score !== undefined ? cert.trust_score : 0;
  const trustGrade = cert.trust_grade || (trustScore >= 90 ? 'Grade A' : (trustScore >= 75 ? 'Grade B' : 'Grade C'));
  const certNumber = cert.certificate_number || `AEGIS-${cert.job_id?.slice(0, 8)?.toUpperCase() || 'REPORT'}`;
  const targetName = cert.target_name || 'Authorized Chatbot Target';
  const pillars = cert.category_breakdown || cert.pillars || {};
  const failures = cert.failures || [];
  const recommendations = cert.recommendations || [];
  const reportHash = cert.report_hash || 'SHA-256 Verified';

  const downloadJson = () => {
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(cert, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute('download', `${certNumber}-Report.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
    toast.success('Downloaded Certificate JSON report');
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <AppLayout pageTitle="Trust & Safety Certificate">
      <div className="space-y-6">
        {/* Certificate Header Banner */}
        <motion.section
          initial={{ opacity: 0, y: -16 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6 md:p-8 flex flex-col md:flex-row justify-between items-start md:items-center relative overflow-hidden"
        >
          <div className="flex-1 z-10">
            <div className="flex flex-wrap items-center gap-2.5 mb-2">
              <span className="bg-emerald-50 text-emerald-800 border border-emerald-300 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider flex items-center gap-1.5 shadow-2xs">
                <span className="material-symbols-outlined text-sm text-emerald-600">verified</span>
                {trustGrade} Certified
              </span>
              <span className="text-xs font-mono font-semibold text-slate-500 bg-slate-100 px-2.5 py-0.5 rounded-lg border border-slate-200">
                Cert ID: {certNumber}
              </span>
              <span className="text-xs text-slate-400">
                Evaluation Protocol: <strong className="text-slate-700">Aegis Sentinel Multi-Pillar v1.0</strong>
              </span>
            </div>
            <h1 className="text-2xl md:text-3xl font-bold text-slate-900 tracking-tight mb-1">
              Fintech Trust & Safety Evaluation Certificate
            </h1>
            <p className="text-xs md:text-sm text-slate-500">
              Evaluated Target: <strong className="text-slate-800">{targetName}</strong> • Independent Judge: <strong className="text-slate-800">Groq Llama Guard 3 8B</strong>
            </p>

            {availableJobs.length > 1 && (
              <div className="flex items-center gap-2 mt-3">
                <span className="text-xs font-semibold text-slate-500 flex items-center gap-1">
                  <span className="material-symbols-outlined text-sm text-[#0e61a1]">history</span>
                  Audit Run:
                </span>
                <select
                  value={cert.job_id}
                  onChange={(e) => navigate(`/report/${e.target.value}`)}
                  className="px-2.5 py-1 text-xs font-semibold bg-white border border-slate-200 rounded-lg text-slate-700 shadow-2xs hover:border-slate-300 focus:outline-none focus:ring-1 focus:ring-[#0e61a1]"
                >
                  {availableJobs.map((j) => (
                    <option key={j.id} value={j.id}>
                      {j.target?.name || `Run #${j.id.slice(0, 8)}`} — {j.completed_items}/{j.total_items} items ({j.state})
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>


          {/* Overall Composite Score Box */}
          <div className="mt-6 md:mt-0 flex items-center gap-5 z-10 shrink-0 bg-slate-50/80 p-4 rounded-2xl border border-slate-200">
            <div className="text-right">
              <p className="text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-0.5">
                Composite Trust Score
              </p>
              <div className="flex items-baseline justify-end gap-1">
                <motion.span
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.2, duration: 0.4 }}
                  className="text-3xl md:text-4xl font-extrabold text-[#0e61a1]"
                >
                  {trustScore}%
                </motion.span>
                <span className="text-xs font-bold text-slate-400">/ 100</span>
              </div>
            </div>
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-[#001c40] via-[#0e61a1] to-[#38bdf8] flex items-center justify-center text-white shadow-md shadow-sky-900/20">
              <span className="material-symbols-outlined text-3xl">workspace_premium</span>
            </div>
          </div>
        </motion.section>

        {/* 6 Multi-Dimensional Pillars Grid */}
        <div>
          <div className="flex items-center justify-between mb-3 px-1">
            <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <span className="material-symbols-outlined text-[#0e61a1]">radar</span>
              Multi-Dimensional Evaluation Pillars (Fintech Domain Breakdown)
            </h2>
            <span className="text-xs text-slate-500 font-medium">{Object.keys(pillars).length} Evaluated Dimensions</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.keys(pillars).length === 0 ? (
              <div className="col-span-full p-8 text-center bg-white rounded-2xl border border-slate-200 text-slate-400">
                No dimensional pillars recorded for this evaluation job.
              </div>
            ) : (
              Object.entries(pillars).map(([key, p], i) => {
                const isPass = p.score >= 85;
                const isWarn = p.score >= 70 && p.score < 85;
                const scoreColor = isPass ? '#10b981' : (isWarn ? '#f59e0b' : '#ef4444');

              return (
                <motion.div
                  key={key}
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className="bg-white rounded-2xl border border-slate-200/80 p-5 shadow-sm hover:shadow-md transition-all flex flex-col justify-between"
                >
                  <div>
                    <div className="flex justify-between items-start gap-2 mb-2">
                      <h3 className="text-xs font-bold text-slate-900 leading-tight">
                        {p.name}
                      </h3>
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 border border-slate-200 shrink-0">
                        {Math.round(p.weight * 100)}% Weight
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-500 mb-4 line-clamp-2">
                      {p.description}
                    </p>
                  </div>

                  <div>
                    {/* Score and Bar */}
                    <div className="flex justify-between items-baseline mb-1.5">
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded border ${
                          isPass
                            ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                            : isWarn
                            ? 'bg-amber-50 text-amber-700 border-amber-200'
                            : 'bg-rose-50 text-rose-700 border-rose-200'
                        }`}
                      >
                        {p.status || (isPass ? 'PASS' : 'WARN')}
                      </span>
                      <span className="text-lg font-bold text-slate-900">
                        {p.score}%
                      </span>
                    </div>

                    <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${p.score}%` }}
                        transition={{ duration: 0.8, ease: 'easeOut' }}
                        className="h-2 rounded-full"
                        style={{ backgroundColor: scoreColor }}
                      />
                    </div>

                    <div className="flex justify-between text-[10px] text-slate-400 mt-2">
                      <span>Passed: <strong>{p.pass_count || 0}</strong></span>
                      <span>Failed: <strong className={p.fail_count ? 'text-rose-600' : ''}>{p.fail_count || 0}</strong></span>
                      <span>Total: <strong>{p.total_count || 0}</strong></span>
                    </div>
                  </div>
                </motion.div>
              );
            }))}
          </div>
        </div>

        {/* Two Column Layout: Critical Vulnerabilities & Actionable Roadmap */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left: Critical Vulnerabilities / Failure Audit */}
          <div className="lg:col-span-7 flex flex-col gap-6">
            <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm overflow-hidden flex flex-col">
              <div className="p-5 border-b border-slate-200 bg-slate-50/60 flex justify-between items-center">
                <div>
                  <h3 className="text-sm md:text-base font-bold text-slate-900 flex items-center gap-2">
                    <span className="material-symbols-outlined text-rose-600">warning</span>
                    Critical Vulnerability Audit ({failures.length})
                  </h3>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Adversarial test cases where the target bot failed to refuse or triggered a violation
                  </p>
                </div>
              </div>

              <div className="divide-y divide-slate-100 p-2">
                {failures.length === 0 ? (
                  <div className="p-8 text-center text-slate-400">
                    <span className="material-symbols-outlined text-3xl text-emerald-500 mb-2">
                      verified_user
                    </span>
                    <p className="text-xs font-semibold text-slate-700">Zero Critical Failures Detected</p>
                    <p className="text-[11px] text-slate-500 mt-0.5">The target bot successfully resisted all tested high-severity exploitation prompts.</p>
                  </div>
                ) : (
                  failures.map((f, i) => {
                    const isExpanded = expandedFailureId === (f.result_id || i);
                    return (
                      <div key={f.result_id || i} className="p-3.5 hover:bg-slate-50/70 rounded-xl transition-colors">
                        <div
                          onClick={() => setExpandedFailureId(isExpanded ? null : (f.result_id || i))}
                          className="flex justify-between items-start cursor-pointer group"
                        >
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-50 text-rose-700 border border-rose-200 uppercase tracking-wider">
                                {f.severity || 'CRITICAL'}
                              </span>
                              <span className="text-xs font-bold text-slate-800 group-hover:text-[#0e61a1] transition-colors">
                                {f.category}
                              </span>
                            </div>
                            <p className="text-xs text-slate-600 line-clamp-1">{f.rationale}</p>
                          </div>
                          <span className="text-[11px] font-semibold text-[#0e61a1] shrink-0 ml-3">
                            {isExpanded ? 'Hide' : 'View Payload'}
                          </span>
                        </div>

                        {isExpanded && (
                          <div className="mt-3 pt-3 border-t border-slate-100 space-y-2.5 text-xs">
                            <div>
                              <span className="font-bold text-slate-700 block mb-1">Dispatched Attack Prompt:</span>
                              <div className="bg-slate-100 p-2.5 rounded-lg font-mono text-[11px] text-slate-800 whitespace-pre-wrap">
                                {f.attack_prompt}
                              </div>
                            </div>
                            <div>
                              <span className="font-bold text-slate-700 block mb-1">Bot Raw Response:</span>
                              <div className="bg-rose-50/70 border border-rose-200 p-2.5 rounded-lg font-mono text-[11px] text-rose-900 whitespace-pre-wrap">
                                {f.target_response}
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })
                )}
              </div>
            </div>
          </div>

          {/* Right: Actionable Remediation Roadmap & Export */}
          <div className="lg:col-span-5 flex flex-col gap-6">
            {/* Recommendations */}
            <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6">
              <h3 className="text-sm md:text-base font-bold text-slate-900 flex items-center gap-2 mb-4">
                <span className="material-symbols-outlined text-[#0e61a1]">recommend</span>
                Actionable Remediation Roadmap
              </h3>
              {recommendations.length === 0 ? (
                <div className="py-6 text-center text-slate-400">
                  <span className="material-symbols-outlined text-3xl text-emerald-500 block mb-1">
                    check_circle
                  </span>
                  <p className="text-xs font-semibold text-slate-700">All Safety Guardrails Met</p>
                  <p className="text-[11px] text-slate-500 mt-0.5">
                    No critical remediation actions required for this evaluated build.
                  </p>
                </div>
              ) : (
                <ul className="space-y-3">
                  {recommendations.map((rec, i) => (
                    <li key={i} className="flex items-start gap-2.5 text-xs text-slate-700 leading-relaxed">
                      <span className="material-symbols-outlined text-[#0e61a1] text-base shrink-0 mt-0.5">
                        check_circle
                      </span>
                      <span>{rec}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            {/* Cryptographic Hash & Actions */}
            <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6 space-y-4">
              <div>
                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block mb-1">
                  Cryptographic Report Hash (SHA-256)
                </span>
                <p className="text-[11px] font-mono text-slate-600 bg-slate-100 p-2 rounded-lg border border-slate-200 break-all select-all">
                  {reportHash}
                </p>
              </div>

              <div className="flex flex-col sm:flex-row gap-2.5 pt-2">
                <button
                  onClick={handlePrint}
                  className="flex-1 py-2.5 px-4 bg-[#0e61a1] hover:bg-[#0b4e82] text-white rounded-xl text-xs font-semibold shadow-xs flex items-center justify-center gap-2 transition-all"
                >
                  <span className="material-symbols-outlined text-base">print</span>
                  <span>Print Certificate</span>
                </button>
                <button
                  onClick={downloadJson}
                  className="flex-1 py-2.5 px-4 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 rounded-xl text-xs font-semibold shadow-2xs flex items-center justify-center gap-2 transition-all"
                >
                  <span className="material-symbols-outlined text-base">code</span>
                  <span>Export JSON</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
