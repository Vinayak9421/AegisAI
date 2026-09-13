import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import AdminLayout from '../../../shared/components/AdminLayout';
import TestSuiteCard from '../components/TestSuiteCard';
import PromptExplorer from '../components/PromptExplorer';
import benchmarkService from '../../../services/benchmarkService';

const toggleItems = [
  { id: 'single', label: 'Single-turn Evaluation', detail: 'Target prompt-response security testing.', defaultOn: true },
  { id: 'multi', label: 'Multi-turn Conversation', detail: 'Context retention and jailbreak drift.', defaultOn: true },
  { id: 'agentic', label: 'Deterministic Seed (42)', detail: 'Reproducible stratified benchmark sampling.', defaultOn: true },
];

function Toggle({ item }) {
  const [on, setOn] = useState(item.defaultOn);
  return (
    <div className="flex items-center justify-between p-3 rounded-xl hover:bg-slate-50 transition-colors">
      <div>
        <p className="text-xs font-semibold text-slate-800">{item.label}</p>
        <p className="text-[11px] text-slate-500 mt-0.5">{item.detail}</p>
      </div>
      <button
        onClick={() => setOn(!on)}
        className={`relative w-11 h-6 rounded-full transition-colors duration-200 ${on ? 'bg-[#0e61a1]' : 'bg-slate-300'}`}
      >
        <motion.span
          animate={{ x: on ? 20 : 2 }}
          transition={{ duration: 0.2 }}
          className="absolute top-1 left-0.5 w-4 h-4 bg-white rounded-full shadow-xs"
        />
      </button>
    </div>
  );
}

export default function TestSuitePage() {
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('prompts'); // 'prompts' | 'datasets'

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

  const totalPromptsCount = sources.reduce((acc, s) => acc + (s.total_test_cases || s.total_prompts || 0), 0);

  const displayPools = sources.map((s, i) => {
    const src = s.source || s;
    const count = s.total_test_cases || s.total_prompts || 0;
    return {
      id: src.id || i,
      name: src.name,
      badge: src.revision || src.version || 'v1.0',
      badgeVariant: src.source_type === 'EXTERNAL' ? 'standard' : 'ethics',
      description: src.description || 'Pre-configured financial security & evasion attack suites.',
      stats: [
        { icon: 'format_list_numbered', text: `${count.toLocaleString()} Prompts` },
        { icon: 'shield', text: src.source_type || 'FINTECH' },
        { icon: 'verified', text: 'Seeded in PostgreSQL', color: '#0e61a1' },
      ],
    };
  });

  return (
    <AdminLayout pageTitle="Benchmark Threat Catalog">
      <div className="space-y-6">
        {/* Header & Tabs */}
        <motion.div
          initial={{ opacity: 0, y: -16 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col md:flex-row md:items-end justify-between gap-4"
        >
          <div>
            <h1 className="text-2xl md:text-3xl font-bold text-slate-900 tracking-tight">
              Threat Benchmark Catalog & Prompts
            </h1>
            <p className="text-sm text-slate-500 mt-1">
              Ingested adversarial corpora categorized across 5 banking threat vectors and stored in PostgreSQL.
            </p>
          </div>

          {/* View Mode Toggle */}
          <div className="flex bg-slate-200/70 p-1 rounded-xl border border-slate-300/60 shadow-2xs">
            <button
              onClick={() => setActiveTab('prompts')}
              className={`flex items-center gap-1.5 px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${
                activeTab === 'prompts'
                  ? 'bg-white text-[#0e61a1] shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <span className="material-symbols-outlined text-base">database</span>
              <span>Database Prompts ({totalPromptsCount.toLocaleString()})</span>
            </button>
            <button
              onClick={() => setActiveTab('datasets')}
              className={`flex items-center gap-1.5 px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${
                activeTab === 'datasets'
                  ? 'bg-white text-[#0e61a1] shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <span className="material-symbols-outlined text-base">library_books</span>
              <span>Dataset Sources & Config</span>
            </button>
          </div>
        </motion.div>

        {/* Tab 1: Live DB Prompt Explorer */}
        {activeTab === 'prompts' && (
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <PromptExplorer />
          </motion.div>
        )}

        {/* Tab 2: Datasets & Config View */}
        {activeTab === 'datasets' && (
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="grid grid-cols-1 lg:grid-cols-12 gap-6"
          >
            {/* Left: Benchmark Pools */}
            <div className="lg:col-span-8 flex flex-col gap-4">
              <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <span className="material-symbols-outlined text-[#0e61a1]">library_books</span>
                Active Benchmark Datasets ({displayPools.length})
              </h2>
              {displayPools.length === 0 ? (
                <div className="p-8 text-center bg-white rounded-2xl border border-slate-200 text-slate-400">
                  <span className="material-symbols-outlined text-4xl text-slate-300 mb-2">folder_off</span>
                  <p className="text-sm font-semibold text-slate-600">No benchmark sources found</p>
                  <p className="text-xs text-slate-400 mt-1">
                    Execute benchmark database seeding to populate threat catalogs.
                  </p>
                </div>
              ) : (
                displayPools.map((pool, i) => (
                  <TestSuiteCard key={pool.id} pool={pool} index={i} />
                ))
              )}
            </div>

            {/* Right: Config Panel */}
            <div className="lg:col-span-4 flex flex-col gap-6">
              {/* Judge Configuration */}
              <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm">
                <h3 className="text-sm md:text-base font-bold text-slate-900 flex items-center gap-2 mb-4">
                  <span className="material-symbols-outlined text-[#0e61a1]">gavel</span>
                  Independent Judge Config
                </h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                      Primary Judge Model
                    </label>
                    <div className="relative">
                      <select className="w-full bg-slate-50 border border-slate-200 rounded-xl py-2.5 px-3 text-slate-800 text-xs font-medium focus:bg-white focus:border-[#0e61a1] outline-none appearance-none">
                        <option>Groq / Llama Guard 3 8B (Adversarial Delimiters)</option>
                        <option>Groq / Llama-3.3-70B-Versatile (Active)</option>
                        <option>Rule-based Heuristic Judge (Offline Fallback)</option>
                      </select>
                      <span className="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none text-lg">
                        expand_more
                      </span>
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1.5">
                      Evaluation Sampling Mode
                    </label>
                    <div className="relative">
                      <select className="w-full bg-slate-50 border border-slate-200 rounded-xl py-2.5 px-3 text-slate-800 text-xs font-medium focus:bg-white focus:border-[#0e61a1] outline-none appearance-none">
                        <option>Quick Mode (~25 Stratified Prompts)</option>
                        <option>Full Audit (150–200 Balanced Prompts)</option>
                      </select>
                      <span className="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none text-lg">
                        expand_more
                      </span>
                    </div>
                  </div>

                  <div className="pt-3 border-t border-slate-100">
                    <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2 flex justify-between">
                      <span>Target Rate Limit</span>
                      <span className="text-[#0e61a1] font-bold">60 RPM</span>
                    </label>
                    <input
                      type="range"
                      min="10"
                      max="300"
                      defaultValue="60"
                      className="w-full accent-[#0e61a1] cursor-pointer"
                    />
                  </div>
                </div>
              </div>

              {/* Test Modalities */}
              <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm">
                <h3 className="text-sm md:text-base font-bold text-slate-900 flex items-center gap-2 mb-3">
                  <span className="material-symbols-outlined text-[#0e61a1]">tune</span>
                  Test Parameters
                </h3>
                <div className="space-y-1">
                  {toggleItems.map((item) => (
                    <Toggle key={item.id} item={item} />
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </AdminLayout>
  );
}
