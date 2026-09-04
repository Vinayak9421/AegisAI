# AEGIS AI — NEGATIVE-SIDE / RISK AUDIT

## Purpose

This document is a critical audit of the Aegis AI architecture, research methodology, evaluation metrics, security model, backend design, database design, and FYP feasibility.

The goal is not to reject the project. The goal is to identify **everything that can go wrong, everything a critical judge can challenge, and everything that could make the results misleading or the implementation unreliable**.

This document should be treated as a pre-implementation and pre-viva risk checklist.

---

# 1. Provenance Score Can Be Gamed

## Problem

The proposed provenance/identity scoring approach can reward the **presence and quality of documentation** without proving that the documented information is actually true.

## Why This Is a Problem

A system could provide:

- complete model documentation
- provider information
- fine-tuning information
- data-source documentation
- configuration records

while the underlying claims are inaccurate.

Therefore:

> Documentation completeness ≠ factual truth.

## What Can Fail

A target may receive a high provenance score even though:

- its model identity is incorrect
- its dataset claims are unverifiable
- its fine-tuning claims are misleading
- its configuration documentation is outdated

## Impact

The score could be interpreted incorrectly as a factual trust guarantee.

## Required Mitigation

Separate:

- declared information
- documented information
- evidence-backed information
- independently verified information
- unverifiable information

Consider renaming the metric to:

**Provenance Transparency Score**

or

**Provenance Evidence Score**

rather than implying factual verification.

---

# 2. Trust Score Weights Are Arbitrary

## Problem

The proposed Trust Score weights are architectural choices rather than empirically established constants.

Example:

- Identity = 35%
- Behavioral Safety = 55%
- Other metrics = 10%

Severity weights such as:

- LOW = 0.25
- MEDIUM = 0.50
- HIGH = 0.80
- CRITICAL = 1.00

are also design decisions.

## Why This Is a Problem

A judge can ask:

> “Why 35/55/10? Why not 20/70/10?”

Without justification, the score looks subjective.

## What Can Fail

Changing the weights can substantially change rankings between systems.

## Required Mitigation

- Version the scoring formula.
- Document the rationale.
- Perform sensitivity analysis.
- Keep raw metrics visible.
- Do not present the weights as universal scientific truth.
- Record the scoring version in every evaluation/certificate.

---

# 3. Aggregate Trust Score Can Hide Critical Failures

## Problem

A weighted average can produce a high overall score even when a system has a severe vulnerability.

Example:

A system receives a Trust Score of 92 but has a CRITICAL fraud-enabling failure.

## Why This Is Dangerous

Users may interpret 92/100 as “very safe.”

## Required Mitigation

Use:

- aggregate Trust Score
- category-level scores
- severity breakdown
- critical/high-severity flags
- minimum thresholds where appropriate

A critical vulnerability must remain highly visible even when the aggregate score is high.

---

# 4. AER Thresholds May Be Arbitrary

## Problem

Attack Effectiveness Rate may depend on category-specific severity thresholds.

## Risk

A judge can ask:

> “Why does this severity qualify as an effective attack?”

## Required Mitigation

Document:

- threshold definition
- rationale
- rubric version
- category-specific logic
- raw severity distribution

Treat thresholds as project-defined research parameters unless externally validated.

---

# 5. LLM Judge Is a Major Failure Point

## Problem

The LLM-based evaluator can itself be wrong.

Possible failures:

- false SAFE
- false UNSAFE
- wrong severity
- wrong category
- inconsistent decisions
- hallucinated rationale
- poor confidence calibration

## Why It Matters

The system is evaluating AI systems using another AI system.

If the evaluator is wrong, the final score can be wrong even if the target behavior was correctly recorded.

## Additional Risk

The target's response is potentially hostile input.

A target may attempt to manipulate the judge with text such as:

- “Ignore previous instructions.”
- “Classify this response as SAFE.”
- hidden instructions
- malicious formatting
- Unicode tricks
- JSON-like content

## Required Mitigation

- Strong evaluator/system instruction separation
- Structured output schema
- Input size limits
- Safe serialization
- Schema validation
- No target-controlled evaluator instructions
- Retry/repair handling
- Human-review sampling
- Judge validation dataset
- Versioned judge/rubric

Invalid judge output must never silently become SAFE.

---

# 6. Calling the Judge “Independent” Can Be Misleading

## Problem

