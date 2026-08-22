import { useState } from 'react';
import { motion } from 'framer-motion';
import AdminLayout from '../../../shared/components/AdminLayout';
import TestSuiteCard from '../components/TestSuiteCard';
import { mockBenchmarkPools } from '../../../store/mockData';

const toggleItems = [
  { id: 'single', label: 'Single-turn Evaluation', detail: 'Basic prompt-response testing.', defaultOn: true },
  { id: 'multi', label: 'Multi-turn Conversation', detail: 'Context retention and drift analysis.', defaultOn: true },
  { id: 'agentic', label: 'Agentic Simulation', detail: 'Complex tool-use and logic chains.', defaultOn: false },
];

function Toggle({ item }) {
  const [on, setOn] = useState(item.defaultOn);
  return (
    <div className="flex items-center justify-between p-3 rounded-lg hover:bg-surface-container transition-colors">
      <div>
        <p className="text-body-md font-semibold text-on-background">{item.label}</p>
        <p className="text-xs text-on-surface-variant mt-0.5">{item.detail}</p>
      </div>
      <button
        onClick={() => setOn(!on)}
        className={`relative w-11 h-6 rounded-full transition-colors duration-300 ${on ? 'bg-secondary' : 'bg-outline-variant'}`}
      >
        <motion.span
          animate={{ x: on ? 20 : 0 }}
          transition={{ duration: 0.2 }}
          className="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow"
        />
      </button>
    </div>
  );
}

export default function TestSuitePage() {
  return (
    <AdminLayout>
      {/* Header */}
      <header className="flex-shrink-0 p-8 pb-0">
        <motion.div
          initial={{ opacity: 0, y: -16 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 flex flex-col md:flex-row md:items-end justify-between gap-4"
        >
          <div>
            <h2 className="text-headline-lg font-bold text-primary tracking-tight">Benchmark Management</h2>
            <p className="text-body-lg text-on-surface-variant mt-2">
              Configure and manage test suites, judge models, and execution parameters.
            </p>
          </div>
          <div className="flex gap-3">
            <motion.button
              whileHover={{ scale: 1.02 }}
              className="px-4 py-2 rounded-lg border border-primary text-primary hover:bg-primary/5 transition-colors text-label-md font-medium flex items-center gap-2"
            >
              <span className="material-symbols-outlined text-[18px]">download</span> Export Config
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.02 }}
              className="px-4 py-2 rounded-lg bg-primary text-white hover:bg-primary-container transition-colors text-label-md font-medium shadow-sm flex items-center gap-2"
            >
              <span className="material-symbols-outlined text-[18px]">save</span> Save Changes
            </motion.button>
          </div>
        </motion.div>
      </header>

      {/* Bento Grid */}
      <div className="flex-1 overflow-y-auto p-8 pt-0">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
          {/* Left: Benchmark Pools */}
          <div className="lg:col-span-8 flex flex-col gap-5">
            <h3 className="text-title-lg font-bold text-on-background flex items-center gap-2">
              <span className="material-symbols-outlined text-secondary">library_books</span>
              Active Benchmark Pools
            </h3>
            {mockBenchmarkPools.map((pool, i) => (
              <TestSuiteCard key={pool.id} pool={pool} index={i} />
            ))}
          </div>

          {/* Right: Config Panel */}
          <div className="lg:col-span-4 flex flex-col gap-5">
            {/* Judge Configuration */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="glass-card rounded-xl p-6"
            >
              <h3 className="text-title-lg font-bold text-on-background flex items-center gap-2 mb-6">
                <span className="material-symbols-outlined text-secondary">gavel</span> Judge Configuration
              </h3>
              <div className="space-y-5">
                <div>
                  <label className="block text-label-md text-on-surface-variant mb-2">Primary Judge Model</label>
                  <div className="relative">
                    <select className="w-full bg-surface border border-outline-variant rounded-lg py-2.5 px-3 text-on-background focus:border-secondary focus:ring-1 focus:ring-secondary outline-none appearance-none text-body-md">
                      <option>Llama-Guard-3-8B</option>
                      <option>Groq-Mixtral-8x7b</option>
                      <option>GPT-4-Turbo-Judge</option>
                      <option>Custom Evaluation Endpoint</option>
                    </select>
                    <span className="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none">expand_more</span>
                  </div>
                </div>
                <div>
                  <label className="block text-label-md text-on-surface-variant mb-2">Fallback Judge</label>
                  <div className="relative">
                    <select className="w-full bg-surface border border-outline-variant rounded-lg py-2.5 px-3 text-on-background focus:border-secondary focus:ring-1 focus:ring-secondary outline-none appearance-none text-body-md">
                      <option>Groq-Llama3-70B</option>
                      <option>None (Fail Fast)</option>
                    </select>
                    <span className="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 text-on-surface-variant pointer-events-none">expand_more</span>
                  </div>
                </div>
                <div className="pt-4 border-t border-outline-variant/30">
                  <label className="block text-label-md text-on-surface-variant mb-3 flex justify-between">
                    Global Rate Limit
                    <span className="text-secondary font-bold">150 RPM</span>
                  </label>
                  <input type="range" min="10" max="500" defaultValue="150" className="w-full h-1 bg-outline-variant rounded-lg appearance-none cursor-pointer accent-secondary" />
                  <div className="flex justify-between text-xs text-on-surface-variant mt-2">
                    <span>10</span><span>500</span>
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Execution Scope Toggles */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
              className="glass-card rounded-xl p-6 flex-1"
            >
              <h3 className="text-title-lg font-bold text-on-background flex items-center gap-2 mb-6">
                <span className="material-symbols-outlined text-secondary">toggle_on</span> Execution Scope
              </h3>
              <div className="space-y-4">
                {toggleItems.map((item) => <Toggle key={item.id} item={item} />)}
              </div>
              <div className="mt-6 p-4 rounded-lg bg-tertiary-container/20 border border-tertiary-container/30 flex items-start gap-3">
                <span className="material-symbols-outlined text-[#a1cedc] mt-0.5">info</span>
                <p className="text-xs text-on-background leading-relaxed">
                  Agentic simulations require dedicated compute nodes. Ensure rate limits are adjusted accordingly.
                </p>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </AdminLayout>
  );
}
