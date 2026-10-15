# Loop Spec: Cortex PM Chief-of-Staff Agent

> Module 2 · Loop Engineering, ★ Deliverable 2
>
> ✅ **What this validates:** the agent knows when to run and when to stop, by the end you'll have proven a one-page Loop Spec with a trigger, a definition of "done," and explicit stop conditions.
>
> Your one-page blueprint for how the work you handed to the agent (M1) actually *runs*.
> An agent is just a prompt that fires itself, this spec says when it fires, what "done" means, and what it needs to do the job. Living document; refine as the course progresses.

## 1. Trigger & loop type

**Chosen type:** hook

Cortex is a chief of staff responding to inbound prompts from me or my product lead. Because its permissions are bounded to reading and drafting, it fires only when an actual request arrives, rather than autonomously creating drafts nobody asked for.

**Ruled out:** cron-only, because it cannot handle an ad-hoc request mid-week. A continuous heartbeat, because running all the time spends tokens when nothing has changed. A goal loop, because Cortex does not own the commitments or the posting needed to prove it is finished.

**Dedupe:** message ID. Cortex checks the incoming message ID against IDs it has already processed. The same ID a second time skips the run, so it does not write a second draft.

## 2. Goal / definition of done

Cortex is done when it has pulled verified state, written the draft update, and staged the capped story batch. The packet is waiting for a human. Cortex does not post, set tone or a commitment, or choose an escalation. Staging that packet has no external blast radius. The human's review is a later step, not part of this run.

## 3. Stop conditions

| Condition | What it looks like | What happens |
|---|---|---|
| **Success** | A draft exists, it is flagged as waiting for review, and the story batch is queued at or under the cap. | Cortex stops. Nothing is posted. The human review happens outside this run. A critic pass is not required. |
| **Stuck / give up** | `get_project` or `get_activity` has failed 3 times, or 8 iterations finish with no queued draft. | Stop and write an error log. Do not invent the missing data. Three retries absorb a blip. Eight iterations stop a tool loop that never produces a draft. |
| **Escalate to human** | The request would make Cortex commit to a date or other promise, exceed the story cap, include confidential or embargoed material, or choose what to escalate. | Stop and hand the run over. Do not draft the forbidden commitment. Routine HITL items and critic rejections are not this exit. |

## 4. State

A run holds only this request: the message ID, the project named in it, that project's pulls, and the draft being built. Cortex may read the governed record (roadmap, past updates, accepted decision log, team norms, project state) and does not append unapproved drafts or dismissed flags to it. Another project's confidential items stay out of this draft. Processed message IDs are kept so the same ID skips a second run.

## 5. The five things a loop can lean on

`state` is always-on. `connectors` only if you already have one wired (e.g. a Jira key or Google MCP), otherwise just note it as a plan. `skills`, `subagents`, `work tree` scale with autonomy; "not needed yet, because…" is a valid answer.

| Component | For Cortex |
|---|---|
| **Work tree** (isolated workspace per run, a git worktree) | Not needed yet. Cortex reads fixtures and holds one draft. It does not commit, edit the repo, or push a branch. Message-ID dedupe already stops a second run. |
| **Skills** (reusable capabilities) | Not needed yet. The six tools already are the reads and the capped proposal. A skill would only rename them until a multi-step procedure is reused. |
| **Plugins / connectors** (tools & access, optional if you don't have one yet) | Not wired. The build reads local fixtures, not a live Jira or GitHub account. Plan: a read-only Jira or GitHub connector later. This step does not connect one. |
| **Subagents** (independent check when the loop can't grade itself) | Not needed yet. The human reviews the queued packet, and a critic pass is not required to stop. A specialist subagent waits until a check cannot be handed to that human review. |
| **State tracking** | This request plus the governed record, as in §4. Processed message IDs persist for dedupe. Unapproved drafts do not. |

> Context plan (M4) and the hand-off to bounds & evals (M5) come in later modules, you'll add them to their own deliverables then, not here.

## Link to live loop

_[path to your agent in `00-build/`]_