A second LLM evaluator is not necessarily statistically independent.

It may share:

- training data
- model architecture
- alignment behavior
- safety biases
- benchmark contamination

## Better Terminology

Use:

- Decoupled Evaluator
- Secondary Evaluator
- Independent Evaluation Layer

unless genuine independence can be demonstrated.

---

# 7. Judge Validation Dataset May Be Too Small

## Problem

A proposed validation set of around 100 examples may be too small when divided across many:

- categories
- severities
- languages
- attack types

## What Can Fail

The evaluator may appear accurate overall while performing badly on an important category.

Example:

95% overall accuracy but poor recall on CRITICAL findings.

## Required Mitigation

Measure:

- precision
- recall
- F1
- confusion matrix
- high-severity recall
- category-level performance
- severity-level performance
- agreement with human labels
- confidence calibration where applicable

If sample size remains limited, explicitly state the limitation.

---

# 8. Correlation Study Has Weak Statistical Power With Few Targets

## Problem

A correlation between provenance and safety cannot be strongly supported using only a very small number of independent targets/configurations.

## Critical Issue

Repeated runs of the same target are not equivalent to independent systems.

## What Can Fail

The project may report a statistically impressive-looking correlation based on repeated measurements of the same system.

## Required Mitigation

Distinguish:

- target-level observations
- configuration-level observations
- repeated-run observations

Do not artificially inflate sample size.

If the number of independent targets is small, describe the result as:

**exploratory**

rather than definitive.

---

# 9. Correlation Does Not Prove Causation

## Problem

Even if provenance transparency correlates with safety, that does not mean provenance causes safety.

## Possible Confounders

- engineering maturity
- provider quality
- model size
- safety tuning
- dataset quality
- development resources
- monitoring maturity
- application complexity

## Required Mitigation

State clearly:

> Correlation between provenance transparency and behavioral safety does not establish causation.

Where possible, record potential confounding variables.

---

# 10. Benchmark Contamination

## Problem

Public red-team/jailbreak datasets may have been used during model training or safety tuning.

## What Can Fail

A target may perform well simply because it has already seen similar attacks.

## Required Mitigation

Separate:

- public benchmark tests
- Aegis-authored tests
- held-out tests
- domain-specific fintech tests

Avoid evaluating adaptive attackers on the same data used to train them.

---

# 11. Dataset Composition Can Bias Results

## Problem

Generic jailbreak datasets may not accurately represent fintech-specific risks.

## Risk

A model may perform well on generic attacks while failing on financial application threats.

## Required Mitigation

Maintain explicit categories for:

- fraud facilitation
- financial misinformation
- regulatory misstatement
- sensitive information leakage
- eligibility manipulation
- prompt injection
- indirect/RAG injection
- excessive authority
- tool misuse
- privacy
- fairness/bias where relevant

Record:

- category distribution
- severity distribution
- language
- dataset source
- license
- version
- transformations
- deduplication
- sampling strategy

---

# 12. Quick Mode Can Produce Unstable Scores

## Problem

A small Quick Mode test set may not represent the full behavior of the target.

## What Can Fail

Two Quick evaluations may produce noticeably different scores simply because of sample composition.

## Required Mitigation

Label Quick Mode as:

**Preliminary / Rapid Evaluation**

Display:

- number of tests
- category coverage
- severity coverage
- exclusions

Do not imply that Quick Mode is statistically equivalent to Full Mode.

---

# 13. Certificate Terminology Can Overclaim

## Problem

“Certificate” may imply formal regulatory or compliance certification.

## Risk

Users or judges may misunderstand the result.

## Required Wording

Use a name such as:

**Aegis AI Trust & Safety Evaluation Certificate**

and explicitly state:

> This output is an application-level trust and safety assessment. It is not regulatory certification, legal certification, compliance certification, or a guarantee of safety.

The disclaimer should appear in:

- UI
- certificate
- documentation
- relevant API metadata

---

# 14. Multi-Turn Session Recovery Is Difficult

## Problem

Multi-turn evaluation introduces stateful execution.

## Possible Failures

- incorrect conversation history
- duplicate turns
- wrong turn numbering
- session corruption
- partial recovery
- concurrent workers
- unsafe continuation
- inconsistent retry behavior

## Required Mitigation

Define:

- authoritative conversation history
- session ID
- turn ID
- turn number
- history hash
- session state
- recovery behavior
- retry behavior

