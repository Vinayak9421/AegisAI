import { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import benchmarkService from '../../../services/benchmarkService';
import toast from 'react-hot-toast';

const CATEGORY_OPTIONS = [
  { value: 'FINANCIAL_FRAUD', label: 'Financial Crime & Fraud Resistance (FINRISK)' },
  { value: 'COMPLIANCE', label: 'Regulatory Compliance & Evasion (COMPLIANCE)' },
  { value: 'SECURITY', label: 'Adversarial Robustness & Jailbreaks (SECURITY)' },
  { value: 'MARKET_MANIPULATION', label: 'Market Manipulation & Spoofing' },
  { value: 'CYBERSECURITY_AUTH', label: 'Cybersecurity & Auth Exploitation' },
  { value: 'CONSUMER_HARM', label: 'Consumer Harm & Predatory Steering' },
  { value: 'GROUNDING', label: 'Factual Integrity & Hallucination Resistance' },
  { value: 'SESSION', label: 'Conversational Session Resilience' },
];

export default function UploadSuiteModal({ isOpen, onClose, onUploadSuccess }) {
  const fileInputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [suiteName, setSuiteName] = useState('');
  const [description, setDescription] = useState('');
  const [fallbackCategory, setFallbackCategory] = useState('FINANCIAL_FRAUD');
  const [previewRows, setPreviewRows] = useState([]);
  const [isParsing, setIsParsing] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);

  if (!isOpen) return null;

  const handleFileChange = (selectedFile) => {
    if (!selectedFile) return;
    const lowerName = selectedFile.name.toLowerCase();
    if (!lowerName.endsWith('.csv') && !lowerName.endsWith('.json')) {
      toast.error('Please upload a .csv or .json file.');
      return;
    }

    setFile(selectedFile);
    if (!suiteName) {
      const cleanName = selectedFile.name.replace(/\.[^/.]+$/, '').replace(/[_-]/g, ' ');
      setSuiteName(cleanName.charAt(0).toUpperCase() + cleanName.slice(1));
    }

    // Parse preview rows
    parseFilePreview(selectedFile);
  };

  const parseFilePreview = (fileToParse) => {
    setIsParsing(true);
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const text = e.target.result;
        const lowerName = fileToParse.name.toLowerCase();

        if (lowerName.endsWith('.json')) {
          const parsed = JSON.parse(text);
          const rawCases = Array.isArray(parsed)
            ? parsed
            : parsed.test_cases || parsed.cases || parsed.prompts || [parsed];
          const slice = rawCases.slice(0, 5).map((item, idx) => ({
            id: idx + 1,
            prompt: item.prompt || item.prompt_template || item.attack_prompt || item.text || '(empty)',
            category: item.category || item.pillar || fallbackCategory,
            severity: item.severity || item.severity_ceiling || 'HIGH',
            mode: item.mode || (item.session_script || item.turns ? 'SESSION' : 'SINGLE'),
          }));
          setPreviewRows(slice);
        } else {
          // CSV preview
          const lines = text.split(/\r\n|\n/).filter((l) => l.trim().length > 0);
          if (lines.length > 1) {
            const headers = lines[0].split(',').map((h) => h.replace(/["']/g, '').trim().toLowerCase());
            const promptIdx = headers.findIndex((h) => ['prompt', 'prompt_template', 'text', 'attack_prompt'].includes(h));
            const catIdx = headers.findIndex((h) => ['category', 'threat_category', 'pillar'].includes(h));
            const sevIdx = headers.findIndex((h) => ['severity', 'severity_ceiling'].includes(h));
            const modeIdx = headers.findIndex((h) => ['mode'].includes(h));

            const slice = lines.slice(1, 6).map((line, idx) => {
              // Basic CSV line parse
              const parts = line.split(/,(?=(?:(?:[^"]*"){2})*[^"]*$)/).map((s) => s.replace(/^"|"$/g, '').trim());
              return {
                id: idx + 1,
                prompt: promptIdx >= 0 && parts[promptIdx] ? parts[promptIdx] : parts[0] || '(empty)',
                category: catIdx >= 0 && parts[catIdx] ? parts[catIdx] : fallbackCategory,
                severity: sevIdx >= 0 && parts[sevIdx] ? parts[sevIdx] : 'HIGH',
                mode: modeIdx >= 0 && parts[modeIdx] ? parts[modeIdx] : 'SINGLE',
              };
            });
            setPreviewRows(slice);
          } else {
            setPreviewRows([]);
          }
        }
      } catch (err) {
        console.warn('Preview parsing error:', err);
        setPreviewRows([]);
      } finally {
        setIsParsing(false);
      }
    };
    reader.onerror = () => setIsParsing(false);
    reader.readAsText(fileToParse);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  const handleDownloadTemplate = async (format) => {
    try {
      await benchmarkService.downloadTemplate(format);
      toast.success(`Sample ${format.toUpperCase()} template downloaded`);
    } catch (err) {
      toast.error('Failed to download template: ' + err.message);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      toast.error('Please select a CSV or JSON file to upload.');
      return;
    }
    if (!suiteName.trim()) {
      toast.error('Please enter a suite name.');
      return;
    }

    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('name', suiteName.trim());
      if (description.trim()) {
        formData.append('description', description.trim());
      }
      formData.append('fallback_category', fallbackCategory);

      const res = await benchmarkService.uploadTestSuite(formData);
      toast.success(
        `Test suite "${suiteName}" uploaded! Ingested ${res.ingested_count ?? res.inserted_count ?? 0} vectors (${res.duplicate_count ?? res.skipped_duplicates ?? 0} duplicates skipped).`
      );
      if (onUploadSuccess) onUploadSuccess(res);
      handleReset();
      onClose();
    } catch (err) {
      toast.error(err.message || 'Upload failed. Check format and try again.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setSuiteName('');
    setDescription('');
    setFallbackCategory('FINANCIAL_FRAUD');
    setPreviewRows([]);
    setIsParsing(false);
    setIsUploading(false);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 sm:p-6">
        <motion.div
          initial={{ opacity: 0, scale: 0.96, y: 10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.96, y: 10 }}
          transition={{ duration: 0.15 }}
          className="bg-white rounded-2xl border border-slate-200 shadow-2xl w-full max-w-3xl overflow-hidden flex flex-col my-8"
        >
          {/* Modal Header */}
          <div className="px-6 py-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-[#0e61a1]/10 border border-[#0e61a1]/20 flex items-center justify-center text-[#0e61a1]">
                <span className="material-symbols-outlined text-lg">upload_file</span>
              </div>
              <div>
                <h2 className="text-base font-bold text-slate-900 tracking-tight">
                  Upload Custom Test Suite
                </h2>
                <p className="text-xs text-slate-500">
                  Import proprietary attack vectors, compliance prompts, or multi-turn red-team scripts
                </p>
              </div>
            </div>
            <button
              onClick={() => {
                handleReset();
                onClose();
              }}
              className="text-slate-400 hover:text-slate-700 p-1 rounded-lg hover:bg-slate-100 transition-colors"
            >
              <span className="material-symbols-outlined text-xl">close</span>
            </button>
          </div>

          {/* Modal Body */}
          <form onSubmit={handleSubmit} className="p-6 space-y-5 overflow-y-auto max-h-[calc(85vh-130px)]">
            {/* Top Template Download Strip */}
            <div className="flex flex-wrap items-center justify-between gap-2 p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs">
              <div className="flex items-center gap-2 text-slate-600">
                <span className="material-symbols-outlined text-slate-500 text-base">info</span>
                <span>Need formatting reference? Download standard dataset templates:</span>
              </div>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => handleDownloadTemplate('csv')}
                  className="px-2.5 py-1 bg-white border border-slate-200 hover:bg-slate-100 text-slate-700 font-semibold rounded-lg text-[11px] font-mono flex items-center gap-1 shadow-2xs transition-all"
                >
                  <span className="material-symbols-outlined text-xs text-[#0e61a1]">download</span>
                  Sample CSV
                </button>
                <button
                  type="button"
                  onClick={() => handleDownloadTemplate('json')}
                  className="px-2.5 py-1 bg-white border border-slate-200 hover:bg-slate-100 text-slate-700 font-semibold rounded-lg text-[11px] font-mono flex items-center gap-1 shadow-2xs transition-all"
                >
                  <span className="material-symbols-outlined text-xs text-[#0e61a1]">download</span>
                  Sample JSON (Multi-Turn)
                </button>
              </div>
            </div>

            {/* File Drag & Drop Zone */}
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                Dataset File (CSV or JSON) <span className="text-rose-500">*</span>
              </label>
              <div
                onDragOver={(e) => {
                  e.preventDefault();
                  setIsDragOver(true);
                }}
                onDragLeave={() => setIsDragOver(false)}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all flex flex-col items-center justify-center gap-2 ${
                  isDragOver
                    ? 'border-[#0e61a1] bg-[#0e61a1]/5'
                    : file
                    ? 'border-emerald-300 bg-emerald-50/40'
                    : 'border-slate-300 hover:border-slate-400 bg-slate-50/50'
                }`}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".csv,.json"
                  className="hidden"
                  onChange={(e) => {
                    if (e.target.files && e.target.files.length > 0) {
                      handleFileChange(e.target.files[0]);
                    }
                  }}
                />

                {file ? (
                  <div className="flex flex-col items-center">
                    <span className="material-symbols-outlined text-3xl text-emerald-600 mb-1">
                      check_circle
                    </span>
                    <span className="text-xs font-bold text-slate-800 font-mono">{file.name}</span>
                    <span className="text-[11px] text-slate-500 mt-0.5 font-mono">
                      {(file.size / 1024).toFixed(1)} KB &bull; Click or drop another file to replace
                    </span>
                  </div>
                ) : (
                  <>
                    <span className="material-symbols-outlined text-3xl text-slate-400">
                      cloud_upload
                    </span>
                    <p className="text-xs font-semibold text-slate-700">
                      Drag & drop your test dataset file here, or{' '}
                      <span className="text-[#0e61a1] underline font-bold">browse files</span>
                    </p>
                    <p className="text-[11px] text-slate-500 font-mono">
                      Accepts .csv (single-turn vectors) or .json (single & multi-turn scripts) up to 20MB
                    </p>
                  </>
                )}
              </div>
            </div>

            {/* Suite Details Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Test Suite Name <span className="text-rose-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g., Q3 Private Banking Red-Team Vectors"
                  value={suiteName}
                  onChange={(e) => setSuiteName(e.target.value)}
                  className="w-full bg-white border border-slate-200 rounded-lg px-3 py-2 text-xs text-slate-900 focus:outline-none focus:border-[#0e61a1] transition-colors"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                  Fallback Threat Category
                </label>
                <select
                  value={fallbackCategory}
                  onChange={(e) => setFallbackCategory(e.target.value)}
                  className="w-full bg-white border border-slate-200 rounded-lg px-3 py-2 text-xs text-slate-900 focus:outline-none focus:border-[#0e61a1] transition-colors"
                >
                  {CATEGORY_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Description (Optional)
              </label>
              <textarea
                rows={2}
                placeholder="Scope, methodology, or internal test objectives for this vector suite..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full bg-white border border-slate-200 rounded-lg px-3 py-2 text-xs text-slate-900 focus:outline-none focus:border-[#0e61a1] transition-colors resize-none"
              />
            </div>

            {/* Live Parsing Preview */}
            {previewRows.length > 0 && (
              <div className="space-y-2 pt-1 border-t border-slate-200">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                    <span className="material-symbols-outlined text-xs text-emerald-600">visibility</span>
                    File Ingestion Preview (First {previewRows.length} Vectors)
                  </span>
                  <span className="text-[11px] font-mono text-slate-500">
                    Auto-parsed from uploaded file
                  </span>
                </div>

                <div className="border border-slate-200 rounded-xl overflow-hidden shadow-2xs">
                  <table className="w-full text-left border-collapse text-[11px] font-mono">
                    <thead className="bg-slate-100/70 border-b border-slate-200 text-slate-700">
                      <tr>
                        <th className="py-2 px-3 w-12 text-center">#</th>
                        <th className="py-2 px-3">Adversarial Prompt Preview</th>
                        <th className="py-2 px-3 w-32">Category</th>
                        <th className="py-2 px-3 w-20 text-center">Severity</th>
                        <th className="py-2 px-3 w-20 text-center">Mode</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 bg-white">
                      {previewRows.map((r) => (
                        <tr key={r.id} className="hover:bg-slate-50/50">
                          <td className="py-2 px-3 text-center text-slate-400 font-bold">{r.id}</td>
                          <td className="py-2 px-3 text-slate-800 font-sans line-clamp-1 max-w-sm">
                            {r.prompt}
                          </td>
                          <td className="py-2 px-3 text-slate-600 truncate">{r.category}</td>
                          <td className="py-2 px-3 text-center">
                            <span
                              className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                                r.severity === 'CRITICAL'
                                  ? 'bg-rose-50 text-rose-700 border border-rose-200'
                                  : r.severity === 'HIGH'
                                  ? 'bg-amber-50 text-amber-700 border border-amber-200'
                                  : 'bg-slate-100 text-slate-600 border border-slate-200'
                              }`}
                            >
                              {r.severity}
                            </span>
                          </td>
                          <td className="py-2 px-3 text-center">
                            <span className="px-1.5 py-0.5 bg-slate-100 text-slate-700 rounded text-[10px] font-bold">
                              {r.mode}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Modal Footer Actions */}
            <div className="pt-4 border-t border-slate-200 flex items-center justify-between">
              <div className="text-[11px] text-slate-500 font-mono flex items-center gap-1.5">
                <span className="material-symbols-outlined text-xs text-slate-400">lock</span>
                <span>SHA-256 deduplication and validation applied automatically</span>
              </div>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  disabled={isUploading}
                  onClick={() => {
                    handleReset();
                    onClose();
                  }}
                  className="px-4 py-2 border border-slate-200 hover:bg-slate-100 rounded-lg text-xs font-semibold text-slate-700 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isUploading || !file || !suiteName.trim()}
                  className="px-5 py-2 bg-[#0e61a1] hover:bg-[#0b4e82] disabled:opacity-50 text-white rounded-lg text-xs font-bold shadow-2xs flex items-center gap-2 transition-all"
                >
                  {isUploading ? (
                    <>
                      <span className="material-symbols-outlined animate-spin text-sm">sync</span>
                      <span>Ingesting Suite...</span>
                    </>
                  ) : (
                    <>
                      <span className="material-symbols-outlined text-sm">publish</span>
                      <span>Upload & Ingest Suite</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </form>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
