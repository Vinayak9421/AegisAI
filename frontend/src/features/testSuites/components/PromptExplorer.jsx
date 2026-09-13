import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import benchmarkService from '../../../services/benchmarkService';
import toast from 'react-hot-toast';

const CATEGORIES = [
  { value: '', label: 'All Threat Pillars & Categories' },
  { value: 'CYBERSECURITY_AUTH', label: 'Cybersecurity & Auth Exploitation (R1)' },
  { value: 'FRAUD_FACILITATION', label: 'Fraud Facilitation & Social Engineering (R2)' },
  { value: 'MARKET_MANIPULATION', label: 'Market Manipulation & Predatory Steering (R3)' },
  { value: 'CONSUMER_HARM', label: 'Consumer Harm & Vulnerable Exploitation (R4)' },
  { value: 'REGULATORY_EVASION', label: 'Regulatory Evasion & Compliance Bypass (R5)' },
  { value: 'JAILBREAK_GUARDRAILS', label: 'Adversarial Jailbreaks & Injections' },
];

const SEVERITIES = [
  { value: '', label: 'All Severity Levels' },
  { value: 'CRITICAL', label: 'Critical Severity (3.0x Weight)' },
  { value: 'HIGH', label: 'High Severity (2.0x Weight)' },
  { value: 'MEDIUM', label: 'Medium Severity (1.0x Weight)' },
];