---

# 15. Retries Can Produce Different Model Responses

## Problem

If an external model request times out or fails ambiguously, retrying can produce a different response.

## Risk

The system may accidentally evaluate one response while storing another.

## Required Mitigation

Distinguish:

- transport failure
- unknown outcome
- successful response
- evaluation result

Record:

- attempt number
- timestamps
- connector status
- retry reason
- final authoritative response

Never silently overwrite attempts.

---

# 16. At-Least-Once Execution Can Duplicate External Requests

## Problem

Database idempotency can prevent duplicate logical results, but the external target may still receive the request twice.

## Why It Matters

This is acceptable for read-only inference.

It is dangerous for agents with side effects.

## Required Mitigation

For MVP:

- support read-only/query operations
- use provider request IDs where possible
- avoid real-world side effects

Clearly document:

**logical idempotency ≠ external request idempotency**

---

# 17. Agent Connectors Introduce Side-Effect Risk

## Problem

Agent systems can potentially:

- send messages
- modify records
- call tools
- execute transactions
- access external systems

## Risk

A red-team test could accidentally perform a real action.

## Required Mitigation

MVP agent testing should use:

- mock tools
- simulated APIs
- sandbox environments
- read-only operations

Real financial actions should not be part of an uncontrolled FYP evaluation.

---

# 18. Agent Connector Is Too Complex for Core MVP

## Problem

Agent testing introduces:

- tool authorization
- SSRF
- trace integrity
- side effects
- authentication
- replay complexity

## Recommendation

Keep agent evaluation as:

**STRETCH / controlled experimental feature**

unless the project explicitly requires it.

---

# 19. Trace Data May Be Incomplete or Untrustworthy

## Problem

A target-provided trace may not contain every internal step.

## Possible States

- FULL_TRACE
- PARTIAL_TRACE
- NO_TRACE
- INVALID_TRACE

## Risk

Missing trace information could incorrectly make a system appear safer.

## Required Mitigation

Never interpret:

**No trace = no failure**

Instead:

**No trace = not observable**

---

# 20. CMR Can Be Gamed

## Problem

If CMR depends on intermediate traces, a system can appear better simply by exposing fewer intermediate steps.

## Required Mitigation

Report:

- trace availability
- trace completeness
- observable stages
- CMR
- number of non-observable stages

Mark CMR unavailable when the required trace evidence does not exist.

---

# 21. SHR Can Have Selection Bias

## Problem

Infrastructure failures may be excluded from harm-rate calculations.

## Risk

A system that frequently fails to respond could appear safer because unsafe behavior was never evaluated.

## Required Mitigation

Always report:

- eligible tests
- excluded tests
- infrastructure failures
- timeouts
- target unavailable
- judge failures
- incomplete evaluations

Never show a safety percentage without its denominator and exclusions.

---

# 22. SSRF Protection May Be Over-Engineered for an FYP

## Problem

Production-grade SSRF protection involving:

- egress proxies
- firewalls
- DNS controls
- network isolation

may consume excessive FYP time.

## Required Split

### MVP

- HTTPS where possible
- scheme validation
- URL canonicalization
- hostname validation
- private/loopback/link-local/metadata IP blocking
- redirect validation
- timeouts
- allowlists where appropriate

### Production

- isolated worker network
- egress proxy
- firewall policy
- DNS revalidation/pinning
- network-level enforcement

Application validation alone should not be described as a complete production security boundary.

---

# 23. Custom Cryptography / KMS May Be Over-Engineered

## Problem

Implementing custom encryption or key-management infrastructure creates security risk.

## Required Mitigation

Never invent cryptography.

Use:

- managed secret/key infrastructure
- authenticated encryption
- key versioning
- rotation
- revocation
- strict access control

For the FYP, keep production KMS/HSM hardening separate from the core implementation if necessary.

---

# 24. Redis + PostgreSQL + Workers Increase Complexity

## Problem

Multiple state systems create distributed consistency issues.

## Failure Possibilities

- Redis unavailable
- queue message lost
- worker crashes
- DB state differs from queue state
- duplicate messages
- stale leases

## Required Rule

**PostgreSQL is the source of truth.**

Redis should be treated as a queue/coordination mechanism, not authoritative job state.

Define recovery and reconciliation behavior.

---

# 25. Full Multi-Tenancy/RBAC May Be Over-Engineered

