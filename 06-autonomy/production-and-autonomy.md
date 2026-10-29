# Production & Autonomy: Cortex PM Chief-of-Staff Agent

> Module 6 · ★ Deliverable 5, how you'd ship it, govern it, and widen trust over time
>
> ✅ **What this validates:** you can ship it, govern it, and widen trust deliberately, by the end you'll have proven an autonomy dial, a Trust Ladder rung with its eval gate, and a governance plan.

## Autonomy Dial by segment

Autonomy is a product decision per user, not one global setting. The dial changes which below-the-line actions still pause for that person. Tone, choosing an escalation, and posting stay above the line for everyone.

| Segment | Desired autonomy | Why |
|---|---|---|
| **Engineering Lead / Operator** | Supervised | Owns operational execution, blast-radius control, and triage. Must explicitly inspect grounding citations, approve story batches (≤ 10), and mint the single-use write token before any artifact leaves local staging. |
| **Product Lead / Requester** | Assisted | Triggers briefs and consumes drafted narratives for alignment, but has zero standing credentials to dispatch external tools or bypass engineering review. All staged proposals must route through the operator checkpoint. |
| **Leadership and cross-functional stakeholders** | Shadow | High blast-radius audience. Receives only human-verified, final-state updates in broadcast channels, with zero direct agent interaction. Cortex never broadcasts an unvetted output to leadership. |

## Trust Ladder

- **Current rung:** Assisted. Cortex is built to stop for a human, and in the latest runs it behaved as assisted. Neither the happy path nor the jailbreak exited at a green HITL approval. Both halted on `CORTEX_MAX_REVISIONS=2`. Cortex retrieves data, stages story proposals under the batch limit, and drafts. A human still takes the held draft, resolves critic false positives or scope-boundary issues, and performs every external action.
- **Eval gate to reach the next rung (Supervised):** 100% pass on the offline replay suite (`replay-happy-path`, `replay-jailbreak-refusal`, `replay-recovery-transient`, `replay-missing-project`), plus at least 95% first-pass critic approval on EV-5, and 0 unhandled prompt-injection near-misses on EV-1. EV-1 requires a pre-execution classifier in the harness that halts on Turn 1. The window is 20 consecutive production or staging runs over 2 weeks, with no iteration-cap or revision-cap blowout.
- **Incident record that counts as clean for that window:** 0 out-of-bounds writes, unapproved channel broadcasts, or credential leaks (Sev-1). 0 fabricated launch dates, commitments, or cross-project scope assignments (Sev-2). At most 1 benign critic revision escalation per 10 runs (Sev-3), with every escalation logged and held in local staging (`run-output/`).

## Deployment plan

- **Runtime:** Ephemeral container / serverless function, triggered only by an inbound brief (the hook). It runs once, writes artifacts to staging, and exits. No idle process.
- **Operator / on-call owner:** Primary owner is the Engineering Lead / System Operator (Lead AI Engineer). Backup is the Secondary On-Call Engineer. Only those two can set `CORTEX_ENABLED=0` or mint the single-use write token. Requesters and PMs cannot bypass or unfreeze the system.
- **Rollback:** Set `CORTEX_ENABLED=0` so new briefs are rejected. Drop the product lead from Assisted back to Shadow. Revert the git hash and prompt template to the previous known-good commit and verify with the four deterministic replay fixtures (`replay-happy-path`, `replay-jailbreak-refusal`, `replay-recovery-transient`, `replay-missing-project`). Refuse to mint the single-use write token while leaving the read tools and `propose_stories` in place.
- **Monitoring:** EV-1 through EV-5 pass rate on production traces, alert under 95%. Revision-cap and stuck-loop escalations, target at most 1 per 10 runs. Run cost against $0.50 per run and $20 per day. Sev-1 and Sev-2 at zero, plus Sev-3 count.

## ROI metrics (beyond adoption & tokens)

- **Outcome metric:** Operator draft acceptance rate. Target is at least 95% of staged drafts accepted by the operator with zero factual rewrites across 20 consecutive production runs over 2 weeks. Captured via a binary yes/no operator sign-off logged on each HITL packet review.
- **Cost-to-serve metric:** Fully-loaded cost per completed run. Target is under $0.05 average per run, with a hard harness cap at $0.50 per run and a daily spend ceiling at $20.00. Captured directly from the harness execution telemetry line (`Run cost ≈ $X.XXXX`).
- **Trust incidents metric:** Out-of-bounds safety violation rate. Target is 0 Sev-1 (broadcast, write, or leak), 0 Sev-2 (fabricated commitments or dates), and at most 1 Sev-3 (critic revision exhaustion) per 10 runs. Captured from the local staging review audit log and run exit banners in `run-output/`.

## Widen-autonomy decision rule

The Engineering Lead dial advances from Assisted to Supervised only after Cortex completes 20 consecutive staging or production runs over a 2-week observation window with a 100% replay fixture pass rate, at least 95% EV-5 first-pass critic approval, 0 unhandled EV-1 injection near-misses, 0 cap blowouts, and a completely clean Sev-1/Sev-2 incident record, while Product Lead remains Assisted and Leadership remains in Shadow.

## Governance & forward strategy

- **Compliance:** Confidential project records (Orbit, Pulsar, and any context tagged embargoed/confidential) and API keys or credentials must never be passed into prompt context or logged to disk. Customer PII is out of scope and strictly excluded from status brief context.
- **Safety:** Human review stays mandatory above the line for all broadcast posts, scope expansions, and ticket creation. Only the Lead AI Engineer or Secondary On-Call Engineer possesses authority to toggle `CORTEX_ENABLED=0` or mint the single-use write token. The kill switch instantly rejects all incoming brief hooks.
- **Reliability:** Immutable harness limits remain hard-coded: maximum 8 iterations, 90-second wall-clock ceiling, 2 critic redrafts, $0.50 maximum cost per run, $20.00 daily spend ceiling, story batch queue capped at ≤ 10, and transition to `STUCK` after 3 failed tool retrievals. On model API outage or failure, the harness terminates cleanly and quarantines the raw brief for operator triage.
- **Next capability / segment & gating eval:** Implement a deterministic Turn-1 prompt-injection classifier in the pre-execution harness prior to tool invocation. This capability is gated by **EV-1**: achieving a 0 unhandled injection near-miss rate across 20 consecutive production runs over 2 weeks. No segments advance rungs during this phase; posting remains permanently above the line.
