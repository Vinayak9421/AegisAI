import { motion } from 'framer-motion';
import TopNavBar from '../../../shared/components/TopNavBar';
import MessageBubble from '../components/MessageBubble';
import HarmRateMeter from '../components/HarmRateMeter';
import TestCategoryTracker from '../components/TestCategoryTracker';
import { mockSimulationMessages, mockTestCategories } from '../../../store/mockData';

export default function LiveSimulationPage() {
  return (
    <div className="bg-background text-on-background min-h-screen flex flex-col pt-16">
      <TopNavBar />

      <main className="flex-grow p-6 grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Left: Live Chat Panel */}
        <motion.section
          initial={{ opacity: 0, x: -24 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
          className="lg:col-span-8 flex flex-col glass-panel rounded-xl overflow-hidden h-[calc(100vh-120px)]"
        >
          {/* Chat Header */}
          <div className="bg-surface-container-lowest border-b border-outline-variant p-4 flex justify-between items-center">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-white">
                <span className="material-symbols-outlined">bug_report</span>
              </div>
              <div>
                <h2 className="text-title-lg font-bold text-primary">Sentinel Payload Runner</h2>
                <p className="text-label-md text-on-surface-variant">Target: SupportBot v2.1</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-secondary pulse-dot" />
              <span className="text-label-md text-secondary">Scanning in progress...</span>
            </div>
          </div>

          {/* Chat Messages */}
          <div className="flex-grow overflow-y-auto p-6 space-y-6 bg-surface-bright">
            {mockSimulationMessages.map((msg, i) => (
              <MessageBubble key={msg.id} message={msg} index={i} />
            ))}

            {/* Typing indicator */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.7 }}
              transition={{ delay: 0.8 }}
              className="flex flex-col items-start max-w-[80%]"
            >
              <div className="flex items-center gap-2 mb-1">
                <span className="text-label-md font-bold text-primary">Sentinel</span>
                <span className="px-2 py-0.5 rounded-full bg-surface-container-high text-[10px] font-semibold text-on-surface-variant border border-outline-variant">
                  Bias
                </span>
              </div>
              <div className="message-out p-4 rounded-xl rounded-bl-none shadow-sm flex gap-1 items-center">
                {[0, 0.2, 0.4].map((delay, i) => (
                  <motion.span
                    key={i}
                    className="w-2 h-2 rounded-full bg-white"
                    animate={{ y: [0, -6, 0] }}
                    transition={{ repeat: Infinity, duration: 1.4, delay }}
                  />
                ))}
              </div>
            </motion.div>
          </div>
        </motion.section>

        {/* Right: Telemetry Panel */}
        <motion.aside
          initial={{ opacity: 0, x: 24 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="lg:col-span-4 flex flex-col gap-5 h-[calc(100vh-120px)]"
        >
          <HarmRateMeter />
          <TestCategoryTracker categories={mockTestCategories} />
        </motion.aside>
      </main>

      {/* Disclaimer Banner */}
      <motion.div
        initial={{ y: 48 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.4, delay: 0.3 }}
        className="bg-surface-container-highest border-t border-outline-variant py-3 px-6 text-center fixed bottom-0 w-full z-40"
      >
        <p className="text-label-md text-on-surface-variant flex items-center justify-center gap-2">
          <span className="material-symbols-outlined text-sm">info</span>
          This simulation is conducted under ethical red-teaming guidelines. Do not use derived payloads maliciously.
        </p>
      </motion.div>
    </div>
  );
}