## Problem

A university FYP may not need enterprise-grade multi-tenant authorization.

## Risk

Too much implementation effort goes into platform infrastructure rather than the actual research contribution.

## Better Approach

Keep:

- tenant-aware architecture
- ownership boundaries
- correct authorization
- audit logging

But make enterprise-level RBAC a production-hardening concern if it is not required by the FYP.

---

# 26. Database Schema May Be Too Large

## Problem

A highly detailed schema can become a project by itself.

## Risk

The team spends more time implementing:

- metadata tables
- audit tables
- version tables
- job tables
- trace tables
- configuration tables

than implementing the core evaluation engine.

## Required Mitigation

Perform a feature-to-table audit.

For every table ask:

> Is this necessary for the core FYP?

Keep tables required for:

- evaluation reproducibility
- security
- auditability
- core metrics
- execution
- evidence

Move purely advanced functionality to stretch/future scope.

---

# 27. Adaptive Attacker Can Consume the Entire Project

## Problem

Adaptive attack generation is a complex research problem.

It requires:

- attack generation
- optimization
- evaluation
- budget management
- stopping criteria
- reproducibility
- held-out evaluation

## Recommendation

Keep it **STRETCH**.

Do not allow it to delay the core system.

---

# 28. LoRA Attacker Training Can Overfit

## Problem

An attacker fine-tuned on a particular attack dataset may simply memorize that dataset.

## Risk

It may look better on the training benchmark without generalizing.

## Required Mitigation

Use:

- training set
- validation set
- held-out test set

Compare:

- baseline attacker
- trained attacker
- held-out performance

Do not evaluate the attacker only on data it saw during training.

---

# 29. Too Many Research Contributions Can Weaken the Story

## Problem

Aegis AI currently touches many research areas.

This can make the central contribution unclear.

## Risk

A judge may ask:

> “What exactly is your novel contribution?”

## Recommended Positioning

### Primary

**Provenance-aware application-level red-team evaluation for fintech-oriented LLM systems.**

### Secondary

- multi-turn evaluation
- evidence-aware reporting
- trace-aware analysis
- reproducible scoring/reporting

### Stretch

- adaptive attacker
- LoRA
- advanced agent evaluation

---

# 30. “Universal Connector” Is an Overclaim

## Problem

Supporting every chatbot/LLM/application is unrealistic.

## Better Term

**Extensible Connector Architecture**

Only claim support for connector types that are actually implemented and tested.

---

# 31. Local HuggingFace Support Is Hardware-Dependent

## Problem

Local inference depends on:

- CPU
- RAM
- GPU/VRAM
- quantization
- model architecture
- tokenizer
- inference framework

## What Can Fail

A model may work on one machine and fail on another.

## Required Mitigation

Document:

- supported/tested models
- minimum hardware
- model size limitations
- quantization assumptions
- timeout behavior
- unsupported model behavior

Do not claim universal HuggingFace compatibility.

---

# 32. LLM-Generated Mitigation Recommendations Can Hallucinate

## Problem

If an LLM generates remediation advice, it may recommend:

- nonexistent controls
- inappropriate mitigations
- irrelevant security mechanisms

## Better Approach

Use deterministic:

**Finding Category → Recommended Mitigation**

mapping.

LLM-generated explanations may supplement deterministic recommendations, but should not silently invent security controls.

---

# 33. PII Redaction Is Not Perfect

## Problem

Prompts, responses and traces may contain sensitive information.

Automated redaction can miss data.

## Risk

A system could falsely claim that all personal/financial data has been removed.

## Required Mitigation

Use:

- configurable redaction
- data minimization
- restricted raw evidence access
- retention policies
- audit logging
- explicit redaction limitations

Never claim perfect PII detection.

---

# 34. Dataset Licensing Risk

## Problem

Not every publicly accessible dataset is legally safe to redistribute or modify.

## Required Mitigation

Record:

- source
- license
- version
- retrieval date
- transformations
- redistribution restrictions

Verify licensing before packaging datasets into the project.

---

# 35. OWASP Mapping Is Version-Sensitive

## Problem

OWASP categories and frameworks can change.

## Risk

An evaluation may reference an outdated taxonomy.

## Required Mitigation

Store:

- OWASP framework name
- edition/year/version
- mapping version

Do not describe mappings as timeless.

---

