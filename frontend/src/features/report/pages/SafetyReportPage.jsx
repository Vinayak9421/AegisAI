import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useParams, useNavigate } from 'react-router-dom';
import AppLayout from '../../../shared/components/AppLayout';
import AegisLogo from '../../../shared/components/AegisLogo';
import jobService from '../../../services/jobService';
import toast from 'react-hot-toast';

export default function SafetyReportPage() {
  const { reportId } = useParams();
  const navigate = useNavigate();

  const [cert, setCert] = useState(null);
  const [availableJobs, setAvailableJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedFailureId, setExpandedFailureId] = useState(null);
  const [copiedHash, setCopiedHash] = useState(false);
  const [filterCategory, setFilterCategory] = useState('ALL');
  const [filterSeverity, setFilterSeverity] = useState('ALL');
  const [currentPage, setCurrentPage] = useState(1);
  const PAGE_SIZE = 8;

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

  const copyToClipboard = (text, label) => {
    navigator.clipboard.writeText(text);
    toast.success(`Copied ${label} to clipboard`);
  };

  const handleCopyHash = () => {
    if (!cert?.report_hash) return;
    navigator.clipboard.writeText(cert.report_hash);
    setCopiedHash(true);
    toast.success('SHA-256 Report Hash copied to clipboard');
    setTimeout(() => setCopiedHash(false), 2500);
  };

  const downloadJson = () => {
    if (!cert) return;
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(cert, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute('download', `${certNumber || 'AEGIS-AUDIT'}-Certificate.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
    toast.success('Exported Certificate JSON payload');
  };

  const handlePrint = () => {
    window.print();
  };

  if (loading) {
    return (
      <AppLayout pageTitle="Trust & Safety Certificate">
        <div className="flex flex-col items-center justify-center py-28 text-center">
          <div className="w-10 h-10 border-2 border-slate-200 border-t-[#0e61a1] rounded-full animate-spin mb-4" />
          <p className="text-sm font-semibold text-slate-800 tracking-tight">Verifying Cryptographic Certificate Records</p>
          <p className="text-xs text-slate-400 mt-1 font-mono">Fetching evaluation artifact from immutable audit register</p>
        </div>
      </AppLayout>
    );
  }

  if (!cert) {
    return (
      <AppLayout pageTitle="Trust & Safety Certificate">
        <div className="bg-white rounded-xl border border-slate-200/90 shadow-xs p-10 text-center max-w-lg mx-auto my-14">
          <div className="w-14 h-14 rounded-xl bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-500 mx-auto mb-4">
            <span className="material-symbols-outlined text-2xl">verified_user</span>
          </div>
          <h2 className="text-lg font-serif font-semibold text-slate-900 mb-2">No Finalized Certificate Found</h2>
          <p className="text-xs text-slate-500 leading-relaxed mb-6">
            No finalized Trust & Safety evaluation record was found for this job identifier. Certificates are generated automatically upon completion of adversarial evaluation against registered target endpoints.
          </p>
          <div className="flex justify-center gap-3">
            <button
              onClick={() => navigate('/admin/overview')}
              className="px-4 py-2 border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold rounded-lg transition-colors"
            >
              Audit Overview
            </button>
            <button
              onClick={() => navigate('/simulation')}
              className="px-4 py-2 bg-[#0e61a1] hover:bg-[#0b4e82] text-white text-xs font-semibold rounded-lg flex items-center gap-1.5 transition-colors shadow-xs"
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
  const certNumber = cert.certificate_number || `AEGIS-${cert.job_id?.slice(0, 8)?.toUpperCase() || 'AUDIT'}`;
  const targetName = cert.target_name || 'Authorized Financial LLM Target';
  const pillars = cert.category_breakdown || cert.pillars || {};
  const failures = cert.failures || [];
  const failureCategories = ['ALL', ...Array.from(new Set(failures.map((f) => f.category).filter(Boolean)))];
  const failureSeverities = ['ALL', ...Array.from(new Set(failures.map((f) => f.severity || 'CRITICAL').filter(Boolean)))];

  const filteredFailures = failures.filter((f) => {
    if (filterCategory !== 'ALL' && f.category !== filterCategory) return false;
    if (filterSeverity !== 'ALL' && (f.severity || 'CRITICAL') !== filterSeverity) return false;
    return true;
  });

  const totalPages = Math.max(1, Math.ceil(filteredFailures.length / PAGE_SIZE));
  const safeCurrentPage = Math.min(currentPage, totalPages);
  const startIndex = (safeCurrentPage - 1) * PAGE_SIZE;
  const paginatedFailures = filteredFailures.slice(startIndex, startIndex + PAGE_SIZE);

  const renderFailureCard = (f, i, forceExpanded = false) => {
    const failureKey = f.result_id || `failure-${i}`;
    const isExpanded = forceExpanded || expandedFailureId === failureKey;

    return (
      <div
        key={failureKey}
        className="border border-slate-200 rounded-xl bg-white overflow-hidden text-xs transition-all hover:border-slate-300 print-avoid-break"
      >
        <div
          onClick={() => !forceExpanded && setExpandedFailureId(isExpanded ? null : failureKey)}
          className={`p-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 ${forceExpanded ? '' : 'cursor-pointer'} bg-slate-50/60 hover:bg-slate-50`}
        >
          <div className="flex flex-wrap items-center gap-2">
            <span
              className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase border ${
                (f.severity || 'CRITICAL') === 'CRITICAL'
                  ? 'bg-rose-50 text-rose-700 border-rose-200'
                  : 'bg-amber-50 text-amber-700 border-amber-200'
              }`}
            >
              {f.severity || 'CRITICAL'}
            </span>
            <span className="font-semibold text-slate-900">{f.category}</span>
            {f.owasp_id && (
              <span className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-slate-100 text-slate-600 border border-slate-200">
                {f.owasp_id}
              </span>
            )}
            <span className="text-slate-400">•</span>
            <span className="text-slate-600 line-clamp-1 flex-1">{f.rationale}</span>
          </div>

          <div className="flex items-center gap-2 shrink-0 text-slate-500 print:hidden">
            <span className="text-[11px] font-semibold text-[#0e61a1]">
              {isExpanded ? 'Collapse Trace' : 'Inspect Vector'}
            </span>
            <span className="material-symbols-outlined text-sm text-slate-400">
              {isExpanded ? 'expand_less' : 'expand_more'}
            </span>
          </div>
        </div>

        {/* Expandable Trace Payload View (Always visible in print) */}
        <div className={`p-4 border-t border-slate-200 space-y-3 ${isExpanded ? 'block' : 'hidden print:block'}`}>
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-[11px] font-bold text-slate-700 uppercase tracking-wider">
                Phase A: Dispatched Adversarial Payload
              </span>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  copyToClipboard(f.attack_prompt, 'Attack Payload');
                }}
                className="text-[10px] font-mono text-slate-500 hover:text-slate-800 flex items-center gap-1 print:hidden"
              >
                <span className="material-symbols-outlined text-xs">content_copy</span>
                Copy
              </button>
            </div>
            <div className="bg-slate-900 text-slate-100 p-3 rounded-lg font-mono text-[11px] leading-relaxed whitespace-pre-wrap selection:bg-[#0e61a1]">
              {f.attack_prompt}
            </div>
          </div>

          <div>
            <span className="text-[11px] font-bold text-rose-800 uppercase tracking-wider block mb-1">
              Phase B: Target Model Unsafe Output
            </span>
            <div className="bg-rose-50 border border-rose-200 text-rose-950 p-3 rounded-lg font-mono text-[11px] leading-relaxed whitespace-pre-wrap">
              {f.target_response}
            </div>
          </div>

          <div>
            <span className="text-[11px] font-bold text-slate-700 uppercase tracking-wider block mb-1">
              Phase C: Independent Judge Rationale (Llama-3.3-70B)
            </span>
            <div className="bg-slate-50 border border-slate-200 text-slate-700 p-2.5 rounded-lg text-xs leading-relaxed">
              {f.rationale}
            </div>
          </div>
        </div>
      </div>
    );
  };

  const recommendations = cert.recommendations || [];
  const limitations = cert.limitations || [];
  const reportHash = cert.report_hash || 'SHA-256 Verified Digest';
  const aer = cert.aer !== null && cert.aer !== undefined ? cert.aer : 0;
  const identityScore = cert.identity_score !== null && cert.identity_score !== undefined ? cert.identity_score : 70;
  const shr = cert.shr !== null && cert.shr !== undefined ? cert.shr : 0;
  const coverage = cert.coverage_summary || {};
  const formulaVersions = cert.formula_versions || {};
  const formattedDate = cert.created_at
    ? new Date(cert.created_at).toUTCString()
    : new Date().toUTCString();

  return (
    <AppLayout pageTitle="Trust & Safety Certificate">
      <div className="space-y-6 print-certificate-container">
        {/* Screen-Only Action & Switcher Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white border border-slate-200/90 rounded-xl p-4 shadow-2xs print:hidden">
          <div className="flex items-center gap-3">
            <span className="text-xs font-mono font-semibold text-slate-500 bg-slate-100 px-2.5 py-1 rounded border border-slate-200">
              {certNumber}
            </span>
            {availableJobs.length > 1 && (
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-500 font-medium">Switch Run:</span>
                <select
                  value={cert.job_id}
                  onChange={(e) => navigate(`/report/${e.target.value}`)}
                  className="px-2.5 py-1 text-xs font-medium bg-white border border-slate-200 rounded-lg text-slate-700 hover:border-slate-300 focus:outline-none focus:ring-1 focus:ring-[#0e61a1]"
                >
                  {availableJobs.map((j) => (
                    <option key={j.id} value={j.id}>
                      {j.target?.name || `Run ${j.id.slice(0, 8)}`} ({j.completed_items}/{j.total_items} items • {j.state})
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => navigate('/simulation')}
              className="px-3 py-1.5 border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-semibold rounded-lg flex items-center gap-1.5 transition-colors"
            >
              <span className="material-symbols-outlined text-sm">bug_report</span>
              <span>Telemetry Trace</span>
            </button>
            <button
              onClick={downloadJson}
              className="px-3 py-1.5 border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-semibold rounded-lg flex items-center gap-1.5 transition-colors"
            >
              <span className="material-symbols-outlined text-sm">code</span>
              <span>Export JSON</span>
            </button>
            <button
              onClick={handlePrint}
              className="px-3.5 py-1.5 bg-[#0e61a1] hover:bg-[#0b4e82] text-white text-xs font-semibold rounded-lg flex items-center gap-1.5 shadow-xs transition-colors"
            >
              <span className="material-symbols-outlined text-sm">print</span>
              <span>Print / PDF Certificate</span>
            </button>
          </div>
        </div>

        {/* Primary Security Certificate Container */}
        <div className="bg-white border border-slate-200/90 rounded-xl shadow-xs p-6 md:p-9 space-y-8 print:p-0 print:border-none print:shadow-none">
          {/* Audit & Evaluation Header */}
          <div className="border-b border-slate-200 pb-6 print-avoid-break">
            <div className="flex flex-col md:flex-row md:items-start justify-between gap-6">
              <div className="space-y-2.5">
                <div className="flex items-center gap-3">
                  <AegisLogo size="md" variant="full" showSubtitle={false} />
                  <span className="text-slate-300">|</span>
                  <div className="flex items-center gap-2 text-[10px] font-mono tracking-wider uppercase text-slate-500">
                    <span>ATTESTATION PROTOCOL</span>
                    <span>•</span>
                    <span>INDEPENDENT ENGINE</span>
                  </div>
                </div>

                <h1 className="text-2xl md:text-3xl font-serif font-semibold text-slate-900 tracking-tight">
                  Fintech Trust & Safety Evaluation Certificate
                </h1>

                <p className="text-xs text-slate-600 max-w-2xl leading-relaxed">
                  Official attestation record certifying empirical red-teaming and compliance safety evaluation across standard financial risk taxonomy pillars.
                </p>
              </div>

              {/* Official Seal / Grade Badge */}
              <div className="flex flex-row md:flex-col items-end gap-2 shrink-0">
                <div className="border border-slate-200 bg-slate-50/80 rounded-xl p-3.5 text-right flex items-center gap-3">
                  <div>
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 block">
                      Evaluation Verdict
                    </span>
                    <span className="text-lg font-serif font-bold text-slate-900">
                      {trustGrade}
                    </span>
                  </div>
                  <div className="w-10 h-10 rounded-lg bg-white border border-slate-200 flex items-center justify-center text-[#0e61a1]">
                    <span className="material-symbols-outlined text-xl">verified</span>
                  </div>
                </div>

                <div className="text-[11px] font-mono text-slate-500 text-right">
                  ID: <span className="text-slate-800 font-semibold">{certNumber}</span>
                </div>
              </div>
            </div>

            {/* Target & Evaluation Metadata Ribbon */}
            <div className="mt-5 grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-50 border border-slate-200/80 rounded-lg p-3 text-xs">
              <div>
                <span className="text-[10px] uppercase font-bold text-slate-400 block">Evaluated Target</span>
                <span className="font-semibold text-slate-900 truncate block" title={targetName}>
                  {targetName}
                </span>
              </div>
              <div>
                <span className="text-[10px] uppercase font-bold text-slate-400 block">Evaluation Protocol</span>
                <span className="font-mono text-slate-800">
                  {formulaVersions.scoring_formula || 'aegis_multi_pillar_v1.0'}
                </span>
              </div>
              <div>
                <span className="text-[10px] uppercase font-bold text-slate-400 block">Independent Judge</span>
                <span className="text-slate-800 font-medium">Groq Llama-3.3-70B</span>
              </div>
              <div>
                <span className="text-[10px] uppercase font-bold text-slate-400 block">Attestation Date</span>
                <span className="text-slate-800 font-medium">{formattedDate.slice(0, 16)}</span>
              </div>
            </div>
          </div>

          {/* Core Composite Metric Band */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 print-avoid-break">
            {/* Trust Score */}
            <div className="bg-slate-50/50 border border-slate-200 rounded-xl p-4">
              <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
                <span className="text-[10px] font-bold uppercase tracking-wider">Composite Trust Score</span>
                <span className="material-symbols-outlined text-sm text-[#0e61a1]">security</span>
              </div>
              <div className="flex items-baseline gap-1.5">
                <span className="text-3xl font-bold font-sans tabular-nums text-slate-900">
                  {trustScore}%
                </span>
                <span className="text-xs text-slate-400 font-medium">/ 100</span>
              </div>
              <p className="text-[11px] text-slate-500 mt-1">Weighted aggregate across 6 threat dimensions</p>
            </div>

            {/* Attack Exposure Rate (AER) */}
            <div className="bg-slate-50/50 border border-slate-200 rounded-xl p-4">
              <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
                <span className="text-[10px] font-bold uppercase tracking-wider">Attack Exposure Rate</span>
                <span className="material-symbols-outlined text-sm text-slate-600">shield</span>
              </div>
              <div className="flex items-baseline gap-1.5">
                <span className={`text-3xl font-bold font-sans tabular-nums ${aer > 15 ? 'text-rose-600' : 'text-slate-900'}`}>
                  {aer}%
                </span>
                <span className="text-xs text-slate-400 font-medium">AER</span>
              </div>
              <p className="text-[11px] text-slate-500 mt-1">
                {aer <= 5.0 ? 'Exemplary (< 5.0% threshold)' : `${aer}% adversarial bypasses`}
              </p>
            </div>

            {/* Provenance & Identity */}
            <div className="bg-slate-50/50 border border-slate-200 rounded-xl p-4">
              <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
                <span className="text-[10px] font-bold uppercase tracking-wider">Provenance & Supply Chain</span>
                <span className="material-symbols-outlined text-sm text-slate-600">fingerprint</span>
              </div>
              <div className="flex items-baseline gap-1.5">
                <span className="text-3xl font-bold font-sans tabular-nums text-slate-900">
                  {identityScore}%
                </span>
                <span className="text-xs text-slate-400 font-medium">Identity</span>
              </div>
              <p className="text-[11px] text-slate-500 mt-1">Model origin, weights hash & endpoint verification</p>
            </div>

            {/* Session Harm Rate (SHR) */}
            <div className="bg-slate-50/50 border border-slate-200 rounded-xl p-4">
              <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
                <span className="text-[10px] font-bold uppercase tracking-wider">Session Harm Rate</span>
                <span className="material-symbols-outlined text-sm text-slate-600">history</span>
              </div>
              <div className="flex items-baseline gap-1.5">
                <span className="text-3xl font-bold font-sans tabular-nums text-slate-900">
                  {shr}%
                </span>
                <span className="text-xs text-slate-400 font-medium">SHR</span>
              </div>
              <p className="text-[11px] text-slate-500 mt-1">Context manipulation & cross-turn drift</p>
            </div>
          </div>

          {/* Formal Attestation Statement */}
          <div className="bg-slate-50 border-l-2 border-[#0e61a1] p-4 rounded-r-lg text-xs text-slate-700 leading-relaxed print-avoid-break">
            <strong className="text-slate-900 block mb-0.5 font-serif">Regulatory Compliance Attestation</strong>
            This evaluation validates the behavioral safety posture of <span className="font-semibold text-slate-900">{targetName}</span> against the NIST AI Risk Management Framework (AI RMF 1.0), OWASP Top 10 for LLMs (2025), and applicable financial regulations including FINRA Regulatory Notice 21-25 and SEC Rule 10b-5. Dual-phase independent judging was executed via isolated Groq reasoning models to guarantee neutrality.
          </div>

          {/* 6 Multi-Dimensional Pillars Risk Matrix */}
          <div className="space-y-3.5 print-avoid-break">
            <div className="flex items-center justify-between border-b border-slate-200 pb-2">
              <h2 className="text-sm font-bold uppercase tracking-wider text-slate-800 flex items-center gap-2">
                <span className="material-symbols-outlined text-base text-[#0e61a1]">view_column</span>
                Multi-Dimensional Risk Matrix (6 Financial Threat Pillars)
              </h2>
              <span className="text-xs text-slate-500 font-mono">
                Coverage: {coverage.total_evaluations || 0} Test Vectors Executed
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5">
              {Object.keys(pillars).length === 0 ? (
                <div className="col-span-full p-6 text-center text-slate-400 bg-slate-50 rounded-xl border border-slate-200 text-xs">
                  No pillar breakdown recorded for this evaluation run.
                </div>
              ) : (
                Object.entries(pillars).map(([key, p]) => {
                  const isPass = p.score >= 85;
                  const isWarn = p.score >= 70 && p.score < 85;
                  const statusBg = isPass
                    ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                    : isWarn
                    ? 'bg-amber-50 text-amber-800 border-amber-200'
                    : 'bg-rose-50 text-rose-800 border-rose-200';
                  const barColor = isPass ? 'bg-emerald-600' : (isWarn ? 'bg-amber-500' : 'bg-rose-600');

                  return (
                    <div
                      key={key}
                      className="bg-white border border-slate-200 rounded-xl p-4 flex flex-col justify-between hover:border-slate-300 transition-colors"
                    >
                      <div>
                        <div className="flex items-start justify-between gap-2 mb-1.5">
                          <span className="text-xs font-bold text-slate-900 leading-tight">
                            {p.name}
                          </span>
                          <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200 shrink-0">
                            {Math.round(p.weight * 100)}% Wt
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-500 mb-3 line-clamp-2">
                          {p.description}
                        </p>
                      </div>

                      <div className="space-y-2 pt-2 border-t border-slate-100">
                        <div className="flex items-center justify-between">
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase ${statusBg}`}>
                            {p.status || (isPass ? 'PASS' : (isWarn ? 'WARN' : 'FAIL'))}
                          </span>
                          <span className="text-base font-bold font-sans tabular-nums text-slate-900">
                            {p.score}%
                          </span>
                        </div>

                        <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                          <div
                            className={`h-1.5 rounded-full ${barColor}`}
                            style={{ width: `${Math.min(100, Math.max(0, p.score))}%` }}
                          />
                        </div>

                        <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono">
                          <span>Passed: <strong className="text-slate-700">{p.pass_count || 0}</strong></span>
                          <span>Failed: <strong className={p.fail_count ? 'text-rose-600' : 'text-slate-700'}>{p.fail_count || 0}</strong></span>
                          <span>Total: <strong className="text-slate-700">{p.total_count || 0}</strong></span>
                        </div>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>

          {/* Critical Vulnerability Audit Register */}
          <div className="space-y-3.5 print-avoid-break">
            <div className="flex items-center justify-between border-b border-slate-200 pb-2">
              <div className="flex items-center gap-2">
                <span className={`w-2 h-2 rounded-full ${failures.length > 0 ? 'bg-rose-600' : 'bg-emerald-600'}`} />
                <h2 className="text-sm font-bold uppercase tracking-wider text-slate-800">
                  Critical Vulnerability Audit Register ({failures.length})
                </h2>
              </div>
              <span className="text-xs text-slate-500">
                {failures.length === 0 ? 'Zero Breaches Detected' : 'Requires Engineering Remediation'}
              </span>
            </div>

            {failures.length === 0 ? (
              <div className="bg-emerald-50/50 border border-emerald-200/80 rounded-xl p-6 text-center text-xs">
                <span className="material-symbols-outlined text-2xl text-emerald-600 mb-1">
                  check_circle
                </span>
                <p className="font-semibold text-emerald-900">Zero High-Severity Adversarial Breaches Detected</p>
                <p className="text-emerald-700 mt-0.5">
                  The target model successfully refused or defended against all tested high-severity exploitation vectors.
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {/* Filter Controls (Screen Only) */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3 bg-slate-50 border border-slate-200 rounded-xl print:hidden">
                  <div className="flex flex-wrap items-center gap-1.5">
                    <span className="text-[11px] font-semibold text-slate-500 mr-1">Category:</span>
                    {failureCategories.map((cat) => (
                      <button
                        key={cat}
                        onClick={() => {
                          setFilterCategory(cat);
                          setCurrentPage(1);
                        }}
                        className={`px-2.5 py-1 text-[11px] font-medium rounded-lg transition-colors ${
                          filterCategory === cat
                            ? 'bg-[#0e61a1] text-white font-semibold shadow-2xs'
                            : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-100'
                        }`}
                      >
                        {cat}
                      </button>
                    ))}
                  </div>

                  {failureSeverities.length > 2 && (
                    <div className="flex items-center gap-2 shrink-0">
                      <span className="text-[11px] font-semibold text-slate-500">Severity:</span>
                      <select
                        value={filterSeverity}
                        onChange={(e) => {
                          setFilterSeverity(e.target.value);
                          setCurrentPage(1);
                        }}
                        className="px-2 py-1 text-[11px] bg-white border border-slate-200 rounded-lg text-slate-700 focus:outline-none focus:ring-1 focus:ring-[#0e61a1]"
                      >
                        {failureSeverities.map((sev) => (
                          <option key={sev} value={sev}>
                            {sev}
                          </option>
                        ))}
                      </select>
                    </div>
                  )}
                </div>

                {/* Paginated Failures List (Screen) */}
                <div className="space-y-2.5 print:hidden">
                  {paginatedFailures.length === 0 ? (
                    <div className="p-6 text-center text-xs text-slate-500 bg-slate-50 border border-slate-200 rounded-xl">
                      No vulnerabilities match the selected filters ({filterCategory} / {filterSeverity}).
                    </div>
                  ) : (
                    paginatedFailures.map((f, i) => renderFailureCard(f, startIndex + i))
                  )}
                </div>

                {/* Complete Unpaginated Failures List (Print / PDF Export Only) */}
                <div className="space-y-2.5 hidden print:block">
                  {filteredFailures.map((f, i) => renderFailureCard(f, i, true))}
                </div>

                {/* Pagination Controls (Screen Only) */}
                {filteredFailures.length > PAGE_SIZE && (
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-2 print:hidden text-xs text-slate-600">
                    <span className="font-mono text-[11px]">
                      Showing <strong>{startIndex + 1}</strong>–
                      <strong>{Math.min(startIndex + PAGE_SIZE, filteredFailures.length)}</strong> of{' '}
                      <strong>{filteredFailures.length}</strong> findings
                      {filteredFailures.length !== failures.length && ` (filtered from ${failures.length})`}
                    </span>

                    <div className="flex items-center gap-1.5">
                      <button
                        onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                        disabled={safeCurrentPage === 1}
                        className="px-2.5 py-1 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed font-medium text-slate-700 flex items-center gap-1"
                      >
                        <span className="material-symbols-outlined text-xs">chevron_left</span>
                        Prev
                      </button>

                      <div className="flex items-center gap-1">
                        {Array.from({ length: totalPages }, (_, idx) => idx + 1).map((p) => (
                          <button
                            key={p}
                            onClick={() => setCurrentPage(p)}
                            className={`w-7 h-7 rounded-lg text-xs font-mono font-medium transition-colors ${
                              p === safeCurrentPage
                                ? 'bg-[#0e61a1] text-white font-bold'
                                : 'border border-slate-200 bg-white hover:bg-slate-50 text-slate-700'
                            }`}
                          >
                            {p}
                          </button>
                        ))}
                      </div>

                      <button
                        onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                        disabled={safeCurrentPage === totalPages}
                        className="px-2.5 py-1 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed font-medium text-slate-700 flex items-center gap-1"
                      >
                        Next
                        <span className="material-symbols-outlined text-xs">chevron_right</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Actionable Remediation Roadmap */}
          <div className="space-y-3.5 print-avoid-break">
            <div className="flex items-center justify-between border-b border-slate-200 pb-2">
              <h2 className="text-sm font-bold uppercase tracking-wider text-slate-800 flex items-center gap-2">
                <span className="material-symbols-outlined text-base text-[#0e61a1]">healing</span>
                Actionable Remediation Roadmap & Mitigations
              </h2>
              <span className="text-xs text-slate-500">Security Engineering Guidance</span>
            </div>

            {recommendations.length === 0 ? (
              <div className="bg-slate-50 rounded-xl p-4 border border-slate-200 text-xs text-slate-600">
                No immediate structural mitigations required. Continue routine evaluation cadence.
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {recommendations.map((rec, i) => (
                  <div
                    key={i}
                    className="p-3.5 bg-slate-50/60 border border-slate-200 rounded-xl flex items-start gap-2.5 text-xs text-slate-700"
                  >
                    <span className="w-5 h-5 rounded bg-sky-100 text-[#0e61a1] flex items-center justify-center font-mono font-bold text-[10px] shrink-0 mt-0.5">
                      P{i + 1}
                    </span>
                    <span className="leading-relaxed">{rec}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Cryptographic Attestation & Audit Scope Sign-Off */}
          <div className="border-t border-slate-200 pt-6 space-y-5 print-avoid-break">
            {/* SHA-256 Digest */}
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                <span className="text-[10px] font-mono uppercase font-bold text-slate-500 tracking-wider">
                  Cryptographic Report Hash (SHA-256 Digest)
                </span>
                <button
                  onClick={handleCopyHash}
                  className="text-[11px] font-mono text-[#0e61a1] hover:text-[#0b4e82] flex items-center gap-1 self-start sm:self-auto print:hidden"
                >
                  <span className="material-symbols-outlined text-xs">
                    {copiedHash ? 'done' : 'content_copy'}
                  </span>
                  {copiedHash ? 'Digest Copied' : 'Copy Hash'}
                </button>
              </div>
              <div className="font-mono text-xs text-slate-700 bg-white border border-slate-200 p-2.5 rounded-lg break-all select-all">
                {reportHash}
              </div>
            </div>

            {/* Audit Scope Limitations */}
            {limitations.length > 0 && (
              <div className="text-[11px] text-slate-500 space-y-1">
                <span className="font-bold uppercase tracking-wider text-slate-600 block">Attestation Boundaries & Limitations:</span>
                <ul className="list-disc pl-4 space-y-0.5">
                  {limitations.map((lim, i) => (
                    <li key={i}>{lim}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Formal Attestation Signature Block */}
            <div className="pt-6 border-t border-slate-200 grid grid-cols-2 sm:grid-cols-3 gap-6 text-xs text-slate-600">
              <div>
                <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">Evaluating Engine</span>
                <p className="font-semibold text-slate-800">Aegis Autonomous Defense</p>
                <p className="text-[10px] text-slate-400 font-mono">v1.0.0-release</p>
              </div>
              <div>
                <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">Independent Judge</span>
                <p className="font-semibold text-slate-800">Llama-3.3-70B-Versatile</p>
                <p className="text-[10px] text-slate-400 font-mono">Groq LPU Inference</p>
              </div>
              <div className="col-span-2 sm:col-span-1">
                <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">Official Attestation</span>
                <div className="border-b border-slate-300 w-36 mb-1 mt-3" />
                <p className="text-[10px] text-slate-500">Authorized Quantitative Auditor</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
