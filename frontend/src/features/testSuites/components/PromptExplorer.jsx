import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import benchmarkService from '../../../services/benchmarkService';
import toast from 'react-hot-toast';

const CATEGORIES = [
  { value: '', label: 'All Categories' },
  { value: 'CYBERSECURITY_AUTH', label: 'Cybersecurity & Auth (R1)' },
  { value: 'FRAUD_FACILITATION', label: 'Fraud Facilitation (R2)' },
  { value: 'MARKET_MANIPULATION', label: 'Market Manipulation (R3)' },
  { value: 'CONSUMER_HARM', label: 'Consumer Harm (R4)' },
  { value: 'REGULATORY_EVASION', label: 'Regulatory Evasion (R5)' },
  { value: 'JAILBREAK_GUARDRAILS', label: 'Jailbreak Guardrails' },
];

const SEVERITIES = [
  { value: '', label: 'All Severities' },
  { value: 'CRITICAL', label: 'Critical' },
  { value: 'HIGH', label: 'High' },
  { value: 'MEDIUM', label: 'Medium' },
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
    toast.success('Prompt copied to clipboard!');
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm overflow-hidden flex flex-col">
      {/* Header with DB Status & Controls */}
      <div className="p-5 border-b border-slate-200 bg-slate-50/60">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 mb-4">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <span className="material-symbols-outlined text-[#0e61a1]">database</span>
                Live Database Attack Prompts (test_cases table)
              </h3>
              <span className="inline-flex items-center gap-1 text-[11px] font-bold text-sky-800 bg-sky-50 border border-sky-200 px-2.5 py-0.5 rounded-full">
                <span className="w-1.5 h-1.5 rounded-full bg-[#0e61a1] animate-pulse" />
                {totalCount.toLocaleString()} Prompts in DB
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Real adversarial test cases loaded live from PostgreSQL via <code className="text-slate-700 bg-slate-100 px-1 py-0.5 rounded font-mono text-[11px]">GET /api/v1/benchmarks/test-cases</code>
            </p>
          </div>

          {/* Quick Refresh */}
          <button
            onClick={() => setOffset((prev) => prev)}
            className="self-start md:self-auto px-3 py-1.5 bg-white border border-slate-200 hover:bg-slate-50 rounded-xl text-xs font-semibold text-slate-700 shadow-2xs flex items-center gap-1.5 transition-all"
          >
            <span className={`material-symbols-outlined text-sm ${loading ? 'animate-spin' : ''}`}>
              refresh
            </span>
            <span>Refresh DB</span>
          </button>
        </div>

        {/* Filter Toolbar */}
        <div className="grid grid-cols-1 sm:grid-cols-12 gap-3 pt-2">
          {/* Keyword Search */}
          <form onSubmit={handleSearchSubmit} className="sm:col-span-5 relative">
            <input
              type="text"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              placeholder="Search prompt keywords (e.g. 2FA, wire fraud, SEC)..."
              className="w-full bg-white border border-slate-200 rounded-xl pl-9 pr-16 py-2 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:border-[#0e61a1] shadow-2xs transition-colors"
            />
            <span className="material-symbols-outlined absolute left-3 top-2.5 text-slate-400 text-base">
              search
            </span>
            <button
              type="submit"
              className="absolute right-1.5 top-1 px-2.5 py-1 bg-[#0e61a1] hover:bg-[#0b4e82] text-white text-[11px] font-semibold rounded-lg shadow-2xs"
            >
              Filter
            </button>
          </form>

          {/* Category Dropdown */}
          <div className="sm:col-span-4 relative">
            <select
              value={category}
              onChange={(e) => handleCategoryChange(e.target.value)}
              className="w-full bg-white border border-slate-200 rounded-xl px-3 py-2 text-xs font-medium text-slate-800 focus:outline-none focus:border-[#0e61a1] appearance-none shadow-2xs"
            >
              {CATEGORIES.map((c) => (
                <option key={c.value} value={c.value}>
                  {c.label}
                </option>
              ))}
            </select>
            <span className="material-symbols-outlined absolute right-3 top-2.5 text-slate-400 pointer-events-none text-base">
              expand_more
            </span>
          </div>

          {/* Severity Dropdown */}
          <div className="sm:col-span-3 relative">
            <select
              value={severity}
              onChange={(e) => handleSeverityChange(e.target.value)}
              className="w-full bg-white border border-slate-200 rounded-xl px-3 py-2 text-xs font-medium text-slate-800 focus:outline-none focus:border-[#0e61a1] appearance-none shadow-2xs"
            >
              {SEVERITIES.map((s) => (
                <option key={s.value} value={s.value}>
                  {s.label}
                </option>
              ))}
            </select>
            <span className="material-symbols-outlined absolute right-3 top-2.5 text-slate-400 pointer-events-none text-base">
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
            <p className="text-xs font-medium">Fetching prompts from PostgreSQL database...</p>
          </div>
        ) : testCases.length === 0 ? (
          <div className="p-12 text-center text-slate-400">
            <span className="material-symbols-outlined text-3xl mb-2 text-slate-300">search_off</span>
            <p className="text-sm font-semibold text-slate-700">No attack prompts found</p>
            <p className="text-xs text-slate-400 mt-1">Try relaxing your search terms or filters</p>
          </div>
        ) : (
          testCases.map((tc, idx) => {
            const isExpanded = expandedId === tc.id;
            const isCritical = tc.severity === 'CRITICAL';
            const isHigh = tc.severity === 'HIGH';

            return (
              <div
                key={tc.id}
                className="p-4 hover:bg-slate-50/70 transition-colors flex flex-col gap-2.5"
              >
                {/* Meta Header */}
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-[11px] font-mono text-slate-400 font-bold">
                      #{offset + idx + 1}
                    </span>
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-slate-100 text-slate-700 border border-slate-200">
                      {tc.category}
                    </span>
                    {tc.subcategory && (
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-medium bg-sky-50 text-sky-800 border border-sky-200">
                        {tc.subcategory}
                      </span>
                    )}
                    <span
                      className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${
                        isCritical
                          ? 'bg-rose-50 text-rose-700 border-rose-200'
                          : isHigh
                          ? 'bg-amber-50 text-amber-700 border-amber-200'
                          : 'bg-emerald-50 text-emerald-700 border-emerald-200'
                      }`}
                    >
                      {tc.severity}
                    </span>
                  </div>

                  <div className="flex items-center gap-1.5">
                    {tc.owasp_category_ids &&
                      tc.owasp_category_ids.slice(0, 2).map((owasp) => (
                        <span
                          key={owasp}
                          className="px-1.5 py-0.5 rounded text-[10px] font-mono bg-purple-50 text-purple-700 border border-purple-200"
                        >
                          {owasp.split(':')[0]}
                        </span>
                      ))}

                    <button
                      onClick={() => copyToClipboard(tc.prompt_template)}
                      title="Copy Prompt"
                      className="p-1 rounded-lg hover:bg-slate-200 text-slate-400 hover:text-slate-700 transition-colors"
                    >
                      <span className="material-symbols-outlined text-base">content_copy</span>
                    </button>
                  </div>
                </div>

                {/* Prompt Template Text */}
                <div
                  onClick={() => setExpandedId(isExpanded ? null : tc.id)}
                  className="cursor-pointer group"
                >
                  <p
                    className={`text-xs text-slate-800 font-mono bg-slate-50/80 group-hover:bg-slate-100/80 p-3 rounded-xl border border-slate-200/80 leading-relaxed transition-colors ${
                      isExpanded ? 'whitespace-pre-wrap' : 'line-clamp-2'
                    }`}
                  >
                    {tc.prompt_template}
                  </p>
                  <div className="flex justify-end mt-1">
                    <span className="text-[11px] font-semibold text-[#0e61a1] hover:underline">
                      {isExpanded ? '▲ Collapse' : '▼ Read Full Prompt'}
                    </span>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Pagination Bar */}
      <div className="p-4 border-t border-slate-200 bg-slate-50/60 flex flex-col sm:flex-row justify-between items-center gap-3 text-xs text-slate-600">
        <div>
          Showing <strong>{Math.min(offset + 1, totalCount)}</strong> to{' '}
          <strong>{Math.min(offset + limit, totalCount)}</strong> of{' '}
          <strong>{totalCount.toLocaleString()}</strong> attack prompts
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setOffset((prev) => Math.max(0, prev - limit))}
            disabled={offset === 0 || loading}
            className="px-3 py-1.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed font-semibold text-slate-700 shadow-2xs transition-all flex items-center gap-1"
          >
            <span className="material-symbols-outlined text-base">chevron_left</span>
            <span>Previous</span>
          </button>

          <span className="px-2 font-mono font-medium text-slate-700">
            Page {currentPage} of {totalPages}
          </span>

          <button
            onClick={() => setOffset((prev) => prev + limit)}
            disabled={offset + limit >= totalCount || loading}
            className="px-3 py-1.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed font-semibold text-slate-700 shadow-2xs transition-all flex items-center gap-1"
          >
            <span>Next</span>
            <span className="material-symbols-outlined text-base">chevron_right</span>
          </button>
        </div>
      </div>
    </div>
  );
}