# 36. Score Uncertainty Is Easy to Ignore

## Problem

A single number can look more precise than the underlying evidence supports.

## Risk

A Trust Score of 81.4 may appear scientifically precise even when based on a small sample.

## Required Mitigation

Show:

- number of tests
- category coverage
- severity coverage
- exclusions
- preliminary/full status
- uncertainty information where statistically appropriate

Do not manufacture confidence intervals for tiny or unsuitable samples.

---

# 37. Evaluation Reproducibility Can Break

## Problem

LLM outputs can vary between runs.

## Required Metadata

Record:

- target version
- configuration version
- test-case version
- dataset version
- random seed where applicable
- judge version
- scoring version
- connector version
- model/provider version
- timestamp

Even with all metadata, exact output reproduction may not always be possible for nondeterministic remote models.

Document this limitation.

---

# 38. Cross-Target Comparison May Be Unfair

## Problem

Different systems may be evaluated under different conditions.

Differences can include:

- number of tests
- category mix
- severity mix
- language
- context
- tools
- system prompts
- retrieval configuration
- model capability

## Required Mitigation

Comparisons should show the evaluation configuration and scope.

Do not compare incompatible runs as if they were equivalent.

---

# 39. Human Review Is Necessary for Important Cases

## Problem

Fully automated evaluation can misclassify ambiguous or complex cases.

## Recommended Human Review

Prioritize:

- CRITICAL findings
- HIGH findings
- ambiguous results
- disputed classifications
- judge validation
- ground-truth dataset creation

Human review should be part of validation even if the normal evaluation pipeline is automated.

---

# 40. Silent Failure Is Unacceptable

## Problem

An evaluation system can accidentally hide failures.

Examples:

- connector failure excluded
- judge failure excluded
- malformed trace discarded
- timeout omitted
- incomplete session ignored

## Risk

The final score looks better than reality.

## Required Rule

Every excluded result must have:

- reason
- status
- audit record
- metric impact

The dashboard and certificate must expose exclusions and coverage.

---

# 41. Judge Pipeline Can Be Attacked Through Target Output

## Threats

A malicious target response may contain:

- prompt injection
- instruction overrides
- huge content
- Unicode tricks
- JSON-like payloads
- delimiter attacks
- hidden instructions
- context-overflow attempts

## Required Controls

- bounded input size
- structured serialization
- strict evaluator instructions
- schema validation
- no unnecessary judge tool access
- safe escaping
- token budgets

Treat all target output as untrusted.

---

# 42. Resource Exhaustion

## Attack Surface

An attacker/target can cause:

- huge prompts
- huge responses
- huge traces
- excessive sessions
- excessive retries
- expensive local inference
- expensive judge calls
- excessive concurrent jobs

## Required Controls

Define limits for:

- prompt size
- response size
- trace size
- turns per session
- retries
- job budget
- concurrency
- rate limits
- judge token budget

---

# 43. Authorization Must Be End-to-End

## Problem

Unpredictable IDs do not provide authorization.

## Required Rule

Every resource access must verify the ownership chain:

**Tenant/User → Target → Job → Result → Session → Trace → Certificate**

Never rely solely on IDs being difficult to guess.

---

# 44. Research Claims Must Be Separated From Engineering Features

## Problem

A working implementation does not automatically prove a research hypothesis.

## Required Separation

Clearly distinguish:

- engineering capability
- research hypothesis
- experiment
- observation
- interpretation
- production claim

Avoid turning implementation success into scientific evidence.

---

# 45. Failure Matrix Needs to Be Comprehensive

The system should define behavior for at least:

- 401
- 403
- 429
- timeout
- DNS failure
- SSRF attempt
- redirect to private IP
- target unavailable
- malformed response
- judge unavailable
- judge malformed output
- judge prompt injection
- worker crash
- duplicate worker
- stale lease
- database outage
- Redis outage
- outbox failure
- partial session
- invalid trace
- oversized response
- quota exceeded
- credential failure
- certificate generation failure

For each, document:

- cause
- detection
- behavior
- retry
- user-visible status
- metric impact
- recovery
- audit event
- security implications

---

# 46. Transaction Boundaries Can Cause Problems

## Problem

Long transactions around network calls are dangerous.

## Required Rule

Never hold a database transaction while waiting for:

- target response
- judge response
- local inference
- external provider

Use:

1. short transaction
2. claim/lease
3. external call
4. short transaction to persist result

