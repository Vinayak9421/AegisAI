import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const STANDARD_NAMES = [
  'Finred Financial Red-Teaming Benchmark',
  'AdvBench Harmful Behaviors',
  'HarmBench Standard Behaviors',
  'Benign Financial & General Baseline',
];

export default function SuiteSelectionModal({
  isOpen,
  onClose,
  sources = [],
  selectedSuiteIds = [],
  onApply,
}) {
  const [selected, setSelected] = useState([]);

  useEffect(() => {
    if (isOpen) {
      setSelected(selectedSuiteIds || []);
    }
  }, [isOpen, selectedSuiteIds]);

  if (!isOpen) return null;

  const standardSources = sources.filter((s) => {
    const src = s.source || s;
    return STANDARD_NAMES.includes(src.name);
  });

  const customSources = sources.filter((s) => {
    const src = s.source || s;
    return !STANDARD_NAMES.includes(src.name);
  });

  const toggleSuite = (id) => {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const selectAll = () => {
    setSelected(sources.map((s) => (s.source?.id || s.id)));
  };

  const selectAllStandard = () => {
    setSelected(standardSources.map((s) => (s.source?.id || s.id)));
  };

  const clearAll = () => {
    setSelected([]);
  };

  const handleApply = () => {
    onApply(selected);
    onClose();
  };

  // Calculate total vectors in selected suites
  const totalSelectedVectors = sources
    .filter((s) => selected.includes(s.source?.id || s.id))
    .reduce((sum, s) => {
      const src = s.source || s;
      return sum + (s.total_test_cases ?? src.total_test_cases ?? src.total_prompts ?? 0);
    }, 0);

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-xs">
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 10 }}
          transition={{ duration: 0.15 }}
          className="bg-white rounded-2xl max-w-2xl w-full border border-slate-200 shadow-2xl overflow-hidden flex flex-col max-h-[85vh]"
        >
          {/* Header */}
          <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/70">
            <div>
              <h2 className="text-base font-serif font-bold text-slate-900 flex items-center gap-2">
                <span className="material-symbols-outlined text-[#0e61a1] text-xl">tune</span>
                Customize Benchmark Suite Selection
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Pick any combination of standard datasets and uploaded custom suites for this evaluation run.
              </p>
            </div>
            <button
              onClick={onClose}
              className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100 transition-colors"
            >
              <span className="material-symbols-outlined text-lg">close</span>
            </button>
          </div>

          {/* Quick Presets Bar */}
          <div className="px-6 py-2.5 bg-slate-100/60 border-b border-slate-200 flex items-center justify-between gap-2 text-xs">
            <span className="text-slate-500 font-mono text-[11px]">Quick Select:</span>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={selectAllStandard}
                className="px-2.5 py-1 bg-white hover:bg-slate-50 border border-slate-200 rounded text-slate-700 font-medium text-[11px] shadow-2xs transition-colors"
              >
                Standard Only
              </button>
              <button
                type="button"
                onClick={selectAll}
                className="px-2.5 py-1 bg-white hover:bg-slate-50 border border-slate-200 rounded text-slate-700 font-medium text-[11px] shadow-2xs transition-colors"
              >
                Select All
              </button>
              <button
                type="button"
                onClick={clearAll}
                className="px-2.5 py-1 text-slate-500 hover:text-rose-600 font-medium text-[11px] transition-colors"
              >
                Clear All
              </button>
            </div>
          </div>

          {/* Body List */}
          <div className="p-6 overflow-y-auto space-y-5 flex-1 text-xs">
            {/* Standard Datasets */}
            <div>
              <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-2.5 flex items-center gap-1.5">
                <span className="material-symbols-outlined text-sm text-[#0e61a1]">verified</span>
                Standard Regulatory & Safety Benchmarks ({standardSources.length})
              </h3>
              <div className="space-y-2">
                {standardSources.map((item) => {
                  const src = item.source || item;
                  const isChecked = selected.includes(src.id);
                  const count = item.total_test_cases ?? src.total_test_cases ?? src.total_prompts ?? 0;
                  return (
                    <label
                      key={src.id}
                      className={`flex items-start gap-3 p-3 rounded-xl border cursor-pointer transition-all ${
                        isChecked
                          ? 'bg-sky-50/60 border-[#0e61a1] shadow-2xs'
                          : 'bg-white border-slate-200 hover:bg-slate-50/80'
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={isChecked}
                        onChange={() => toggleSuite(src.id)}
                        className="mt-1 rounded border-slate-300 text-[#0e61a1] focus:ring-[#0e61a1]"
                      />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between gap-2">
                          <span className="font-bold text-slate-900 text-xs truncate">
                            {src.name}
                          </span>
                          <span className="px-2 py-0.5 bg-slate-100 text-slate-700 font-mono text-[10px] rounded font-bold shrink-0">
                            {count.toLocaleString()} vectors
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-500 mt-0.5 line-clamp-1">
                          {src.license_text || src.description || 'Standard curated benchmark dataset'}
                        </p>
                      </div>
                    </label>
                  );
                })}
              </div>
            </div>

            {/* Custom Uploaded Datasets */}
            <div>
              <div className="flex items-center justify-between mb-2.5">
                <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-sm text-purple-600">upload_file</span>
                  Custom Uploaded Test Suites ({customSources.length})
                </h3>
              </div>

              {customSources.length === 0 ? (
                <div className="p-4 rounded-xl border border-dashed border-slate-200 text-center text-slate-500 bg-slate-50/50">
                  <p className="text-xs">No custom test suites uploaded yet.</p>
                  <p className="text-[11px] text-slate-400 mt-0.5">
                    You can upload proprietary CSV or JSON suites on the Test Suites page.
                  </p>
                </div>
              ) : (
                <div className="space-y-2">
                  {customSources.map((item) => {
                    const src = item.source || item;
                    const isChecked = selected.includes(src.id);
                    const count = item.total_test_cases ?? src.total_test_cases ?? src.total_prompts ?? 0;
                    return (
                      <label
                        key={src.id}
                        className={`flex items-start gap-3 p-3 rounded-xl border cursor-pointer transition-all ${
                          isChecked
                            ? 'bg-purple-50/60 border-purple-500 shadow-2xs'
                            : 'bg-white border-slate-200 hover:bg-slate-50/80'
                        }`}
                      >
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={() => toggleSuite(src.id)}
                          className="mt-1 rounded border-slate-300 text-purple-600 focus:ring-purple-500"
                        />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between gap-2">
                            <span className="font-bold text-slate-900 text-xs truncate">
                              {src.name}
                            </span>
                            <span className="px-2 py-0.5 bg-purple-100 text-purple-700 font-mono text-[10px] rounded font-bold shrink-0">
                              {count.toLocaleString()} vectors
                            </span>
                          </div>
                          <p className="text-[11px] text-slate-500 mt-0.5 line-clamp-1">
                            {src.license_text || src.description || 'User-uploaded adversarial benchmark'}
                          </p>
                        </div>
                      </label>
                    );
                  })}
                </div>
              )}
            </div>
          </div>

          {/* Footer Bar */}
          <div className="px-6 py-3.5 bg-slate-50 border-t border-slate-200 flex items-center justify-between gap-4">
            <div className="text-xs font-mono text-slate-600">
              <strong className="text-slate-900">{selected.length}</strong> suites selected (
              <strong className="text-[#0e61a1]">{totalSelectedVectors.toLocaleString()}</strong> vectors pool)
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={onClose}
                className="px-3.5 py-2 border border-slate-200 text-slate-700 hover:bg-slate-100 rounded-lg text-xs font-bold transition-colors"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleApply}
                disabled={selected.length === 0}
                className="px-4 py-2 bg-[#0e61a1] hover:bg-[#0b4e82] disabled:opacity-50 text-white rounded-lg text-xs font-bold transition-all shadow-2xs"
              >
                Apply Selection
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