export default function PromptExplorer() {
  const [testCases, setTestCases] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);

  // Filters
  const [category, setCategory] = useState('');
  const [severity, setSeverity] = useState('');
  const [search, setSearch] = useState('');
  const [searchInput, setSearchInput] = useState('');
  const [offset, setOffset] = useState(0);
  const limit = 20;

  // Selected prompt modal or expansion
  const [expandedId, setExpandedId] = useState(null);

  useEffect(() => {
    async function fetchPrompts() {
      setLoading(true);
      try {
        const res = await benchmarkService.listTestCases({
          category: category || undefined,
          severity: severity || undefined,
          search: search || undefined,
          limit,
          offset,
        });
        setTestCases(res.items || []);
        setTotalCount(res.total || 0);
      } catch (err) {
        toast.error('Could not load prompts from database: ' + err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchPrompts();
  }, [category, severity, search, offset]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setOffset(0);
    setSearch(searchInput.trim());
  };

  const handleCategoryChange = (val) => {
    setCategory(val);
    setOffset(0);
  };

  const handleSeverityChange = (val) => {
    setSeverity(val);
    setOffset(0);
  };

  const totalPages = Math.ceil(totalCount / limit) || 1;
  const currentPage = Math.floor(offset / limit) + 1;

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Prompt copied to clipboard');
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-2xs overflow-hidden flex flex-col">
      {/* Header with DB Status & Controls */}
      <div className="p-4 border-b border-slate-200 bg-slate-50/70">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 mb-3">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                <span className="material-symbols-outlined text-[#0e61a1] text-base">database</span>
                Live Database Attack Vectors (PostgreSQL test_cases)
              </h3>
              <span className="inline-flex items-center gap-1 text-[11px] font-mono font-bold text-slate-700 bg-white border border-slate-200 px-2 py-0.5 rounded shadow-2xs">
                {totalCount.toLocaleString()} Vectors Seeded
              </span>
            </div>
            <p className="text-[11px] text-slate-500 font-mono mt-0.5">
              Protocol: <code className="text-slate-700 font-bold">GET /api/v1/benchmarks/test-cases</code>
            </p>
          </div>

          {/* Refresh */}
          <button
            onClick={() => setOffset((prev) => prev)}
            className="self-start md:self-auto px-2.5 py-1 bg-white border border-slate-200 hover:bg-slate-50 rounded text-xs font-semibold text-slate-700 shadow-2xs flex items-center gap-1.5 transition-all"
          >
            <span className={`material-symbols-outlined text-sm ${loading ? 'animate-spin' : ''}`}>
              refresh
            </span>
            <span>Refresh</span>
          </button>
        </div>

        {/* Filter Toolbar */}
        <div className="grid grid-cols-1 sm:grid-cols-12 gap-2.5 pt-1">
          {/* Keyword Search */}
          <form onSubmit={handleSearchSubmit} className="sm:col-span-5 relative">
            <input
              type="text"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              placeholder="Filter prompt content (e.g. 2FA, wire fraud, SEC)..."
              className="w-full bg-white border border-slate-200 rounded-lg pl-8 pr-16 py-1.5 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-[#0e61a1] transition-colors"
            />
            <span className="material-symbols-outlined absolute left-2.5 top-2 text-slate-400 text-sm">
              search
            </span>
            <button
              type="submit"
              className="absolute right-1 top-1 px-2.5 py-0.5 bg-[#0e61a1] hover:bg-[#0b4e82] text-white text-[11px] font-bold rounded shadow-2xs"
            >
              Filter
            </button>
          </form>

          {/* Category Dropdown */}
          <div className="sm:col-span-4 relative">
            <select
              value={category}
              onChange={(e) => handleCategoryChange(e.target.value)}
              className="w-full bg-white border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs font-medium text-slate-800 focus:outline-none focus:border-[#0e61a1] appearance-none"
            >
              {CATEGORIES.map((c) => (
                <option key={c.value} value={c.value}>
                  {c.label}
                </option>
              ))}
            </select>
            <span className="material-symbols-outlined absolute right-2.5 top-2 text-slate-400 pointer-events-none text-base">
              expand_more
            </span>
          </div>

          {/* Severity Dropdown */}
          <div className="sm:col-span-3 relative">
            <select
              value={severity}
              onChange={(e) => handleSeverityChange(e.target.value)}
              className="w-full bg-white border border-slate-200 rounded-lg px-2.5 py-1.5 text-xs font-medium text-slate-800 focus:outline-none focus:border-[#0e61a1] appearance-none"
            >
              {SEVERITIES.map((s) => (
                <option key={s.value} value={s.value}>
                  {s.label}
                </option>
              ))}
            </select>
            <span className="material-symbols-outlined absolute right-2.5 top-2 text-slate-400 pointer-events-none text-base">
              expand_more
            </span>
          </div>
        </div>
      </div>

      {/* Prompts List */}
      <div className="divide-y divide-slate-100 max-h-[650px] overflow-y-auto">
        {loading ? (
          <div className="p-12 text-center text-slate-400 flex flex-col items-center gap-2">
            <span className="material-symbols-outlined animate-spin text-3xl text-[#0e61a1]">
              sync
            </span>
            <p className="text-xs font-medium">Fetching benchmark vectors from PostgreSQL...</p>
          </div>
        ) : testCases.length === 0 ? (
          <div className="p-12 text-center text-slate-400">
            <span className="material-symbols-outlined text-3xl mb-2 text-slate-300">search_off</span>
            <p className="text-xs font-bold text-slate-700">No attack vectors match criteria</p>
            <p className="text-[11px] text-slate-400 mt-0.5">Adjust keyword search or category filters</p>
          </div>
        ) : (
          testCases.map((tc, idx) => {
            const isExpanded = expandedId === tc.id;
            const isCritical = tc.severity === 'CRITICAL';
            const isHigh = tc.severity === 'HIGH';

            return (
              <div
                key={tc.id}
                className={`p-4 transition-colors ${
                  isExpanded ? 'bg-slate-50/80' : 'hover:bg-slate-50/50'
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-[10px] font-mono font-bold text-slate-400 bg-slate-100 px-1.5 py-0.5 rounded border border-slate-200">
                      #{offset + idx + 1}
                    </span>
                    <span className="text-[11px] font-mono font-bold text-slate-800">
                      {tc.category || 'FINRISK'}
                    </span>
                    {tc.subcategory && (
                      <span className="text-[11px] text-slate-500 font-mono">
                        / {tc.subcategory}
                      </span>
                    )}
                  </div>

                  <div className="flex items-center gap-2">
                    <span
                      className={`px-2 py-0.5 text-[10px] font-mono font-bold uppercase rounded border ${
                        isCritical
                          ? 'bg-rose-50 text-rose-800 border-rose-300'
                          : isHigh
                          ? 'bg-amber-50 text-amber-800 border-amber-300'
                          : 'bg-slate-50 text-slate-700 border-slate-300'
                      }`}
                    >
                      {tc.severity || 'MEDIUM'}
                    </span>
                    <button
                      onClick={() => setExpandedId(isExpanded ? null : tc.id)}
                      className="text-xs font-semibold text-[#0e61a1] hover:underline flex items-center gap-0.5"
                    >
                      <span>{isExpanded ? 'Collapse' : 'Inspect'}</span>
                      <span className="material-symbols-outlined text-sm">
                        {isExpanded ? 'expand_less' : 'expand_more'}
                      </span>
                    </button>
                  </div>
                </div>

                {/* Prompt Preview */}
                <div className="text-xs font-mono text-slate-700 line-clamp-2 bg-slate-50 p-2.5 rounded border border-slate-200/80 leading-relaxed select-text">
                  {tc.prompt_template}
                </div>

                {/* Expanded Details */}
                <AnimatePresence>
                  {isExpanded && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      className="mt-3 pt-3 border-t border-slate-200 space-y-3"
                    >
                      <div>
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-[10px] font-mono font-bold text-slate-500 uppercase tracking-wider">
                            Full Adversarial Prompt Template
                          </span>
                          <button
                            onClick={() => copyToClipboard(tc.prompt_template)}
                            className="text-[11px] font-bold text-[#0e61a1] hover:text-[#0b4e82] flex items-center gap-1"
                          >
                            <span className="material-symbols-outlined text-xs">content_copy</span>
                            Copy Prompt
                          </button>
                        </div>
                        <pre className="p-3 bg-slate-900 text-slate-100 text-xs font-mono rounded-lg overflow-x-auto whitespace-pre-wrap select-text leading-relaxed">
                          {tc.prompt_template}
                        </pre>
                      </div>

                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-[11px] font-mono bg-white p-2.5 rounded border border-slate-200">
                        <div>
                          <span className="text-slate-400 block text-[10px]">Test Case UUID:</span>
                          <span className="text-slate-800 truncate block">{tc.id}</span>
                        </div>
                        <div>
                          <span className="text-slate-400 block text-[10px]">Source Pool:</span>
                          <span className="text-slate-800">{tc.source || 'FinRed Financial Safety'}</span>
                        </div>
                        <div>
                          <span className="text-slate-400 block text-[10px]">Evaluation Rubric:</span>
                          <span className="text-slate-800">{tc.rubric_version || 'financial_safety_v1.0'}</span>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            );
          })
        )}
      </div>

      {/* Pagination Footer */}
      <div className="p-3.5 border-t border-slate-200 bg-slate-50/70 flex justify-between items-center text-xs font-mono text-slate-500">
        <span>
          Page {currentPage} of {totalPages} ({totalCount} total vectors)
        </span>
        <div className="flex gap-1">
          <button
            onClick={() => setOffset(Math.max(0, offset - limit))}
            disabled={offset === 0}
            className="px-2.5 py-1 bg-white border border-slate-200 rounded text-xs font-semibold disabled:opacity-40 hover:bg-slate-50"
          >
            Previous
          </button>
          <button
            onClick={() => setOffset(offset + limit)}
            disabled={offset + limit >= totalCount}
            className="px-2.5 py-1 bg-white border border-slate-200 rounded text-xs font-semibold disabled:opacity-40 hover:bg-slate-50"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}