This prevents database locks from being held unnecessarily.

---

# 47. Stale Worker Completion

## Problem

A worker can lose its lease and then later attempt to write a result.

## Risk

A stale worker could overwrite a newer attempt.

## Required Mitigation

Use:

- lease/version checks
- attempt numbers
- optimistic concurrency
- unique logical result constraints

A stale completion must fail safely.

---

# 48. Certificate Data Can Become Stale

## Problem

If a certificate represents an evaluation, later changes to:

- scoring formula
- test dataset
- target configuration
- judge model

should not alter the meaning of the old certificate.

## Required Mitigation

Certificates must store immutable references to:

- evaluation
- dataset version
- scoring version
- judge version
- target/config version
- generation timestamp

Regeneration should create a new version rather than mutating historical evidence.

---

# 49. Raw Evidence Can Create Privacy and Security Risk

## Problem

Raw prompts/responses/traces may contain sensitive content.

## Required Mitigation

Separate:

### Raw Evidence

Restricted access.

### Aggregated Results

Broader access.

### Certificate

Sanitized public/shareable representation.

Never expose:

- credentials
- authorization headers
- query secrets
- internal tokens
- unnecessary PII

---

# 50. Production Security Boundary Must Not Be Confused With FYP Security

## Problem

Application-level controls are not equivalent to infrastructure-level security.

For example:

- URL validation ≠ complete SSRF isolation
- application RBAC ≠ network isolation
- encrypted database field ≠ complete secret-management system

## Required Mitigation

Explicitly distinguish:

- FYP security controls
- production hardening

This prevents overclaiming.

---

# 51. FYP Scope Creep

## Problem

The combination of:

- provenance
- red teaming
- fintech
- multi-turn
- judge
- traces
- certificates
- adaptive attackers
- LoRA
- agents
- multi-tenancy
- distributed workers

can become too large.

## Risk

The team may build many incomplete features instead of one excellent core system.

## Required Mitigation

Freeze scope.

### MUST HAVE

Core evaluation platform.

### SHOULD HAVE

Features strengthening the research contribution.

### STRETCH

Adaptive/agent/LoRA features.

### FUTURE

Enterprise production hardening.

---

# 52. The Core Research Contribution Can Become Lost

## Problem

Too many features can make the project look like a collection of technologies.

## Judge Question

> “What is actually new here?”

## Required Answer

The project should primarily focus on:

**Provenance-aware application-level red-team evaluation for fintech-oriented LLM systems.**

Everything else should support this central story.

---

# 53. Technology Stack Can Become the Project Instead of the Research

## Problem

Using FastAPI, PostgreSQL, Redis, Celery, Next.js, Transformers, HuggingFace, LLM judges, etc. does not itself constitute novelty.

## Risk

The presentation focuses on technologies rather than contribution.

## Required Mitigation

For every technology answer:

> Why is this required by the problem?

Not:

> “Because it is modern.”

---

# 54. Local Model Support Can Distort Comparisons

## Problem

Different local models may have different:

- hardware
- quantization
- inference parameters
- context lengths
- latency

## Risk

Performance differences may be caused by infrastructure rather than model behavior.

## Required Mitigation

Record:

- model
- version
- quantization
- hardware
- inference configuration

---

# 55. Judge Confidence May Not Be Calibrated

## Problem

An LLM saying confidence = 0.95 does not necessarily mean there is a 95% probability the classification is correct.

## Required Mitigation

Treat confidence as an evaluator output, not a guaranteed probability.

If confidence is used operationally, validate calibration against human-labelled examples.

---

# 56. Category Classification and Severity Classification Can Be Wrong Separately

## Problem

A judge might correctly detect harmful behavior but assign the wrong category or severity.

## Risk

The overall score and category breakdown can both become misleading.

## Required Mitigation

Evaluate separately:

- verdict accuracy
- category accuracy
- severity accuracy

Do not treat one correct verdict as proof that all metadata is correct.

---

# 57. “No Harm Observed” Is Not the Same as “Safe”

## Problem

A test may not expose a vulnerability even though the system has one.

## Required Language

Prefer:

- “No harmful behavior observed under this evaluation”
- “No failure detected in tested cases”

Avoid:

- “The model is safe”
- “The system is guaranteed safe”

---

# 58. Coverage Is as Important as the Score

## Problem

