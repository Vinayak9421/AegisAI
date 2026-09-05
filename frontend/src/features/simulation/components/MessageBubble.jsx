import { motion } from 'framer-motion';
import { clsx } from 'clsx';

export default function MessageBubble({ message, index }) {
  const { sender, tag, text, response } = message;
  const isSentinel = sender === 'sentinel';

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.2, duration: 0.4 }}
      className="space-y-4"
    >
      {/* Sentinel (attacker) message */}
      <div className="flex flex-col items-start max-w-[80%]">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-label-md font-bold text-primary">Sentinel</span>
          <span className="px-2 py-0.5 rounded-full bg-surface-container-high text-[10px] font-semibold text-on-surface-variant border border-outline-variant">
            {tag}
          </span>
        </div>
        <div className="message-out p-4 rounded-xl rounded-bl-none text-body-md shadow-sm">
          {text}
        </div>
      </div>

      {/* Target Chatbot response */}
      {response && (
        <div className="flex flex-col items-end max-w-[80%] ml-auto">
          <div className="flex items-center gap-2 mb-1">
            <span
              className={clsx(
                'px-2 py-0.5 rounded-full text-[10px] font-bold flex items-center gap-1 border',
                response.variant === 'safe'
                  ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                  : 'bg-red-50 text-error border-red-200'
              )}
            >
              {response.variant === 'failed' && (
                <span className="material-symbols-outlined text-[14px]">warning</span>
              )}
              {response.label}
            </span>
            <span className="text-label-md font-bold text-on-surface-variant">Target Chatbot</span>
          </div>
          <div
            className={clsx(
              'message-in p-4 rounded-xl rounded-br-none text-body-md shadow-xs border',
              response.variant === 'safe'
                ? 'border-slate-200 bg-slate-50 text-slate-800'
                : 'border-rose-200 bg-rose-50/50 text-rose-900'
            )}
          >
            {response.text}
          </div>

          {/* Independent Judge Analysis */}
          {response.rationale && (
            <div className="mt-1.5 flex items-start gap-1.5 p-2.5 rounded-lg bg-sky-50/70 border border-sky-200/70 text-[11px] text-slate-700 max-w-full shadow-2xs">
              <span className="material-symbols-outlined text-[15px] text-[#0e61a1] shrink-0 mt-0.5">gavel</span>
              <div>
                <span className="font-bold text-[#0e61a1]">Judge Audit: </span>
                <span>{response.rationale}</span>
              </div>
            </div>
          )}
        </div>
      )}
    </motion.div>
  );
}
