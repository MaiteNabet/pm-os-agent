# Agent Line Map: Cortex PM Chief-of-Staff Agent

> Module 1 · The Agent Line
>
> ✅ **What this validates:** every risky action has a clear owner, by the end you'll have proven an above/below-the-line map with HITL checkpoints, scored on reversibility, blast radius, and measurability.

## The workflow, decision by decision

List every discrete decision or action in your agent's workflow, then score each one and place it **above** the line (a human owns it) or **below** (the agent owns it). Borderline calls get an HITL checkpoint.

| Decision / action | Reversibility (H/M/L) | Blast radius (H/M/L) | Measurability (H/M/L) | Above / Below | HITL? |
|---|---|---|---|---|---|
| Pull project state and activity | H | L | H | Below | no |
| Decide relevant context | M | H | L | HITL | yes |
| Draft the update | H | L | H | Below | no |
| Decide tone and commitment level | L | H | L | Above | no |
| Flag at-risk or escalation | H | L | M | HITL | yes |
| Choose what to escalate | L | H | L | Above | no |
| Propose a story batch (capped) | H | L | M | HITL | yes |
| Post an update, or approve a company-wide one | L | H | M | Above | no |

## Agent anatomy (sketch)

- **Model:** `gpt-4o-mini` by default for the routine below-the-line work (pulling state, drafting a disposable update), because those steps are read-only or fully disposable and a run stays cheap. Step up to a frontier model (Claude 3.5 Sonnet or GPT-4o) only for HITL packets: the relevant-context cut, risk flags, and the story batch, where the proposal a human must approve needs a higher signal-to-noise ratio. Never use a frontier model for the above-the-line calls (tone and commitments, choosing escalations, posting). Capability is not permission.
- **Tools:** `get_project`, `get_activity`, `search_past_updates`, `get_roadmap`, `get_norms`, and `propose_stories` as a capped queue for human approval. No post tool and no ticket create, close, or merge. Those actions stay impossible because the tools are absent.
- **Memory:** The governed record only: roadmap, past updates, accepted decision log, team norms, and project state. Cortex reads that ground truth and does not append to it. This run's draft, trace, and any story batch nobody accepted are purged.
- **Loop:** _placeholder, defined in M2 loop-spec.md_
- **Bounds:** _placeholder, defined in M5 bounds-and-evals.md_
- **Evals:** _placeholder, defined in M5 bounds-and-evals.md_

## The golden rule, applied

Pull project state and activity sits below the line because it is highly reversible, has a low blast radius, and is highly measurable, deciding factor: blast radius. A wrong pull changes nothing outside the run, and you can discard it before anything downstream uses it.

Decide relevant context sits at a HITL checkpoint because it is moderately reversible, has a high blast radius, and has low measurability, deciding factor: blast radius. Choosing what matters defines the narrative, and stakeholders cannot challenge a risk they never see, so a human approves the boundary before it is used.

Draft the update sits below the line because it is highly reversible, has a low blast radius, and is highly measurable, deciding factor: reversibility. A human can check the draft and change it before it is sent.

Decide tone and commitment level sits above the line because it is difficult to reverse, has a high blast radius, and has low measurability, deciding factor: blast radius. A status color, a date, or a "we will" is a promise that sets other people moving, and a human has to gauge the pitch for the audience.

Flag at-risk or escalation sits at a HITL checkpoint because it is highly reversible, has a low blast radius, and is only moderately measurable, deciding factor: measurability. A false alarm can be dismissed in seconds, but a risk that was never flagged leaves nothing to check, so a human reviews the flag before it counts.

Choose what to escalate sits above the line because it is difficult to reverse, has a high blast radius, and has low measurability, deciding factor: blast radius. An escalation spends leadership attention and trust, and both a wrong escalation and a buried one are costly, so the choice stays with a human.

Propose a story batch (capped) sits at a HITL checkpoint because it is highly reversible, has a low blast radius, and is only moderately measurable, deciding factor: measurability. The cap keeps it a draft that commits no hours, but a cap check cannot tell you these were the right stories, so a human approves the batch before any story is accepted.

Post an update, or approve a company-wide one, sits above the line because it is difficult to reverse, has a high blast radius, and is only moderately measurable, deciding factor: blast radius. Once it is sent it is the company's position, a retraction is public, and the authority to broadcast stays with a human.

## Hardest call

The hardest call was flag at-risk or escalation, settled by measurability. The first instinct was pure below: a false alarm is cheap to dismiss, and an undetected risk is catastrophic, so flagging looked like a harmless trigger with high reversibility and near-zero blast radius. The golden rule needs all three axes to clear before an action sits fully below the line. A false flag is easy to audit, but a missed flag is invisible. There is no trace left to measure after the fact. That medium measurability pulled it out of pure autonomy. As a HITL checkpoint, Cortex can surface candidate risks, and the absence of a flag is not treated as proof that everything is fine.