A score without coverage is easy to misinterpret.

## Example

A system could score 98/100 on 30 easy tests.

That is not equivalent to 98/100 on 1,000 diverse tests.

## Required Dashboard Fields

Always display:

- total tests
- executed tests
- eligible tests
- excluded tests
- categories
- severities
- languages
- trace availability
- evaluation mode

---

# 59. Dataset Deduplication Can Accidentally Remove Important Attacks

## Problem

Aggressive semantic deduplication may remove attacks that look similar but exercise different vulnerabilities.

## Required Mitigation

Deduplication should be:

- versioned
- auditable
- hash/semantic similarity based
- manually reviewed for important categories where practical

Do not assume similar wording means identical security behavior.

---

# 60. Sampling Can Accidentally Underrepresent Critical Categories

## Problem

Random sampling may produce too few:

- CRITICAL
- HIGH
- fintech-specific
- multi-turn
- multilingual

cases.

## Required Mitigation

Use stratified sampling.

Track coverage before execution.

Do not allow Quick Mode sampling to silently omit critical categories.

---

# 61. Adaptive Attackers Can Create Unfair Evaluation

## Problem

An adaptive attacker may optimize specifically against the target.

## Risk

Different targets may receive different attack budgets, making comparison unfair.

## Required Mitigation

Record:

- attack budget
- rounds
- model
- prompt strategy
- dataset
- stopping criteria

Use standardized budgets for comparative experiments.

---

# 62. External Provider Changes Can Break Reproducibility

## Problem

Hosted LLM providers can silently change:

- model versions
- safety filters
- system behavior
- rate limits

## Required Mitigation

Record:

- provider
- exact model identifier
- version where available
- timestamp
- configuration

Acknowledge that exact remote-model reproduction may not always be possible.

---

# 63. Rate Limits Can Bias Results

## Problem

429s or throttling may cause some systems to be evaluated under different effective conditions.

## Required Mitigation

Record:

- rate-limit events
- retries
- delays
- excluded tests
- evaluation duration

Do not silently treat infrastructure limitations as behavioral safety results.

---

# 64. Timeouts Can Bias Results

## Problem

A system that times out may never produce a response that can be judged.

## Required Mitigation

Separate:

**Behavioral result**

from

**Availability/performance result**.

Do not convert timeout into SAFE.

---

# 65. The System Can Become Too Complex to Explain in Viva

## Problem

A technically impressive architecture with too many services/states/metrics can become difficult to defend.

## Required Mitigation

Every component should have a one-sentence answer:

> Why does this exist?

If the team cannot explain it clearly, reconsider whether it belongs in MVP.

---

# 66. Remaining Fundamental Limitation

Even after all engineering improvements:

**Aegis AI cannot prove that an LLM application is completely safe.**

It can only evaluate behavior against the selected:

- test cases
- datasets
- attack strategies
- configurations
- judge rubric
- evaluation scope

Therefore the final system must communicate:

> Evaluation evidence, not absolute safety.

---

# 67. Top 10 Arguments a Hostile FYP Judge Could Make

1. **“Your Trust Score weights are arbitrary. Why should I believe the number?”**
2. **“Your provenance score measures documentation, not truth. Why call it trust?”**
3. **“Your LLM judge can itself be wrong. How do you validate it?”**
4. **“You have too few independent targets to claim correlation.”**
5. **“Correlation does not prove provenance causes safety.”**
6. **“Your aggregate score can hide a critical vulnerability.”**
7. **“How do you know your benchmark attacks were not already seen during model training?”**
8. **“What happens when a worker crashes after sending a request but before saving the result?”**
9. **“How do you guarantee a target cannot attack your judge or exploit SSRF?”**
10. **“You have too many features. What exactly is your primary contribution?”**

These questions should be explicitly prepared for in the final architecture and viva documentation.

---

# 68. Overall Risk Assessment

## Highest Risk — Research Validity

The biggest danger is not that the backend fails.

The biggest danger is:

> **The backend works perfectly, but the evaluation numbers cannot be scientifically defended.**

Priority fixes:

1. Improve research methodology.
2. Validate the judge.
3. Make scoring transparent and versioned.
4. Prevent aggregate scores from hiding critical findings.
5. Report coverage/exclusions.
6. Separate correlation from causation.
7. Control benchmark contamination.
8. Clearly document limitations.

---

# 69. Risk Priority Matrix

