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
              'message-in p-4 rounded-xl rounded-br-none text-body-md shadow-sm border',
              response.variant === 'safe'
                ? 'border-outline-variant'
                : 'border-error-container bg-error-container/20'
            )}
          >
            {response.text}
          </div>
        </div>
      )}
    </motion.div>
  );
}
