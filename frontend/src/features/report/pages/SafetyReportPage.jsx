import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import TopNavBar from '../../../shared/components/TopNavBar';
import { mockReportFindings, mockVerificationChecklist } from '../../../store/mockData';

const barData = [20, 15, 35, 10, 5, 8];

function FindingCard({ finding, index }) {
  const [expanded, setExpanded] = useState(false);
  const isHigh = finding.severity === 'high';

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className="p-4 hover:bg-surface-container/30 transition-colors cursor-pointer group border-b border-outline-variant/20 last:border-0"
      onClick={() => setExpanded(!expanded)}
    >
      <div className="flex justify-between items-start gap-4">
        <div className="flex items-start gap-3 flex-1">
          <span className={`material-symbols-outlined icon-fill mt-0.5 ${isHigh ? 'text-error' : 'text-[#b97a00]'}`}>
            {isHigh ? 'warning' : 'error'}
          </span>
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                isHigh ? 'bg-error-container text-on-error-container' : 'bg-[#fef3c7] text-[#92400e]'
              }`}>
                {isHigh ? 'High Severity' : 'Medium Severity'}
              </span>
              <span className="text-label-md text-on-surface-variant">Category: {finding.category}</span>
            </div>
            <p className="text-body-md text-on-surface truncate max-w-xl">{finding.text}</p>
          </div>
        </div>
        <motion.span
          animate={{ rotate: expanded ? 180 : 0 }}
          className="material-symbols-outlined text-on-surface-variant group-hover:text-primary transition-colors"
        >
          expand_more
        </motion.span>
      </div>
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="overflow-hidden mt-3 ml-9 p-3 bg-surface-container-low rounded-lg text-body-md text-on-surface-variant"
          >
            Full prompt text: {finding.text} — Response leaked PII/unsafe content triggering violation flag.
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export default function SafetyReportPage() {
  const navigate = useNavigate();

  return (
    <div className="bg-background text-on-background min-h-screen pt-16">
      <TopNavBar />

      <main className="max-w-[1440px] mx-auto px-6 py-6 grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Certificate Header */}
        <motion.section
          initial={{ opacity: 0, y: -16 }}
          animate={{ opacity: 1, y: 0 }}
          className="col-span-1 lg:col-span-12 bg-surface rounded-xl border border-[#E8F4F8] shadow-ice p-8 flex flex-col md:flex-row justify-between items-start md:items-center relative overflow-hidden"
        >
          <div className="absolute -right-20 -top-20 w-64 h-64 bg-secondary/5 rounded-full blur-3xl pointer-events-none" />
          <div className="flex-1 z-10">
            <div className="flex items-center gap-3 mb-2">
              <span className="bg-[#e6f4ea] text-[#137333] px-2 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider flex items-center gap-1 border border-[#137333]/20">
                <span className="material-symbols-outlined text-[14px]">verified</span> Certified Secure
              </span>
              <span className="text-on-surface-variant text-label-md">Report ID: AEGIS-77X-992</span>
            </div>
            <h1 className="text-headline-lg font-bold text-primary mb-1">Trust & Safety Evaluation Report</h1>
            <p className="text-body-lg text-on-surface-variant">Model: LLaMA-3-Instruct-8B • Evaluated: Oct 24, 2024</p>
          </div>
          <div className="mt-6 md:mt-0 flex items-center gap-6 z-10">
            <div className="text-right">
              <p className="text-label-md text-on-surface-variant mb-1 uppercase tracking-wider">Overall Safety Score</p>
              <div className="flex items-baseline justify-end gap-1">
                <motion.span
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.3, duration: 0.5 }}
                  className="text-display-lg font-bold text-primary"
                >
                  94
                </motion.span>
                <span className="text-title-lg text-on-surface-variant">/ 100</span>
              </div>
            </div>
            <motion.div
              initial={{ scale: 0, rotate: -30 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ delay: 0.4, type: 'spring', stiffness: 200 }}
              className="w-16 h-16 rounded-full border-4 border-[#137333] flex items-center justify-center bg-[#e6f4ea]"
            >
              <span className="material-symbols-outlined icon-fill text-[32px] text-[#137333]">workspace_premium</span>
            </motion.div>
          </div>
        </motion.section>

        {/* Left Column */}
        <div className="col-span-1 lg:col-span-8 flex flex-col gap-6">
          {/* Charts Row */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Spider Chart Mockup */}
            <motion.div
              initial={{ opacity: 0, x: -16 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-surface rounded-xl border border-[#E8F4F8] shadow-ice p-6 h-80 flex flex-col"
            >
              <h2 className="text-title-lg font-bold text-primary mb-4">Category Breakdown</h2>
              <div className="flex-1 relative flex items-center justify-center">
                <svg viewBox="0 0 200 200" className="w-full h-full opacity-80">
                  {/* Hexagon grid */}
                  {[1, 0.75, 0.5, 0.25].map((scale, i) => (
                    <polygon
                      key={i}
                      points={[0,1,2,3,4,5].map(n => {
                        const angle = (n * 60 - 90) * Math.PI / 180;
                        const r = 80 * scale;
                        return `${100 + r * Math.cos(angle)},${100 + r * Math.sin(angle)}`;
                      }).join(' ')}
                      fill="none" stroke="#e5e9eb" strokeWidth="1"
                    />
                  ))}
                  {/* Data polygon */}
                  <motion.polygon
                    points={[95, 80, 95, 78, 88, 60, 95, 80, 78, 20].map((v, i) => {
                      const scores = [0.95, 0.80, 0.88, 0.75, 0.92, 0.85];
                      const angle = (i * 60 - 90) * Math.PI / 180;
                      const r = 80 * scores[i % 6];
                      return `${100 + r * Math.cos(angle)},${100 + r * Math.sin(angle)}`;
                    }).join(' ')}
                    fill="rgba(14, 97, 161, 0.12)" stroke="#0e61a1" strokeWidth="2"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.5, duration: 0.6 }}
                  />
                </svg>
                {[
                  { label: 'Injection', pos: 'top-0 left-1/2 -translate-x-1/2' },
                  { label: 'Bias', pos: 'top-1/4 right-0' },
                  { label: 'Toxicity', pos: 'bottom-1/4 right-0' },
                  { label: 'PII Leak', pos: 'bottom-0 left-1/2 -translate-x-1/2' },
                  { label: 'Hallucination', pos: 'bottom-1/4 left-0' },
                  { label: 'Jailbreak', pos: 'top-1/4 left-0' },
                ].map((l) => (
                  <div key={l.label} className={`absolute text-[10px] font-bold text-primary ${l.pos}`}>{l.label}</div>
                ))}
              </div>
            </motion.div>

            {/* Bar Chart */}
            <motion.div
              initial={{ opacity: 0, x: 16 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.15 }}
              className="bg-surface rounded-xl border border-[#E8F4F8] shadow-ice p-6 h-80 flex flex-col"
            >
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-title-lg font-bold text-primary">Session Harm Rate</h2>
                <span className="text-label-md text-on-surface-variant bg-surface-container px-2 py-1 rounded">Over 10k Prompts</span>
              </div>
              <div className="flex-1 flex items-end justify-between gap-2 border-b border-l border-outline-variant/30 pb-2 pl-2 pt-4">
                {barData.map((h, i) => (
                  <div key={i} className="flex-1 flex flex-col items-center gap-1">
                    <motion.div
                      className="w-full bg-secondary/20 rounded-t border-t-2 border-secondary hover:bg-secondary/40 transition-colors cursor-pointer"
                      initial={{ height: 0 }}
                      animate={{ height: `${h * 3}px` }}
                      transition={{ delay: i * 0.08 + 0.3, duration: 0.5 }}
                    />
                  </div>
                ))}
              </div>
              <div className="flex justify-between mt-2 text-[10px] text-on-surface-variant">
                <span>Batch 1</span><span>Batch 6</span>
              </div>
            </motion.div>
          </div>

          {/* Failure Gallery */}
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25 }}
            className="bg-surface rounded-xl border border-[#E8F4F8] shadow-ice overflow-hidden"
          >
            <div className="p-6 border-b border-outline-variant/30 bg-surface-container-lowest">
              <h2 className="text-title-lg font-bold text-primary">Failure Gallery (Flagged Prompts)</h2>
              <p className="text-body-md text-on-surface-variant mt-1">Review critical safety violations triggered during testing.</p>
            </div>
            <div className="divide-y divide-outline-variant/20">
              {mockReportFindings.map((f, i) => <FindingCard key={f.id} finding={f} index={i} />)}
            </div>
          </motion.div>
        </div>

        {/* Right Column */}
        <div className="col-span-1 lg:col-span-4 flex flex-col gap-6">
          {/* Verification Checklist */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-surface rounded-xl border border-[#E8F4F8] shadow-ice p-6"
          >
            <h2 className="text-title-lg font-bold text-primary mb-4 flex items-center gap-2">
              <span className="material-symbols-outlined text-secondary">fact_check</span>
              Verification Checklist
            </h2>
            <ul className="space-y-4">
              {mockVerificationChecklist.map((item, i) => (
                <motion.li
                  key={item.id}
                  initial={{ opacity: 0, x: -12 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 + 0.3 }}
                  className="flex items-start gap-3"
                >
                  <span className={`material-symbols-outlined icon-fill text-[20px] mt-0.5 ${item.passed ? 'text-[#137333]' : 'text-error'}`}>
                    {item.passed ? 'check_circle' : 'cancel'}
                  </span>
                  <div>
                    <p className={`text-body-md font-semibold ${item.passed ? 'text-on-surface' : 'text-error'}`}>{item.label}</p>
                    <p className={`text-label-md ${item.passed ? 'text-on-surface-variant' : 'text-error'}`}>{item.detail}</p>
                  </div>
                </motion.li>
              ))}
            </ul>
          </motion.div>

          {/* Action Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="flex flex-col gap-3"
          >
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.97 }}
              className="w-full glacier-gradient text-on-primary py-3 rounded-lg text-body-md font-semibold hover:scale-[1.02] transition-transform shadow-ice flex justify-center items-center gap-2"
            >
              <span className="material-symbols-outlined">download</span> Download PDF Report
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.97 }}
              className="w-full bg-transparent border border-[#1B4F8C] text-[#1B4F8C] py-3 rounded-lg text-body-md font-semibold hover:bg-secondary-fixed/30 transition-colors flex justify-center items-center gap-2"
            >
              <span className="material-symbols-outlined">share</span> Share Certificate Link
            </motion.button>
          </motion.div>
        </div>
      </main>
    </div>
  );
}
