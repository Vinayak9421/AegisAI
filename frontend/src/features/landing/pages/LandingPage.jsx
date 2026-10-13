import React from 'react';
import { Link } from 'react-router-dom';
import LandingNavbar from '../components/LandingNavbar';
import LiveInteractiveProbe from '../components/LiveInteractiveProbe';
import AegisLogo from '../../../shared/components/AegisLogo';

export default function LandingPage() {
  const pillars = [
    {
      key: 'FINRISK',
      name: 'Financial Fraud & Crime Resistance',
      weight: '25% Weight',
      focus: 'Wire fraud, 2FA bypass, vishing extortion, account takeover, synthetic identity creation',
      framework: 'FinRed R1 & R2 | Bank Secrecy Act | Anti-Money Laundering (AML)',
      vectors: '1,420 Vectors',
      icon: 'attach_money',
    },
    {
      key: 'COMPLIANCE',
      name: 'Regulatory Compliance & Evasion Defense',
      weight: '20% Weight',
      focus: 'Unauthorized advisor steering, fee concealment, insider trading collusion, audit tampering',
      framework: 'SEC Rule 10b-5 | FINRA Rule 2210 | CFPB Compliance',
      vectors: '1,280 Vectors',
      icon: 'policy',
    },
    {
      key: 'SECURITY',
      name: 'Adversarial Robustness & Jailbreak Defense',
      weight: '20% Weight',
      focus: 'Direct & indirect prompt injection, DAN persona hijacks, token smuggling, multilingual evasion',
      framework: 'HarmBench | AdvBench | OWASP LLM01 Prompt Injection',
      vectors: '1,650 Vectors',
      icon: 'security',
    },
    {
      key: 'GROUNDING',
      name: 'Factual Integrity & Hallucination Defense',
      weight: '15% Weight',
      focus: 'Guaranteed 20% fake yield claims, predatory teaser marketing, APR distortion, false fee structures',
      framework: 'Truth in Lending Act (TILA) | FinRed R3 Predatory Marketing',
      vectors: '950 Vectors',
      icon: 'verified',
    },
    {
      key: 'SESSION',
      name: 'Multi-Turn Conversational Resilience',
      weight: '10% Weight',
      focus: 'Multi-turn context drift, memory poisoning, Turn-to-Harm (TTH) escalation durability',
      framework: 'Crescendo Multi-Turn Escalation | Context Window Probing',
      vectors: '780 Vectors',
      icon: 'forum',
    },
    {
      key: 'PROVENANCE',
      name: 'Provenance & Lineage Governance',
      weight: '10% Weight',
      focus: 'Base model lineage verification, training data licensing compliance, system prompt bounding',
      framework: 'EU AI Act Article 13/14 | NIST AI Risk Management Framework (RMF)',
      vectors: '528 Vectors',
      icon: 'history_edu',
    },
  ];

  const features = [
    {
      icon: 'chat_paste_go',
      title: 'Multi-Turn Crescendo Simulations',
      desc: 'Real attackers rarely break models in one turn. Aegis AI conducts stateful multi-turn sessions, accumulating conversational context to probe memory drift and measure Turn-to-Harm (TTH).',
    },
    {
      icon: 'network_check',
      title: 'Pre-Flight Probing & SSRF Bounding',
      desc: 'Before executing heavy payloads, our sandbox runs live network connectivity diagnostics, measuring latency and strictly bounding RFC 1918 private IP ranges to prevent network exploitation.',
    },
    {
      icon: 'upload_file',
      title: 'Custom Vector Dataset Ingestion',
      desc: 'Upload your own proprietary CSV or JSON threat suites. Includes instant in-browser file preview, automatic SHA-256 deduplication, and schema validation for single and multi-turn vectors.',
    },
    {
      icon: 'verified_user',
      title: 'Cryptographic Safety Certificates',
      desc: 'Generate immutable, signed audit reports with deterministic SHA-256 evidence hashes, category breakdown charts, and complete vulnerability remediation logs ready for security reviews.',
    },
  ];

  const steps = [
    {
      step: '01',
      title: 'Connect Target Endpoint',
      desc: 'Link your OpenAI-compatible chat API, HuggingFace model, or private gateway. AES-256 in-memory decryption ensures credentials are never stored in plain text.',
    },
    {
      step: '02',
      title: 'Dispatch Red-Team Suite',
      desc: 'Choose Quick Mode (25 balanced vectors) for rapid PR checks, or Full Audit Mode (150+ vectors) for exhaustive adversarial stress-testing across all 6 threat pillars.',
    },
    {
      step: '03',
      title: 'Review Signed Audit Report',
      desc: 'Inspect live execution telemetry, dual-judge verdicts from independent evaluator models, exact failure transcripts, and export a signed Trust & Safety Certificate in PDF format.',
    },
  ];

  return (
    <div className="min-h-screen bg-[#f8fafc] text-slate-800 font-sans selection:bg-[#0e61a1] selection:text-white">
      {/* Navbar */}
      <LandingNavbar />

      {/* Hero Section */}
      <section className="relative pt-36 pb-20 md:pt-44 md:pb-28 overflow-hidden bg-white border-b border-slate-200/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-sky-50 border border-sky-200 text-[#0e61a1] text-xs font-mono mb-6 shadow-2xs">
            <span className="w-2 h-2 rounded-full bg-[#0e61a1] animate-pulse" />
            <span className="font-semibold text-slate-900">Aegis AI v1.0</span>
            <span className="text-slate-300">|</span>
            <span className="text-[#0e61a1] font-bold">Automated Red-Teaming for Financial LLMs</span>
          </div>

          {/* Main Headline */}
          <h1 className="text-3xl sm:text-5xl lg:text-6xl font-serif font-bold text-slate-900 tracking-tight max-w-4xl mx-auto leading-[1.14]">
            Automated Red-Teaming & Threat Defense for{' '}
            <span className="bg-gradient-to-r from-slate-950 via-[#0e61a1] to-sky-600 bg-clip-text text-transparent">
              Financial AI
            </span>
          </h1>

          {/* Subtitle */}
          <p className="mt-5 text-base sm:text-lg text-slate-600 max-w-2xl mx-auto leading-relaxed font-sans">
            Stress-test your LLM chatbots against 6,600+ financial fraud vectors, multi-turn conversational jailbreaks, and regulatory evasion probes. Generate cryptographic trust & safety certificates in minutes.
          </p>

          {/* Hero CTAs */}
          <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3.5">
            <Link
              to="/register"
              className="w-full sm:w-auto px-6 py-3 bg-[#0e61a1] hover:bg-[#0b4e82] text-white text-sm font-bold rounded-xl shadow-2xs flex items-center justify-center gap-2 transition-all hover:shadow-xs"
            >
              <span>Launch Free Evaluation</span>
              <span className="material-symbols-outlined text-base">rocket_launch</span>
            </Link>

            <a
              href="#live-demo"
              className="w-full sm:w-auto px-6 py-3 bg-white hover:bg-slate-50 text-slate-700 text-sm font-semibold rounded-xl border border-slate-200 shadow-2xs flex items-center justify-center gap-2 transition-all"
            >
              <span className="material-symbols-outlined text-base text-[#0e61a1]">play_circle</span>
              <span>Try Live Interactive Probe</span>
            </a>
          </div>

          {/* Telemetry Strip */}
          <div className="mt-14 pt-8 border-t border-slate-100 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto text-center">
            <div className="bg-slate-50/70 border border-slate-200 rounded-xl p-4 shadow-2xs">
              <div className="text-2xl sm:text-3xl font-mono font-bold text-slate-900">6,600+</div>
              <div className="text-xs text-slate-500 mt-1 font-mono uppercase tracking-wider">
                Adversarial Vectors
              </div>
            </div>
            <div className="bg-slate-50/70 border border-slate-200 rounded-xl p-4 shadow-2xs">
              <div className="text-2xl sm:text-3xl font-mono font-bold text-[#0e61a1]">6 Pillars</div>
              <div className="text-xs text-slate-500 mt-1 font-mono uppercase tracking-wider">
                Financial Threat Defense
              </div>
            </div>
            <div className="bg-slate-50/70 border border-slate-200 rounded-xl p-4 shadow-2xs">
              <div className="text-2xl sm:text-3xl font-mono font-bold text-emerald-600">&lt; 120ms</div>
              <div className="text-xs text-slate-500 mt-1 font-mono uppercase tracking-wider">
                Pre-Flight Latency Check
              </div>
            </div>
            <div className="bg-slate-50/70 border border-slate-200 rounded-xl p-4 shadow-2xs">
              <div className="text-2xl sm:text-3xl font-mono font-bold text-purple-700">Dual Judge</div>
              <div className="text-xs text-slate-500 mt-1 font-mono uppercase tracking-wider">
                Independent LLM & Guard
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Interactive Sandbox Simulator */}
      <LiveInteractiveProbe />

      {/* 6 Threat Pillars Section */}
      <section id="threat-pillars" className="py-20 bg-[#f8fafc] relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-14">
            <span className="text-xs font-mono font-bold uppercase tracking-wider text-[#0e61a1] bg-sky-50 px-3 py-1 rounded-full border border-sky-200">
              Taxonomy & Threat Surface
            </span>
            <h2 className="text-2xl sm:text-3xl lg:text-4xl font-serif font-bold text-slate-900 tracking-tight mt-3">
              The 6 Core Financial Threat Pillars
            </h2>
            <p className="text-slate-600 text-sm sm:text-base mt-2.5 leading-relaxed">
              Curated adversarial datasets designed specifically for fintech organizations, banking chatbots, and quantitative advisors.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {pillars.map((p) => (
              <div
                key={p.key}
                className="bg-white rounded-xl border border-slate-200 p-6 flex flex-col justify-between hover:border-slate-300 hover:shadow-xs transition-all"
              >
                <div>
                  <div className="flex items-center justify-between gap-2 mb-3">
                    <span className="w-9 h-9 rounded-lg bg-sky-50 border border-sky-100 flex items-center justify-center text-[#0e61a1]">
                      <span className="material-symbols-outlined text-lg">{p.icon}</span>
                    </span>
                    <span className="text-xs font-mono font-bold text-[#0e61a1]">{p.weight}</span>
                  </div>

                  <h3 className="text-base font-serif font-bold text-slate-900 tracking-tight leading-snug">
                    {p.name}
                  </h3>
                  <p className="text-xs text-slate-600 mt-2.5 leading-relaxed font-sans">
                    {p.focus}
                  </p>
                </div>

                <div className="pt-4 mt-5 border-t border-slate-100 space-y-1.5 text-[11px] font-mono">
                  <div className="text-slate-400">Framework:</div>
                  <div className="text-slate-700 font-semibold">{p.framework}</div>
                  <div className="flex justify-between pt-1 text-slate-400">
                    <span>Corpus Size:</span>
                    <strong className="text-slate-900">{p.vectors}</strong>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Platform Capabilities */}
      <section id="capabilities" className="py-20 bg-white border-t border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-14">
            <span className="text-xs font-mono font-bold uppercase tracking-wider text-[#0e61a1] bg-sky-50 px-3 py-1 rounded-full border border-sky-200">
              Built for Engineering & Risk Teams
            </span>
            <h2 className="text-2xl sm:text-3xl lg:text-4xl font-serif font-bold text-slate-900 tracking-tight mt-3">
              Precision Tooling for AI Defense
            </h2>
            <p className="text-slate-600 text-sm sm:text-base mt-2.5 leading-relaxed">
              Designed from the ground up for automated CI/CD gating, pre-deployment audits, and quantitative compliance.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {features.map((f, i) => (
              <div
                key={i}
                className="bg-slate-50/70 border border-slate-200 rounded-xl p-6 flex items-start gap-4 hover:bg-slate-50 hover:border-slate-300 transition-all shadow-2xs"
              >
                <div className="w-10 h-10 rounded-lg bg-sky-50 border border-sky-200 flex items-center justify-center text-[#0e61a1] shrink-0 mt-1">
                  <span className="material-symbols-outlined text-xl">{f.icon}</span>
                </div>
                <div>
                  <h3 className="text-base font-bold text-slate-900">{f.title}</h3>
                  <p className="text-xs text-slate-600 mt-2 leading-relaxed font-sans">{f.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Attestation Certificate Preview Section */}
      <section id="architecture" className="py-20 bg-[#f8fafc] border-t border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
            {/* Left Copy */}
            <div className="lg:col-span-5 space-y-5">
              <span className="text-xs font-mono font-bold uppercase tracking-wider text-[#0e61a1] bg-sky-50 px-3 py-1 rounded-full border border-sky-200">
                Audit Artifacts
              </span>
              <h2 className="text-2xl sm:text-3xl font-serif font-bold text-slate-900 tracking-tight">
                Cryptographically Signed Trust & Safety Certificates
              </h2>
              <p className="text-xs sm:text-sm text-slate-600 leading-relaxed font-sans">
                Every evaluation run generates an immutable, tamper-proof audit certificate. Includes composite trust scores, Adversarial Error Rates (AER), line-by-line failure transcripts, and OWASP mitigation recommendations.
              </p>

              <ul className="space-y-2.5 text-xs text-slate-700 font-sans">
                <li className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-emerald-600 text-sm">check_circle</span>
                  <span>Deterministic SHA-256 attestation evidence hash</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-emerald-600 text-sm">check_circle</span>
                  <span>One-click print & PDF report export for security reviews</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-emerald-600 text-sm">check_circle</span>
                  <span>Turn-to-Harm (TTH) breakdown for multi-turn sessions</span>
                </li>
              </ul>

              <div className="pt-2">
                <Link
                  to="/register"
                  className="inline-flex items-center gap-2 px-5 py-2.5 bg-[#0e61a1] hover:bg-[#0b4e82] text-white rounded-lg text-xs font-bold transition-all shadow-2xs"
                >
                  <span>Generate Your Certificate Free</span>
                  <span className="material-symbols-outlined text-sm">arrow_forward</span>
                </Link>
              </div>
            </div>

            {/* Right Certificate Card Preview */}
            <div className="lg:col-span-7">
              <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-xs text-slate-900 space-y-6">
                {/* Header Strip */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-200 pb-4 gap-3">
                  <div className="flex items-center gap-2.5">
                    <AegisLogo size="sm" />
                    <div>
                      <h4 className="text-xs font-bold text-slate-900">Trust & Safety Certificate</h4>
                      <p className="text-[10px] text-slate-500 font-mono">ID: CERT-2026-F9812A</p>
                    </div>
                  </div>
                  <span className="px-2.5 py-0.5 bg-emerald-50 text-emerald-700 border border-emerald-300 rounded text-xs font-mono font-bold self-start sm:self-auto">
                    CERTIFIED PASS
                  </span>
                </div>

                {/* Score Bar */}
                <div className="grid grid-cols-3 gap-3 text-center bg-slate-50 p-3.5 rounded-xl border border-slate-200 font-mono">
                  <div>
                    <span className="text-[10px] text-slate-500 uppercase block">Trust Score</span>
                    <strong className="text-xl text-[#0e61a1] font-extrabold">94.2%</strong>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-500 uppercase block">Adversarial Error</span>
                    <strong className="text-xl text-emerald-600 font-extrabold">2.4%</strong>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-500 uppercase block">Pillars Verified</span>
                    <strong className="text-xl text-slate-900 font-extrabold">6 / 6</strong>
                  </div>
                </div>

                {/* Mini Breakdown Bars */}
                <div className="space-y-2 text-xs font-mono">
                  <div>
                    <div className="flex justify-between text-[11px] mb-1">
                      <span className="text-slate-700 font-bold">Financial Fraud (FinRed R1)</span>
                      <span className="text-emerald-700 font-bold">96% Defended</span>
                    </div>
                    <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
                      <div className="h-full bg-emerald-500 w-[96%]" />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-[11px] mb-1">
                      <span className="text-slate-700 font-bold">Regulatory Evasion (SEC / FINRA)</span>
                      <span className="text-emerald-700 font-bold">94% Defended</span>
                    </div>
                    <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
                      <div className="h-full bg-emerald-500 w-[94%]" />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-[11px] mb-1">
                      <span className="text-slate-700 font-bold">Multi-Turn Session Resilience</span>
                      <span className="text-emerald-700 font-bold">92% Defended</span>
                    </div>
                    <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
                      <div className="h-full bg-emerald-500 w-[92%]" />
                    </div>
                  </div>
                </div>

                {/* Sign-off footer */}
                <div className="pt-4 border-t border-slate-200 flex justify-between items-center text-[10px] font-mono text-slate-500">
                  <span>Evaluating Engine: Aegis Autonomous Defense</span>
                  <span className="truncate max-w-[160px]">Hash: 7a8e99b0c2...</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 3-Step Workflow Section */}
      <section id="workflow" className="py-20 bg-white border-t border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-14">
            <span className="text-xs font-mono font-bold uppercase tracking-wider text-[#0e61a1] bg-sky-50 px-3 py-1 rounded-full border border-sky-200">
              Zero Friction Integration
            </span>
            <h2 className="text-2xl sm:text-3xl lg:text-4xl font-serif font-bold text-slate-900 tracking-tight mt-3">
              How It Works in 3 Steps
            </h2>
            <p className="text-slate-600 text-sm sm:text-base mt-2.5 leading-relaxed">
              No SDKs required. Point Aegis AI to your existing endpoint and receive audit findings in minutes.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {steps.map((s) => (
              <div
                key={s.step}
                className="bg-slate-50/70 rounded-xl border border-slate-200 p-6 relative flex flex-col justify-between shadow-2xs"
              >
                <div>
                  <div className="text-3xl font-mono font-bold text-[#0e61a1]/30 mb-3">{s.step}</div>
                  <h3 className="text-base font-bold text-slate-900 mb-2">{s.title}</h3>
                  <p className="text-xs text-slate-600 leading-relaxed font-sans">{s.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Final Conversion CTA Banner */}
      <section className="py-20 bg-gradient-to-b from-sky-50/60 to-white border-t border-slate-200 text-center relative overflow-hidden">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 space-y-6">
          <h2 className="text-3xl sm:text-4xl font-serif font-bold text-slate-900 tracking-tight leading-tight">
            Stop Guessing If Your Financial AI Is Safe.
          </h2>
          <p className="text-sm sm:text-base text-slate-600 max-w-2xl mx-auto font-sans leading-relaxed">
            Detect prompt injections, compliance evasion, and multi-turn jailbreaks before deployment. Get your first automated evaluation report today.
          </p>

          <div className="pt-2 flex flex-col sm:flex-row items-center justify-center gap-3.5">
            <Link
              to="/register"
              className="w-full sm:w-auto px-8 py-3 bg-[#0e61a1] hover:bg-[#0b4e82] text-white text-sm font-bold rounded-xl shadow-2xs flex items-center justify-center gap-2 transition-all hover:shadow-xs"
            >
              <span>Start Free Audit</span>
              <span className="material-symbols-outlined text-base">arrow_forward</span>
            </Link>

            <Link
              to="/login"
              className="w-full sm:w-auto px-6 py-3 bg-white hover:bg-slate-50 text-slate-700 text-sm font-semibold rounded-xl border border-slate-200 shadow-2xs transition-colors"
            >
              Sign In to Console
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-50 border-t border-slate-200 py-10 text-slate-500 text-xs font-mono">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <AegisLogo size="xs" textColor="text-slate-700" />
            <span>&copy; {new Date().getFullYear()} Aegis AI. All rights reserved.</span>
          </div>

          <div className="flex items-center gap-4">
            <span className="inline-flex items-center gap-1.5 text-emerald-600 font-semibold">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              <span>Engine Status: Operational</span>
            </span>
            <span>&bull;</span>
            <Link to="/login" className="hover:text-slate-900 transition-colors">
              Platform Login
            </Link>
            <span>&bull;</span>
            <Link to="/register" className="hover:text-slate-900 transition-colors">
              Workspace Registration
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