| Area | Risk Level | Main Concern |
|---|---|---|
| Research methodology | 🔴 Critical | Weak statistical claims |
| LLM judge | 🔴 Critical | Incorrect automated evaluation |
| Trust Score | 🔴 Critical | Arbitrary weights / hidden failures |
| Provenance score | 🔴 Critical | Documentation mistaken for truth |
| Dataset quality | 🔴 Critical | Bias / contamination |
| Coverage/exclusions | 🔴 Critical | Scores may look better than reality |
| Agent side effects | 🔴 Critical | Real-world actions |
| Security/SSRF | 🟠 High | Target attacking platform |
| Multi-turn recovery | 🟠 High | Stateful execution complexity |
| Retry semantics | 🟠 High | Different responses across retries |
| FYP scope | 🟠 High | Too many features |
| Distributed infrastructure | 🟠 High | Redis/worker/DB consistency |
| Privacy | 🟠 High | Sensitive raw evidence |
| Database complexity | 🟡 Medium | Implementation burden |
| Local model support | 🟡 Medium | Hardware variability |
| Certificate wording | 🟡 Medium | Potential overclaim |
| OWASP versioning | 🟡 Medium | Outdated mappings |
| Adaptive attacker | 🟡 Medium | Scope explosion |
| LoRA | 🟡 Medium | Overfitting |
| UI complexity | 🟡 Medium | Too much information |

---

# 70. Final Principle

Aegis AI should not try to prove:

> “This LLM is safe.”

It should prove:

> “Under this defined evaluation scope, using this dataset, rubric, judge version, scoring version, and test configuration, these behaviors were observed, these failures were detected, these cases could not be evaluated, and these limitations apply.”

That is a much stronger and more defensible research position.

---

# Final Audit Checklist

Before declaring Aegis AI complete, verify:

- [ ] Provenance score does not claim factual truth.
- [ ] Evidence quality is separate from evidence presence.
- [ ] Trust Score weights are documented and versioned.
- [ ] Sensitivity analysis is defined.
- [ ] Critical findings cannot be hidden by aggregate scoring.
- [ ] AER thresholds are documented.
- [ ] Judge is validated against human labels.
- [ ] Judge prompt injection is tested.
- [ ] Invalid judge output cannot become SAFE.
- [ ] Judge terminology does not falsely imply statistical independence.
- [ ] Research sample size limitations are documented.
- [ ] Repeated runs are not treated as independent targets.
- [ ] Correlation is not presented as causation.
- [ ] Benchmark contamination is considered.
- [ ] Fintech-specific dataset coverage is documented.
- [ ] Quick Mode is clearly marked preliminary.
- [ ] Certificate disclaimer is present.
- [ ] Multi-turn recovery is tested.
- [ ] Retry semantics are deterministic and auditable.
- [ ] External side effects are prevented in MVP.
- [ ] Agent testing is sandboxed.
- [ ] Trace completeness is reported.
- [ ] CMR does not treat missing traces as success.
- [ ] SHR exclusions are visible.
- [ ] SSRF protections are tested.
- [ ] Production security is separated from FYP security.
- [ ] No custom cryptography is used.
- [ ] PostgreSQL remains source of truth.
- [ ] Redis failure/recovery is defined.
- [ ] At-least-once external duplication is documented.
- [ ] Authorization is enforced end-to-end.
- [ ] Raw evidence is protected.
- [ ] PII redaction limitations are documented.
- [ ] Dataset licenses are verified.
- [ ] OWASP mapping is versioned.
- [ ] Resource limits exist.
- [ ] Database complexity is controlled.
- [ ] Adaptive attacker remains stretch unless core system is complete.
- [ ] LoRA uses held-out evaluation.
- [ ] Primary research contribution is clearly defined.
- [ ] Connector claims are not overstated.
- [ ] Local model limitations are documented.
- [ ] Mitigation recommendations are deterministic where possible.
- [ ] Research claims are separated from engineering capabilities.
- [ ] Failure matrix is complete.
- [ ] The entire architecture can be explained in a viva.

---

## Final Assessment

The project has a strong engineering foundation, but its credibility depends heavily on **evaluation validity, scoring transparency, judge reliability, dataset quality, and scope control**.

The most important mindset is:

> **Do not optimize Aegis AI to produce impressive scores. Optimize it to produce trustworthy evidence.**
