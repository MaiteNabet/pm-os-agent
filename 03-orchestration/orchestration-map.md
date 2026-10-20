# Orchestration Map: Cortex PM Chief-of-Staff Agent

> Module 3 · Orchestration & Subagents, ★ Deliverable 3
>
> ✅ **What this validates:** nothing advances unchecked, by the end you'll have proven a justified topology, a roster, and a validator with a defined fail action.
>
> Builds on your M2 Loop Spec. Only split one agent into a team when there's a real reason, coordination has a cost.

## 1. Why split? (or why not)

Cortex splits into exactly two agents, and only because an independent validator applies. The drafter inherits its own blind spots, so a separate checker reads the finished draft against the raw pull before the packet reaches the PM. It does not post, and it does not replace human review.

Separation of concerns does not apply: reading and drafting are one workflow, and posting, dates, tone, and escalation already sit outside Cortex. Parallelism does not apply: the pull must finish before the draft, and the fixture reads are too fast for a second agent to save time. Context-window pressure does not apply: one request is a few thousand tokens. The failure being defended against is a blind spot, not a full window.

The team stays at two. No research agent and no parallel reader.

## 2. Topology

**Pattern:** single plus one subagent

```
[Inbound PM task]
  → [Cortex: pulls this project's data, drafts the update + capped stories]
  → [Validator: the four checks, own context]
       fail → back to Cortex (max 2 redrafts) → then escalate to the PM
       pass → [PM review checkpoint] → queued, nothing posted
```

## 3. Roster

| Agent / subagent | Responsibility | Runs which Loop Spec |
|---|---|---|
| Cortex | Pulls this project's data and drafts the update plus the capped story batch. | Module 2 loop spec |
| Validator | On demand, checks the draft against the four rules. No trigger and no definition of done of its own. | None. A check inside Cortex's run. |

## 4. Communication & hand-offs

In-process function call in the same run. Cortex passes the draft and the source pull. The validator returns pass or fail plus the reasons. No MCP, no agent-to-agent protocol, and no draft file between them.

## 5. The validator

**What the critic checks:**

1. Entity and metric grounding. Only the requested project, and only PR or issue IDs from the pull. Every number traces to that source. No invented figures.
2. Zero forbidden commitments. No promises, dates, public GA targets, or SLA commitments.
3. Boundary and embargo protection. No confidential, embargoed, or out-of-scope items, and no claim that anything was posted or sent.
4. Story batch cap. The batch is within the cap, or the draft explicitly flags that it hits or exceeds it, and it stays a staged draft.

Tone and audience are not checks. Those stay with the PM.

**Fail action:** Revise. The failure reason goes back to Cortex. After 2 redrafts, escalate to the PM. That is at most 3 drafts and 3 critic checks. A first-pass typo does not interrupt the PM and does not disappear. A date, an embargo leak, or a hallucination that survives the cap escalates.

**Pass action:** Queue for the PM. A pass does not post and does not make a commitment.

## 6. State: shared vs isolated

Shared: the draft and the source pull for this request only. Isolated: Cortex's chat history and tool chatter, and the validator's reasoning. Cortex receives only the verdict and the failure reasons. Nothing is appended to the governed record.

## 7. Cost & latency budget

A clean pass adds one critic call after the draft, then the packet is queued for the PM. The worst case is two redrafts: three drafts and three critic checks, then escalate. The GA-date run hit that ceiling at about $0.0045, under the $0.50 spend cap. The PM waits for those calls. The loop does not continue past the cap.
