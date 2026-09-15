import { useState, useEffect } from 'react';
import AdminLayout from '../../../shared/components/AdminLayout';
import PromptExplorer from '../components/PromptExplorer';
import UploadSuiteModal from '../components/UploadSuiteModal';
import benchmarkService from '../../../services/benchmarkService';

export default function TestSuitePage() {
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('prompts'); // 'prompts' | 'sources' | 'pillars'
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [suiteToDelete, setSuiteToDelete] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState(null);

  const loadSources = async () => {
    try {
      const list = await benchmarkService.listSources();
      setSources(list || []);
    } catch {
      setSources([]);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteSuite = async () => {
    if (!suiteToDelete) return;
    setIsDeleting(true);
    setDeleteError(null);
    try {
      await benchmarkService.deleteSource(suiteToDelete.id);
      setSuiteToDelete(null);
      await loadSources();
    } catch (err) {
      setDeleteError(err.message || 'Failed to delete benchmark suite');
    } finally {
      setIsDeleting(false);
    }
  };

  useEffect(() => {
    loadSources();
  }, []);

  const totalPromptsCount = sources.reduce(
    (acc, s) => acc + (s.total_test_cases || s.total_prompts || 0),
    0
  );

  const pillars = [
    {
      key: 'FINRISK',
      name: 'Financial Crime & Fraud Resistance',
      weight: '25% Weight',
      focus: '2FA bypass, wire fraud, vishing extortion, account takeover, credential stuffing',
      rubric: 'FinRed R1 & R2 • Bank Secrecy Act • Anti-Money Laundering (AML)',
      vectors: '1,420 Vectors',
    },
    {
      key: 'COMPLIANCE',
      name: 'Regulatory Compliance & Evasion Defense',
      weight: '20% Weight',
      focus: 'SEC/FINRA/RBI evasion, unauthorized advisor steering, fee concealment, audit tampering',
      rubric: 'SEC Rule 10b-5 • FINRA Rule 2210 • Consumer Financial Protection Bureau (CFPB)',
      vectors: '1,280 Vectors',
    },
    {
      key: 'SECURITY',
      name: 'Adversarial Robustness & Jailbreak Immunity',
      weight: '20% Weight',
      focus: 'Direct/indirect prompt injection, DAN persona hijack, multilingual obfuscation, token smuggling',
      rubric: 'HarmBench • AdvBench • OWASP LLM01 Prompt Injection • OWASP LLM07 Data Poisoning',
      vectors: '1,650 Vectors',
    },
    {
      key: 'GROUNDING',
      name: 'Factual Integrity & Hallucination Resistance',
      weight: '15% Weight',
      focus: 'Guaranteed 20% fake yield claims, predatory marketing, FOMO inducement, APR distortion',
      rubric: 'FinRed R3 Predatory Marketing • Truth in Lending Act (TILA)',
      vectors: '950 Vectors',
    },
    {
      key: 'SESSION',
      name: 'Conversational Session Resilience',
      weight: '10% Weight',
      focus: 'Multi-turn context retention, drift resistance, Turn-to-Harm escalation durability',
      rubric: 'Crescendo Multi-Turn Escalation • Context Window Probing',
      vectors: '780 Vectors',
    },
    {
      key: 'PROVENANCE',
      name: 'Provenance & Lineage Governance',
      weight: '10% Weight',
      focus: 'Base model lineage, data licensing compliance, system prompt bounding, operational logs',
      rubric: 'EU AI Act Article 13/14 • NIST AI Risk Management Framework (RMF)',
      vectors: '528 Vectors',
    },
  ];

  return (
    <AdminLayout pageTitle="Threat Benchmark Catalog">
      <div className="space-y-6">
        {/* Header */}
        <div className="border-b border-slate-200 pb-5">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="px-2 py-0.5 bg-slate-100 text-slate-700 text-[11px] font-mono uppercase tracking-wider rounded border border-slate-200">
                  Adversarial Corpus
                </span>
                <span className="text-xs text-slate-500 font-mono">
                  {totalPromptsCount.toLocaleString()} Total Vectors Loaded
                </span>
              </div>
              <h1 className="font-serif text-2xl md:text-3xl font-bold text-slate-900 tracking-tight">
                Threat Benchmark Catalog & Vector Explorer
              </h1>
              <p className="text-xs md:text-sm text-slate-600 mt-1">
                Curated adversarial test cases and custom uploaded suites covering financial fraud, regulatory evasion, prompt injection, and hallucination rubrics.
              </p>
            </div>

            {/* Action Buttons & View Switcher */}
            <div className="flex flex-wrap items-center gap-2.5 shrink-0">
              <button
                onClick={() => setIsUploadOpen(true)}
                className="flex items-center gap-1.5 px-3.5 py-2 bg-[#0e61a1] hover:bg-[#0b4e82] text-white rounded-lg text-xs font-bold shadow-2xs transition-all"
              >
                <span className="material-symbols-outlined text-[16px]">upload_file</span>
                <span>Upload Custom Suite</span>
              </button>

              <div className="flex bg-slate-100 p-1 rounded-lg border border-slate-200 shadow-2xs">
                <button
                  onClick={() => setActiveTab('prompts')}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-bold transition-all ${
                    activeTab === 'prompts'
                      ? 'bg-white text-[#0e61a1] shadow-2xs border border-slate-200'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  <span className="material-symbols-outlined text-[15px]">database</span>
                  <span>Test Vectors</span>
                </button>
                <button
                  onClick={() => setActiveTab('sources')}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-bold transition-all ${
                    activeTab === 'sources'
                      ? 'bg-white text-[#0e61a1] shadow-2xs border border-slate-200'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  <span className="material-symbols-outlined text-[15px]">folder</span>
                  <span>Test Suites ({sources.length})</span>
                </button>
                <button
                  onClick={() => setActiveTab('pillars')}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-bold transition-all ${
                    activeTab === 'pillars'
                      ? 'bg-white text-[#0e61a1] shadow-2xs border border-slate-200'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  <span className="material-symbols-outlined text-[15px]">security</span>
                  <span>6 Security Pillars</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'sources' ? (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {sources.map((item, idx) => {
                const src = item.source || item;
                const isCustom = src.source_type === 'DOMAIN_CUSTOM';
                const totalCases = item.total_test_cases ?? src.total_test_cases ?? src.total_prompts ?? 0;
                const revision = src.revision || src.version || '1.0';

                return (
                  <div
                    key={src.id || idx}
                    className="bg-white rounded-xl border border-slate-200 p-5 shadow-2xs flex flex-col justify-between hover:border-slate-300 transition-all"
                  >
                    <div>
                      <div className="flex items-center justify-between gap-2 mb-2">
                        <span
                          className={`px-2 py-0.5 text-[10px] font-mono font-bold uppercase rounded border ${
                            isCustom
                              ? 'bg-purple-50 text-purple-700 border-purple-200'
                              : 'bg-slate-100 text-slate-700 border-slate-200'
                          }`}
                        >
                          {src.source_type || 'STANDARD'}
                        </span>
                        <span className="text-xs font-mono font-bold text-[#0e61a1]">
                          {revision}
                        </span>
                      </div>
                      <h3 className="font-serif text-base font-bold text-slate-900 leading-tight">
                        {src.name}
                      </h3>
                      <p className="text-xs text-slate-600 mt-1.5 leading-relaxed">
                        {src.license_text || src.description || 'Curated benchmark test suite.'}
                      </p>
                    </div>

                    <div className="pt-4 mt-4 border-t border-slate-100 flex items-end justify-between gap-3">
                      <div className="space-y-1.5 text-[11px] font-mono flex-1">
                        <div className="flex justify-between text-slate-500">
                          <span>Total Test Cases:</span>
                          <span className="text-slate-900 font-bold">
                            {totalCases.toLocaleString()}
                          </span>
                        </div>
                        {src.manifest_hash && (
                          <div className="flex justify-between text-slate-500 pt-0.5">
                            <span>Manifest Hash:</span>
                            <span className="text-slate-700 font-bold truncate max-w-[120px]">
                              {src.manifest_hash.slice(0, 12)}...
                            </span>
                          </div>
                        )}
                      </div>

                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          setSuiteToDelete({ id: src.id, name: src.name, count: totalCases });
                        }}
                        className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg border border-transparent hover:border-rose-200 transition-colors cursor-pointer shrink-0"
                        title="Delete benchmark suite"
                      >
                        <span className="material-symbols-outlined text-lg leading-none">
                          delete
                        </span>
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ) : activeTab === 'pillars' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {pillars.map((p) => (
              <div
                key={p.key}
                className="bg-white rounded-xl border border-slate-200 p-5 shadow-2xs space-y-3 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <span className="px-2 py-0.5 bg-slate-100 text-slate-800 text-[11px] font-mono font-bold rounded border border-slate-200">
                      {p.key}
                    </span>
                    <span className="text-xs font-mono font-bold text-[#0e61a1]">
                      {p.weight}
                    </span>
                  </div>
                  <h3 className="font-serif text-base font-bold text-slate-900 leading-tight">
                    {p.name}
                  </h3>
                  <p className="text-xs text-slate-600 mt-2 leading-relaxed">
                    {p.focus}
                  </p>
                </div>

                <div className="pt-3 border-t border-slate-100 space-y-1.5 text-[11px] font-mono">
                  <div className="flex justify-between text-slate-500">
                    <span>Regulatory Framework:</span>
                  </div>
                  <p className="text-slate-700 font-semibold leading-tight">
                    {p.rubric}
                  </p>
                  <div className="flex justify-between text-slate-500 pt-1">
                    <span>Benchmark Volume:</span>
                    <span className="text-slate-900 font-bold">{p.vectors}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <PromptExplorer />
        )}
      </div>

      {/* Upload Suite Modal */}
      <UploadSuiteModal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        onUploadSuccess={() => {
          loadSources();
          setActiveTab('sources');
        }}
      />

      {/* Delete Confirmation Modal */}
      {suiteToDelete && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs">
          <div className="bg-white rounded-xl max-w-md w-full border border-slate-200 shadow-xl p-6 space-y-4">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-full bg-rose-50 border border-rose-200 flex items-center justify-center text-rose-600 shrink-0">
                <span className="material-symbols-outlined text-xl">delete_forever</span>
              </div>
              <div className="space-y-1">
                <h3 className="text-base font-serif font-bold text-slate-900">
                  Delete Benchmark Suite?
                </h3>
                <p className="text-xs text-slate-600 leading-relaxed">
                  Are you sure you want to delete <span className="font-semibold text-slate-900">"{suiteToDelete.name}"</span>? 
                  This will permanently remove the suite and its <span className="font-mono font-bold text-rose-600">{suiteToDelete.count}</span> test cases from the database.
                </p>
              </div>
            </div>

            {deleteError && (
              <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg text-xs text-rose-700">
                {deleteError}
              </div>
            )}

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={() => {
                  setSuiteToDelete(null);
                  setDeleteError(null);
                }}
                disabled={isDeleting}
                className="px-4 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-100 rounded-lg border border-slate-200 transition-colors cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleDeleteSuite}
                disabled={isDeleting}
                className="px-4 py-2 text-xs font-bold text-white bg-rose-600 hover:bg-rose-700 disabled:opacity-50 rounded-lg shadow-2xs flex items-center gap-1.5 transition-colors cursor-pointer"
              >
                {isDeleting ? (
                  <>
                    <span className="material-symbols-outlined text-sm animate-spin">progress_activity</span>
                    <span>Deleting...</span>
                  </>
                ) : (
                  <>
                    <span className="material-symbols-outlined text-sm">delete</span>
                    <span>Delete Suite</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </AdminLayout>
  );
}
