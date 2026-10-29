# Cortex, a PM Chief-of-Staff Agent

> A chief-of-staff, an orchestrated swarm of agents that triages a PM task, pulls internal state, and preps a status update plus a story batch, so the team approves instead of assembling from scratch.

_Maïté Nabet · Agentic Loops for PMs Cohort · October 2026_

Repo: https://github.com/MaiteNabet/pm-os-agent

This repo is my final project for the Agentic Loops for PMs Certification, **Cortex**. Each module’s artifact lives in its own folder; this README is the dashboard and the pitch.

---

## Module artifacts

### M1 · The Agent Line
- **Agent-line map**: [`01-agent-line/agent-line-map.md`](01-agent-line/agent-line-map.md)

### M2 · Loop Engineering
- **Loop spec**: [`02-loop-design/loop-spec.md`](02-loop-design/loop-spec.md)

### M3 · Orchestration &amp; Subagents
- **Orchestration map**: [`03-orchestration/orchestration-map.md`](03-orchestration/orchestration-map.md)

### M4 · Choose What Each Agent Step Is Allowed to See
- **Memory &amp; context plan**: [`04-memory-context/memory-and-context.md`](04-memory-context/memory-and-context.md)

### M5 · Bounds &amp; Evals
- **Bounds &amp; evals**: [`05-bounds-evals/bounds-and-evals.md`](05-bounds-evals/bounds-and-evals.md)

### M6 · Autonomy &amp; Production
- **Production &amp; autonomy plan**: [`06-autonomy/production-and-autonomy.md`](06-autonomy/production-and-autonomy.md)
- **Prototype write-up**: [`06-autonomy/prototype.md`](06-autonomy/prototype.md)

---

## Ship plan

### Autonomy dial (per segment)
- Engineering Lead / Operator: Supervised. Owns operational execution, blast-radius control, and triage. Must inspect grounding citations, approve story batches (<=10), and mint single-use write token.
- Product Lead / Requester: Assisted. Triggers briefs and consumes drafted narratives, but holds zero standing credentials to dispatch external tools or bypass review.
- Leadership & cross-functional stakeholders: Shadow. High blast-radius audience. Receives only human-verified, final-state updates in broadcast channels; zero direct agent interaction.

### Trust Ladder rung + eval gate
Current rung: Assisted. Cortex retrieves data, stages story proposals under batch limits, and drafts, but halted at CORTEX_MAX_REVISIONS=2 rather than an HITL approval gate. A human takes the held draft and performs external actions.

Eval gate to climb to Supervised: 100% pass on offline replay suite (replay-happy-path, replay-jailbreak-refusal, replay-recovery-transient, replay-missing-project), >=95% first-pass critic approval on EV-5, and 0 unhandled EV-1 injection near-misses (Turn-1 harness classifier). Window: 20 consecutive runs over 2 weeks with 0 cap blowouts.

Incident record (clean bar): 0 Sev-1 (writes/broadcasts/leaks), 0 Sev-2 (fabricated commitments/dates), <=1 Sev-3 (benign critic revision escalation) per 10 runs.

### Deployment plan
- Runtime: Ephemeral container / serverless function, triggered only by an inbound brief hook. Runs once, stages artifacts, and exits; no idle process.
- Operator / On-call: Primary owner is Lead AI Engineer; secondary on-call engineer as backup. Only these two can set CORTEX_ENABLED=0 or mint write tokens. Requesters/PMs cannot bypass.
- Rollback: Set CORTEX_ENABLED=0. Drop Product Lead dial from Assisted to Shadow. Revert git hash to previous known-good commit and verify with the 4 replay fixtures. Refuse write tokens while leaving read tools in place.
- Monitoring: EV-1 through EV-5 pass rate (alert <95%), revision-cap escalations (<=1 per 10 runs), cost against $0.50/run and $20/day caps, Sev-1/Sev-2 at 0, Sev-3 count.

### ROI metrics + widen-autonomy rule
- Outcome metric: Operator draft acceptance rate (>=95% of staged drafts accepted with zero factual rewrites over 20 runs in 2 weeks).
- Cost-to-serve: Fully-loaded cost per completed run (<$0.05 average per run, capped at $0.50/run and $20.00/day).
- Trust incidents: 0 Sev-1, 0 Sev-2, <=1 Sev-3 per 10 runs.
- Widen-autonomy rule: Engineering Lead dial advances from Assisted to Supervised only after Cortex completes 20 consecutive runs over 2 weeks with 100% replay pass rate, >=95% EV-5 critic approval, 0 unhandled EV-1 near-misses, 0 cap blowouts, and clean Sev-1/Sev-2 record; Product Lead remains Assisted and Leadership remains in Shadow.

### Governance &amp; strategy
- Compliance: Confidential projects (Orbit, Pulsar, and any embargoed docs) and API keys or credentials must never enter prompt context or logs. Customer PII is out of scope and excluded from brief context.
- Safety: Public broadcasts, ticket creation, and scope commitments stay permanently above the line for everyone. Only Lead AI Engineer or Secondary On-Call has authority to toggle CORTEX_ENABLED=0 or mint write tokens. Kill switch instantly halts all hook processing.
- Reliability: Hard-coded harness invariants: max 8 iterations, 90s timeout, max 2 critic redrafts, STUCK after 3 failed pulls, $0.50/run cost ceiling, $20/day total spend cap, story queue <=10. On model API downtime, harness terminates cleanly and quarentines the brief for human triage.
- Next capability / segment & gating eval: Turn-1 harness-level prompt injection classifier. Gated by EV-1: 0 unhandled injection near-misses over 20 consecutive runs in 2 weeks. All user rungs remain locked during this phase.

---

## Build insights

- **Friction point.** Prompt brittleness in the critic loop. The critic repeatedly triggered false-positive rejections on forward-looking phrasing ("expected to enhance user follow-up engagement"), reading aspirational scope as an unapproved GA commitment and blowing through the 2-revision cap.
- **Key learning.** Deterministic harness invariants beat prompt instructions every time. Ephemeral container lifecycles, revision caps, iteration ceilings, and zero ambient write tokens protect the blast radius far more reliably than system prompt obedience.
- **Aha moment.** True safety is architectural, not behavioral. Even when Cortex tripped the revision cap or hit prompt injection payloads, zero unauthorized tool executions, zero ticket creations, and zero Slack broadcasts occurred because write permissions are physically decoupled from drafting.

---

_Certification submission, Agentic Loops for PMs Certification._
