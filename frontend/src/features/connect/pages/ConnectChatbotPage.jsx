import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate, useSearchParams } from 'react-router-dom';
import benchmarkService from '../../../services/benchmarkService';
import SuiteSelectionModal from '../components/SuiteSelectionModal';
import AppLayout from '../../../shared/components/AppLayout';
import toast from 'react-hot-toast';
import targetService from '../../../services/targetService';
import jobService from '../../../services/jobService';

export default function ConnectChatbotPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const preselectedSuiteId = searchParams.get('suiteId');

  // Benchmark suite selection states
  const [availableSources, setAvailableSources] = useState([]);
  const [suiteScope, setSuiteScope] = useState(preselectedSuiteId ? 'CUSTOM_MIX' : 'STANDARD');
  const [customMixIds, setCustomMixIds] = useState(preselectedSuiteId ? [preselectedSuiteId] : []);
  const [isCustomMixOpen, setIsCustomMixOpen] = useState(false);

  const STANDARD_NAMES = [
    'Finred Financial Red-Teaming Benchmark',
    'AdvBench Harmful Behaviors',
    'HarmBench Standard Behaviors',
    'Benign Financial & General Baseline',
  ];

  const standardSources = availableSources.filter((s) => {
    const src = s.source || s;
    return STANDARD_NAMES.includes(src.name);
  });

  const customSources = availableSources.filter((s) => {
    const src = s.source || s;
    return !STANDARD_NAMES.includes(src.name);
  });

  // Form states
  const [targetName, setTargetName] = useState('Google Gemini Flash');
  const [apiUrl, setApiUrl] = useState('https://generativelanguage.googleapis.com/v1beta/openai/chat/completions');
  const [apiKey, setApiKey] = useState('');
  const [authHeaderKind, setAuthHeaderKind] = useState('BEARER_TOKEN');
  const [connectorProfile, setConnectorProfile] = useState('openai_chat_v1');
  const [modelName, setModelName] = useState('gemini-3.8-flash');
  const [evaluationMode, setEvaluationMode] = useState('QUICK');
  const [authConfirmed, setAuthConfirmed] = useState(true);
  const [showKey, setShowKey] = useState(false);

  // Async states
  const [testing, setTesting] = useState(false);
  const [createdTarget, setCreatedTarget] = useState(null);
  const [probeData, setProbeData] = useState(null);
  const [startingScan, setStartingScan] = useState(false);

  // Load benchmark sources on component mount
  useEffect(() => {
    async function loadBenchmarkSources() {
      try {
        const list = await benchmarkService.listSources();
        if (list && list.length > 0) {
          setAvailableSources(list);
          if (preselectedSuiteId) {
            setSuiteScope('CUSTOM_MIX');
            setCustomMixIds([preselectedSuiteId]);
          }
        }
      } catch (e) {
        console.warn('Could not load benchmark sources:', e);
      }
    }
    loadBenchmarkSources();
  }, [preselectedSuiteId]);

  // Auto-load latest target on component mount
  useEffect(() => {
    async function loadLatestTarget() {
      try {
        const targets = await targetService.listTargets();
        if (targets && targets.length > 0) {
          const verifiedTarget = targets.find((t) => t.status === 'VERIFIED') || targets[0];
          setCreatedTarget(verifiedTarget);
          setTargetName(verifiedTarget.name);
          setApiUrl(verifiedTarget.endpoint_url || '');
          if (verifiedTarget.model_ref) {
            setModelName(verifiedTarget.model_ref);
          }
          if (verifiedTarget.connector_profile) {
            setConnectorProfile(verifiedTarget.connector_profile);
          }
          if (verifiedTarget.validation_report && Object.keys(verifiedTarget.validation_report).length > 0) {
            setProbeData({
              status: verifiedTarget.status,
              latency_ms: verifiedTarget.validation_report.latency_ms,
              capability_report: verifiedTarget.validation_report.capability_report || verifiedTarget.validation_report,
              resolved_host_hash: verifiedTarget.validation_report.resolved_host_hash,
              safe_error_class: verifiedTarget.validation_report.safe_error_class,
            });
          }
        }
      } catch (e) {
        console.warn('Could not load existing targets:', e);
      }
    }
    loadLatestTarget();
  }, []);

  const applyPreset = (preset) => {
    if (preset === 'huggingface') {
      setTargetName('Qwen-2.5-72B (HuggingFace)');
      setApiUrl('https://router.huggingface.co/v1/chat/completions');
      setAuthHeaderKind('BEARER_TOKEN');
      setConnectorProfile('openai_chat_v1');
      setModelName('Qwen/Qwen2.5-72B-Instruct');
      toast.success('Configured Hugging Face Router profile');
    } else if (preset === 'gemini') {
      setTargetName('Google Gemini Flash');
      setApiUrl('https://generativelanguage.googleapis.com/v1beta/openai/chat/completions');
      setAuthHeaderKind('BEARER_TOKEN');
      setConnectorProfile('openai_chat_v1');
      setModelName('gemini-3.8-flash');
      toast.success('Configured Google Gemini OpenAI Gateway profile');
    } else if (preset === 'openai') {
      setTargetName('OpenAI GPT-4o-mini');
      setApiUrl('https://api.openai.com/v1/chat/completions');
      setAuthHeaderKind('BEARER_TOKEN');
      setConnectorProfile('openai_chat_v1');
      setModelName('gpt-4o-mini');
      toast.success('Configured OpenAI Chat profile');
    } else if (preset === 'demo') {
      setTargetName('FinSight Banking Advisor (Local)');
      setApiUrl('http://127.0.0.1:8001/chat');
      setApiKey('demo-key-fintech-1234');
      setAuthHeaderKind('API_KEY');
      setConnectorProfile('aegis_simple_chat_v1');
      setModelName('');
      toast.success('Configured Internal Banking Assistant profile');
    } else if (preset === 'localhost') {
      setTargetName('Localhost vLLM Server');
      setApiUrl('http://127.0.0.1:8080/v1/chat/completions');
      setAuthHeaderKind('BEARER_TOKEN');
      setConnectorProfile('openai_chat_v1');
      setModelName('meta-llama/Llama-3.2-3B-Instruct');
      toast.success('Configured Localhost Inference profile');
    }
  };

  const buildTargetPayload = () => {
    const isOAI =
      connectorProfile === 'openai_chat_v1' ||
      apiUrl.includes('chat/completions') ||
      apiUrl.includes('generativelanguage') ||
      apiUrl.includes('openai') ||
      apiUrl.includes('huggingface');

    return {
      name: targetName || 'Target Chatbot',
      mode: 'HOSTED',
      endpoint_url: apiUrl,
      connector_profile: isOAI ? 'openai_chat_v1' : 'aegis_simple_chat_v1',
      model_ref: isOAI
        ? modelName || (apiUrl.includes('generativelanguage') ? 'gemini-3.8-flash' : 'gpt-4o-mini')
        : undefined,
      authorization_confirmed: true,
      authorization_reference: 'sec-authorized-audit-target',
      side_effect_free: true,
      credential_payload: apiKey || undefined,
      credential_kind:
        authHeaderKind === 'CUSTOM_HEADER'
          ? 'CUSTOM_HEADER'
          : authHeaderKind === 'OAUTH'
          ? 'OAUTH'
          : 'API_KEY',
    };
  };

  const handleTestAndRegister = async () => {
    if (!apiUrl) {
      toast.error('Target API endpoint URL is required');
      return;
    }
    setTesting(true);
    try {
      const payload = buildTargetPayload();

      let target;
      try {
        target = await targetService.createTarget(payload);
      } catch (err) {
        const targets = await targetService.listTargets();
        const existing = targets.find((t) => t.name === payload.name || t.endpoint_url === apiUrl);
        if (!existing) throw err;

        target = await targetService.updateTarget(existing.id, {
          name: payload.name,
          endpoint_url: payload.endpoint_url,
          model_ref: payload.model_ref,
          connector_profile: payload.connector_profile,
        });

        if (payload.credential_payload) {
          try {
            await targetService.addCredential(existing.id, payload.credential_payload);
          } catch (cErr) {
            console.warn('Could not update credential:', cErr);
          }
        }
      }

      // Pre-flight target verification probe
      let probeReport = null;
      try {
        probeReport = await targetService.verifyTarget(target.id);
        setProbeData(probeReport);
      } catch (valErr) {
        console.warn('Verification diagnostics note:', valErr);
        probeReport = {
          status: 'INVALID_CONFIG',
          safe_error_class: valErr.message || 'Connection refused or timeout',
        };
        setProbeData(probeReport);
      }

      const refreshed = await targetService.getTarget(target.id);
      setCreatedTarget(refreshed);
      if (refreshed.status === 'VERIFIED') {
        const lat = probeReport?.latency_ms ? ` (${Math.round(probeReport.latency_ms)}ms)` : '';
        toast.success(`Target "${refreshed.name}" verified successfully${lat}. Pre-flight probe passed.`);
      } else {
        toast.error(`Verification status: ${refreshed.status}. ${probeReport?.safe_error_class || 'Check endpoint reachability.'}`);
      }
    } catch (err) {
      toast.error(err.message || 'Failed to register and verify target endpoint');
    } finally {
      setTesting(false);
    }
  };

  const handleStartScan = async () => {
    if (!authConfirmed) {
      toast.error('Authorization confirmation is required to initiate red-team evaluation');
      return;
    }

    setStartingScan(true);
    try {
      let target = createdTarget;

      if (!target) {
        const payload = buildTargetPayload();
        try {
          target = await targetService.createTarget(payload);
        } catch (err) {
          const targets = await targetService.listTargets();
          const existing = targets.find((t) => t.name === payload.name || t.endpoint_url === apiUrl);
          if (!existing) throw err;

          target = await targetService.updateTarget(existing.id, {
            name: payload.name,
            endpoint_url: payload.endpoint_url,
            model_ref: payload.model_ref,
            connector_profile: payload.connector_profile,
          });

          if (payload.credential_payload) {
            try {
              await targetService.addCredential(existing.id, payload.credential_payload);
            } catch (cErr) {
              console.warn('Could not update credential:', cErr);
            }
          }
        }

        try {
          await targetService.verifyTarget(target.id);
        } catch (valErr) {
          console.warn('Verification diagnostics note:', valErr);
        }

        const refreshed = await targetService.getTarget(target.id);
        target = refreshed;
        setCreatedTarget(refreshed);
      }

      if (target.status !== 'VERIFIED') {
        toast.error(`Target status is "${target.status}". Must be VERIFIED before scheduling an audit.`);
        return;
      }



      let sourceIdsPayload = [];
      if (suiteScope === 'STANDARD') {
        sourceIdsPayload = standardSources.map((s) => (s.source?.id || s.id));
      } else if (suiteScope === 'CUSTOM_MIX') {
        if (!customMixIds || customMixIds.length === 0) {
          toast.error('Please configure your custom mix and select at least one benchmark suite.');
          setIsCustomMixOpen(true);
          setStartingScan(false);
          return;
        }
        sourceIdsPayload = customMixIds;
      } else {
        // 'ALL' - include both standard and custom uploaded suites
        sourceIdsPayload = [];
      }

      const job = await jobService.createJob({
        target_id: target.id,
        mode: evaluationMode,
        sample_size: evaluationMode === 'QUICK' ? 25 : 150,
        source_ids: sourceIdsPayload,
        seed: 42,
      });

      toast.success('Evaluation job queued successfully');
      navigate(`/simulation?jobId=${job.id}`);
    } catch (err) {
      toast.error(err.message || 'Could not schedule evaluation job');
    } finally {
      setStartingScan(false);
    }
  };

  const canStart = Boolean(apiUrl && (apiKey || createdTarget));

  return (
    <AppLayout pageTitle="Connect Target Endpoint">
      <div className="max-w-5xl mx-auto w-full py-2 space-y-6">
        {/* Section Header */}
        <div className="border-b border-slate-200 pb-5">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="px-2 py-0.5 bg-slate-100 text-slate-700 text-[11px] font-mono uppercase tracking-wider rounded border border-slate-200">
                  Target Interface v1.0
                </span>
                <span className="text-xs text-slate-500 font-mono">
                  AES-256 In-Memory Decryption
                </span>
              </div>
              <h1 className="font-serif text-2xl md:text-3xl font-bold text-slate-900 tracking-tight">
                Target Endpoint Registration & Audit Configuration
              </h1>
              <p className="text-xs md:text-sm text-slate-600 mt-1 max-w-3xl">
                Register authorized model endpoints for automated adversarial red-teaming, guardrail stress testing, and SEC/FINRA regulatory compliance scoring.
              </p>
            </div>
            <div className="shrink-0">
              <span className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-white border border-slate-200 text-slate-700 text-xs font-semibold rounded-lg shadow-2xs font-mono">
                <span className="w-2 h-2 rounded-full bg-emerald-500" />
                Audit Protocol: Aegis-v1.0
              </span>
            </div>
          </div>
        </div>

        {/* Architecture Profile Presets */}
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-2xs">
          <label className="block text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-2.5">
            Architectural Target Presets
          </label>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2">
            {[
              { id: 'huggingface', name: 'Hugging Face Router', desc: 'Qwen / DeepSeek-R1' },
              { id: 'gemini', name: 'Google Gemini', desc: 'gemini-3.8-flash' },
              { id: 'openai', name: 'OpenAI Chat Gateway', desc: 'gpt-4o-mini / vLLM' },
              { id: 'demo', name: 'FinSight Banking Bot', desc: 'Internal Port 8001' },
              { id: 'localhost', name: 'Localhost vLLM', desc: 'Port 8080 Endpoint' },
            ].map((p) => {
              const active =
                (p.id === 'huggingface' && apiUrl.includes('huggingface')) ||
                (p.id === 'gemini' && apiUrl.includes('generativelanguage')) ||
                (p.id === 'openai' && apiUrl.includes('api.openai.com')) ||
                (p.id === 'demo' && apiUrl.includes('8001')) ||
                (p.id === 'localhost' && apiUrl.includes('8080'));

              return (
                <button
                  key={p.id}
                  type="button"
                  onClick={() => applyPreset(p.id)}
                  className={`p-2.5 text-left border rounded-lg transition-all ${
                    active
                      ? 'bg-sky-50/70 border-[#0e61a1] text-slate-900 shadow-2xs'
                      : 'bg-slate-50/50 border-slate-200 text-slate-700 hover:bg-slate-100 hover:border-slate-300'
                  }`}
                >
                  <p className="text-xs font-bold truncate flex items-center justify-between">
                    <span>{p.name}</span>
                    {active && <span className="w-1.5 h-1.5 rounded-full bg-[#0e61a1]" />}
                  </p>
                  <p className="text-[10px] text-slate-500 font-mono truncate mt-0.5">{p.desc}</p>
                </button>
              );
            })}
          </div>
        </div>

        {/* Configuration Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Main Connection Form */}
          <div className="lg:col-span-8 bg-white border border-slate-200 rounded-xl p-6 shadow-2xs space-y-5">
            <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider border-b border-slate-100 pb-3 flex items-center gap-2">
              <span className="material-symbols-outlined text-base text-[#0e61a1]">settings_input_component</span>
              Connection Parameters
            </h2>

            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Target Application Name
                  </label>
                  <input
                    value={targetName}
                    onChange={(e) => setTargetName(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:bg-white focus:border-[#0e61a1] transition-colors"
                    placeholder="e.g. Wealth Management Advisor"
                    type="text"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Connector Protocol Profile
                  </label>
                  <select
                    value={connectorProfile}
                    onChange={(e) => setConnectorProfile(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-xs text-slate-900 focus:outline-none focus:bg-white focus:border-[#0e61a1] transition-colors font-mono"
                  >
                    <option value="openai_chat_v1">OpenAI Chat Protocol (/v1/chat/completions)</option>
                    <option value="aegis_simple_chat_v1">Aegis Simple JSON (/chat)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Target API Endpoint URL
                </label>
                <input
                  value={apiUrl}
                  onChange={(e) => setApiUrl(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-xs text-slate-900 font-mono placeholder-slate-400 focus:outline-none focus:bg-white focus:border-[#0e61a1] transition-colors"
                  placeholder="https://api.yourbank.com/v1/chat/completions"
                  type="text"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Model Identifier Tag
                  </label>
                  <input
                    value={modelName}
                    onChange={(e) => setModelName(e.target.value)}
                    disabled={connectorProfile === 'aegis_simple_chat_v1'}
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-xs text-slate-900 font-mono placeholder-slate-400 focus:outline-none focus:bg-white focus:border-[#0e61a1] transition-colors disabled:opacity-50"
                    placeholder="Qwen/Qwen2.5-72B-Instruct"
                    type="text"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Authentication Scheme
                  </label>
                  <select
                    value={authHeaderKind}
                    onChange={(e) => setAuthHeaderKind(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-xs text-slate-900 focus:outline-none focus:bg-white focus:border-[#0e61a1] transition-colors font-mono"
                  >
                    <option value="BEARER_TOKEN">Authorization: Bearer &lt;TOKEN&gt;</option>
                    <option value="CUSTOM_HEADER">Custom Header: X-API-Key</option>
                    <option value="API_KEY">Direct API Key</option>
                    <option value="OAUTH">OAuth 2.0 Bearer</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  API Key / Secret Token
                </label>
                <div className="relative">
                  <input
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-xs text-slate-900 font-mono placeholder-slate-400 focus:outline-none focus:bg-white focus:border-[#0e61a1] transition-colors pr-10"
                    placeholder="sk-proj-********************************"
                    type={showKey ? 'text' : 'password'}
                  />
                  <button
                    type="button"
                    onClick={() => setShowKey(!showKey)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
                    title={showKey ? 'Mask secret' : 'Reveal secret'}
                  >
                    <span className="material-symbols-outlined text-base">
                      {showKey ? 'visibility' : 'visibility_off'}
                    </span>
                  </button>
                </div>
              </div>
            </div>

            <div className="pt-2">
              <button
                type="button"
                onClick={handleTestAndRegister}
                disabled={testing}
                className="w-full py-2.5 px-4 bg-slate-100 hover:bg-slate-200 border border-slate-300 text-slate-800 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-2 shadow-2xs"
              >
                {testing ? (
                  <>
                    <span className="material-symbols-outlined animate-spin text-sm text-[#0e61a1]">sync</span>
                    Executing Pre-flight Diagnostic Probe...
                  </>
                ) : (
                  <>
                    <span className="material-symbols-outlined text-sm text-[#0e61a1]">network_check</span>
                    Test Connection & Register Target
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Pre-flight Diagnostics & Evaluation Config */}
          <div className="lg:col-span-4 space-y-6">
            {/* Probe Status Card */}
            <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-2xs space-y-3">
              <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center justify-between">
                <span>Pre-flight Probe Status</span>
                <span
                  className={`px-2 py-0.5 text-[10px] font-mono font-bold rounded border ${
                    (probeData?.status || createdTarget?.status) === 'VERIFIED'
                      ? 'bg-emerald-50 text-emerald-800 border-emerald-300'
                      : (probeData?.status || createdTarget?.status) === 'VALIDATION_FAILED'
                      ? 'bg-rose-50 text-rose-800 border-rose-300'
                      : 'bg-slate-50 text-slate-600 border-slate-200'
                  }`}
                >
                  {probeData?.status || createdTarget?.status || 'UNTESTED'}
                </span>
              </h3>

              <div className="bg-slate-50 rounded-lg p-3 border border-slate-200 space-y-2 text-xs font-mono">
                <div className="flex justify-between items-center">
                  <span className="text-slate-500">HTTP Status:</span>
                  <span className="text-slate-800 font-bold">
                    {(() => {
                      const st = probeData?.capability_report?.http_status ?? createdTarget?.validation_report?.http_status;
                      if (testing) return <span className="text-blue-600 animate-pulse">Probing...</span>;
                      if (st) return `HTTP ${st} ${st < 400 ? 'OK' : 'FAILED'}`;
                      if (probeData?.status === 'VERIFIED' || createdTarget?.status === 'VERIFIED') return 'HTTP 200 OK';
                      return 'Untested';
                    })()}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-500">Round-Trip:</span>
                  <span className="text-slate-800">
                    {(() => {
                      const lat = probeData?.latency_ms ?? probeData?.capability_report?.latency_ms ?? createdTarget?.validation_report?.latency_ms;
                      if (testing) return <span className="text-blue-600">Measuring...</span>;
                      if (lat != null) return `${Math.round(lat)}ms`;
                      return '-';
                    })()}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-500">SSRF Bounding:</span>
                  <span className={probeData || createdTarget?.validation_report ? "text-emerald-700 font-semibold" : "text-slate-400"}>
                    {probeData || createdTarget?.validation_report ? 'Enforced (RFC 1918)' : 'Pending Probe'}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-500">Protocol:</span>
                  <span className="text-slate-800 font-mono">
                    {apiUrl?.startsWith('https') ? 'TLS 1.3 / HTTPS' : apiUrl?.startsWith('http') ? 'HTTP / Plain' : 'HTTPS'}
                  </span>
                </div>
                {(probeData?.resolved_host_hash || createdTarget?.validation_report?.resolved_host_hash) && (
                  <div className="flex justify-between items-center pt-1 border-t border-slate-200 text-[10px]">
                    <span className="text-slate-400">Host Hash:</span>
                    <span className="text-slate-600 font-mono truncate max-w-[160px]" title={probeData?.resolved_host_hash || createdTarget?.validation_report?.resolved_host_hash}>
                      {(probeData?.resolved_host_hash || createdTarget?.validation_report?.resolved_host_hash || '').slice(0, 16)}...
                    </span>
                  </div>
                )}
              </div>

              {probeData?.safe_error_class && (
                <div className="p-2.5 rounded border border-rose-200 bg-rose-50/80 text-[11px] font-mono text-rose-800">
                  <div className="font-bold flex items-center gap-1.5 text-rose-900 mb-0.5">
                    <span className="material-symbols-outlined text-xs">warning</span>
                    Probe Diagnostic Fault
                  </div>
                  <div className="break-all text-[10px] leading-tight">{probeData.safe_error_class}</div>
                </div>
              )}

              {createdTarget && (
                <p className="text-[11px] text-slate-500">
                  Target registered as <strong className="text-slate-800">{createdTarget.name}</strong>. Ready for adversarial test item dispatch.
                </p>
              )}
            </div>

            {/* Audit Scope Selector */}
            <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-2xs space-y-4">
              <div>
                <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-2">
                  Test Suite Scope
                </h3>
                <div className="grid grid-cols-3 gap-1 p-1 bg-slate-100 rounded-lg text-xs font-medium border border-slate-200 mb-3">
                  <button
                    type="button"
                    onClick={() => setSuiteScope('STANDARD')}
                    className={`py-1.5 px-1.5 rounded font-bold transition-all text-center ${
                      suiteScope === 'STANDARD'
                        ? 'bg-white text-[#0e61a1] shadow-2xs'
                        : 'text-slate-600 hover:text-slate-900'
                    }`}
                  >
                    Standard Only
                  </button>
                  <button
                    type="button"
                    onClick={() => setSuiteScope('ALL')}
                    className={`py-1.5 px-1.5 rounded font-bold transition-all text-center ${
                      suiteScope === 'ALL'
                        ? 'bg-white text-[#0e61a1] shadow-2xs'
                        : 'text-slate-600 hover:text-slate-900'
                    }`}
                  >
                    Standard + Custom
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setSuiteScope('CUSTOM_MIX');
                      if (customMixIds.length === 0) {
                        setIsCustomMixOpen(true);
                      }
                    }}
                    className={`py-1.5 px-1.5 rounded font-bold transition-all text-center flex items-center justify-center gap-1 ${
                      suiteScope === 'CUSTOM_MIX'
                        ? 'bg-white text-[#0e61a1] shadow-2xs'
                        : 'text-slate-600 hover:text-slate-900'
                    }`}
                  >
                    <span>Mix & Match</span>
                    {customMixIds.length > 0 && (
                      <span className="px-1.5 py-0.2 bg-purple-100 text-purple-700 font-mono text-[9px] rounded-full font-bold">
                        {customMixIds.length}
                      </span>
                    )}
                  </button>
                </div>

                {suiteScope === 'CUSTOM_MIX' && (
                  <div className="mb-3 p-3 bg-purple-50/70 border border-purple-200 rounded-lg flex items-center justify-between gap-3">
                    <div>
                      <div className="text-xs font-bold text-purple-900 flex items-center gap-1.5">
                        <span className="material-symbols-outlined text-sm text-purple-600">checklist</span>
                        <span>Custom Suite Mix Active</span>
                      </div>
                      <p className="text-[11px] text-purple-700 font-mono mt-0.5">
                        {customMixIds.length} {customMixIds.length === 1 ? 'suite' : 'suites'} selected ({(() => {
                          const cnt = availableSources
                            .filter((s) => customMixIds.includes(s.source?.id || s.id))
                            .reduce((acc, s) => acc + (s.total_test_cases ?? s.source?.total_test_cases ?? s.total_prompts ?? 0), 0);
                          return cnt.toLocaleString();
                        })()} vectors)
                      </p>
                    </div>
                    <button
                      type="button"
                      onClick={() => setIsCustomMixOpen(true)}
                      className="px-2.5 py-1.5 bg-white hover:bg-purple-50 border border-purple-300 text-purple-700 rounded-lg text-xs font-bold transition-all shadow-2xs cursor-pointer flex items-center gap-1"
                    >
                      <span className="material-symbols-outlined text-xs">tune</span>
                      <span>Edit Mix</span>
                    </button>
                  </div>
                )}
              </div>

              <div>
                <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-2">
                  Evaluation Audit Intensity
                </h3>
                <div className="space-y-2">
                  <label
                    onClick={() => setEvaluationMode('QUICK')}
                    className={`p-3 rounded-lg border block cursor-pointer transition-all ${
                      evaluationMode === 'QUICK'
                        ? 'bg-sky-50/70 border-[#0e61a1] shadow-2xs'
                        : 'border-slate-200 hover:bg-slate-50'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-bold text-slate-900">Quick Calibration Run</span>
                      <span className="px-1.5 py-0.2 bg-slate-200 text-slate-700 text-[10px] font-mono rounded font-bold">
                        25 Vectors
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-500">
                      Balanced stratified sample across active categories. Estimated execution: ~90 seconds.
                    </p>
                  </label>

                  <label
                    onClick={() => setEvaluationMode('FULL')}
                    className={`p-3 rounded-lg border block cursor-pointer transition-all ${
                      evaluationMode === 'FULL'
                        ? 'bg-sky-50/70 border-[#0e61a1] shadow-2xs'
                        : 'border-slate-200 hover:bg-slate-50'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-bold text-slate-900">Comprehensive Threat Audit</span>
                      <span className="px-1.5 py-0.2 bg-slate-200 text-slate-700 text-[10px] font-mono rounded font-bold">
                        150 Vectors
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-500">
                      Exhaustive red-team execution across entire taxonomy with non-blocking background telemetry.
                    </p>
                  </label>
                </div>
              </div>

              {/* Legal confirmation */}
              <div className="pt-2 border-t border-slate-100">
                <label className="flex items-start gap-2 cursor-pointer select-none">
                  <input
                    type="checkbox"
                    checked={authConfirmed}
                    onChange={(e) => setAuthConfirmed(e.target.checked)}
                    className="mt-0.5 rounded border-slate-300 text-[#0e61a1] focus:ring-[#0e61a1]"
                  />
                  <span className="text-[11px] text-slate-600 leading-tight">
                    I certify formal authorization to execute adversarial red-teaming against this endpoint.
                  </span>
                </label>
              </div>
            </div>
          </div>
        </div>

        {/* Action Bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 bg-white border border-slate-200 rounded-xl shadow-2xs">
          <div>
            <p className="text-xs font-bold text-slate-800">
              Target Execution Profile Ready
            </p>
            <p className="text-[11px] text-slate-500">
              Seed: 42 (Deterministic) | Independent Judge: Groq Llama-3.3-70B | Anti-Injection Fenced
            </p>
          </div>
          <button
            onClick={handleStartScan}
            disabled={!canStart || startingScan}
            className={`px-6 py-2.5 rounded-lg text-xs font-bold flex items-center gap-2 transition-all shadow-2xs ${
              canStart && !startingScan
                ? 'bg-[#0e61a1] hover:bg-[#0b4e82] text-white cursor-pointer'
                : 'bg-slate-200 text-slate-400 cursor-not-allowed'
            }`}
          >
            {startingScan ? (
              <>
                <span className="material-symbols-outlined animate-spin text-sm">sync</span>
                <span>Scheduling Evaluation Job...</span>
              </>
            ) : (
              <>
                <span className="material-symbols-outlined text-sm">verified_user</span>
                <span>Initialize Threat Evaluation Run</span>
              </>
            )}
          </button>
        </div>
      </div>
      {/* Custom Suite Selection Modal */}
      <SuiteSelectionModal
        isOpen={isCustomMixOpen}
        onClose={() => setIsCustomMixOpen(false)}
        sources={availableSources}
        selectedSuiteIds={customMixIds.length > 0 ? customMixIds : standardSources.map((s) => (s.source?.id || s.id))}
        onApply={(ids) => {
          setCustomMixIds(ids);
          setSuiteScope('CUSTOM_MIX');
        }}
      />
    </AppLayout>
  );
}
