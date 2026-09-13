import { useState, useEffect } from 'react';
import AdminLayout from '../../../shared/components/AdminLayout';
import PromptExplorer from '../components/PromptExplorer';
import benchmarkService from '../../../services/benchmarkService';

export default function TestSuitePage() {
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('prompts'); // 'prompts' | 'pillars'

  useEffect(() => {
    async function loadSources() {
      try {
        const list = await benchmarkService.listSources();
        setSources(list || []);
      } catch {
        setSources([]);
      } finally {
        setLoading(false);
      }
    }
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
                  Seeded in PostgreSQL 18
                </span>
              </div>
              <h1 className="font-serif text-2xl md:text-3xl font-bold text-slate-900 tracking-tight">
                Threat Benchmark Catalog & Vector Explorer
              </h1>
              <p className="text-xs md:text-sm text-slate-600 mt-1">
                Curated adversarial test cases covering financial fraud, regulatory evasion, prompt injection, and hallucination rubrics.
              </p>
            </div>

            {/* View Mode Switcher */}
            <div className="flex bg-slate-100 p-1 rounded-lg border border-slate-200 shadow-2xs shrink-0">
              <button
                onClick={() => setActiveTab('prompts')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-bold transition-all ${
                  activeTab === 'prompts'
                    ? 'bg-white text-[#0e61a1] shadow-2xs border border-slate-200'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <span className="material-symbols-outlined text-[15px]">database</span>
                <span>Test Vector Explorer</span>
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

        {/* Tab Content */}
        {activeTab === 'pillars' ? (
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
    </AdminLayout>
  );
}
