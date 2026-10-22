# Context Engineering & Memory: Cortex PM Chief-of-Staff Agent

> Module 4 · Context Engineering & Memory
>
> ✅ **What this validates:** the agent reasons on the right, safe inputs, by the end you'll have proven a context budget, per-source retrieve-vs-long-context decisions, and a memory map with risk mitigations.
>
> 🗂️ **How the lab maps to this file:** In **Part A** (before the lecture) you don't edit this file, you rough-draft on scratch, focused on the per-source calls in **section 2** plus a quick remember/forget + "how it rots" sketch. In **Part B** (after the lecture) you complete **all five sections**; the Lab Guide's guided builder writes this file for you to copy in and commit.

## 1. Context budget

Each loop iteration cannot fit every source. What stays is ordered. When the window is tight, drop from the bottom.

1. **Task brief** (`get_task`), long-context. The assignment for this run.
2. **Norms** (`get_norms`), long-context, reloaded fresh each run. The standing bans.
3. **This project's activity** (`get_activity`), retrieve. This week's PRs and the activation figure.
4. **This project's roadmap slice** (`get_roadmap`), retrieve. The shareable section only.
5. **Matching past updates** (`search_past_updates`), retrieve. Format and historical precedent.

The assignment (`get_task`) and standing boundaries (`get_norms`) must never be dropped, because dropping them leads directly to constraint violations or leaked embargoes. For the data, fresh working-memory facts for the current run (`get_activity`) strictly outrank historical precedent (`search_past_updates`), which is the largest corpus and the primary vector for stale-fact hallucination. The roadmap slice sits between them: shareable scope for the named project, with Orbit and Pulsar kept off the desk.

## 2. Retrieve vs. long-context: per source

Retrieve narrows a large or changing corpus to the relevant slice. Long-context includes a bounded set the loop can reason over whole.

| Source | Size / volatility | Decision | Why |
|---|---|---|---|
| Task brief (`get_task`) | One static document. Bounded. Does not grow. | Long-context | Deciding factor: **size**. The brief defines the entire assignment for this run. Treating it as a retrieval corpus adds machinery and recall risk: a missing line can drop the story batch or the hold-for-review instruction. The full document has to be on the desk. |
| Norms (`get_norms`) | Compact playbook. Bounded. Must stay current. | Long-context, reloaded fresh each run | Deciding factor: **size**, plus the risk of missing a guardrail. Tone, embargo, and milestone rules operate as one set. A search can fail to retrieve an applicable constraint. The model and the critic need the complete playbook. |
| Activity (`get_activity`) | Grows every week. Unbounded over time. | Retrieve | Deciding factor: **volatility**, with citation/audit close behind. Only the active project's slice belongs on the desk. The validator has to trace each metric and PR to an explicit pull. |
| Roadmap (`get_roadmap`) | Medium. Slow-changing. Carries confidential flags. | Retrieve | Deciding factor: **citation/audit** (and isolation). The whole roadmap would put Orbit and Pulsar in context. The shareable slice isolates them and lets the critic audit the exact section cited. |
| Past updates (`search_past_updates`) | Unbounded. A new week is added every week. | Retrieve | Deciding factor: **size**, with citation/audit close behind. The archive has no ceiling, so a full dump wastes tokens and adds latency. A matched pull keeps past metrics as precedent, not as this week's news, and keeps unrelated embargo notes out of context. |

## 3. Retrieval quality plan

Long-context sources (`get_task`, `get_norms`) are not in this grid. Each retrieved source has the moves its failure mode demands. Caching is off on all three.

| Source | Routing | Document grading | Reranking | Self-verification | Caching |
|---|---|---|---|---|---|
| Activity (`get_activity`) | Yes | Yes | No | Yes | No |
| Roadmap (`get_roadmap`) | Yes | Yes | No | Yes | No |
| Past updates (`search_past_updates`) | Yes | Yes | Yes | Yes | No |

**Activity.** Routing sends this week's progress to `get_activity` instead of the historical archive. Document grading keeps only rows for the active project and the current window. Self-verification checks every PR id (`#820`, `#823`) and the metric (43% versus the 41% prior) against that pull. Reranking stays off: a handful of rows does not need a ranker. Caching stays off: activity is volatile, and a cache can serve 41% in the week that is 43%.

**Roadmap.** Routing fetches only the section for the project named in the task. Document grading drops confidential, embargoed, or internal-only entries, including Orbit and the newly embargoed Pulsar, before drafting. Self-verification checks the draft against that graded slice so an embargoed name or an unconfirmed GA date does not slip through. Reranking stays off: one project's section is structured and small. Caching stays off: an embargo can change, as Pulsar did in this pull, and a cached roadmap would miss it.

**Past updates.** Routing sends historical precedent, formatting, and prior-metric questions to `search_past_updates`, and keeps current-progress queries on `get_activity`. Document grading keeps hits for the queried project and discards decision-log items that carry confidential notes or embargoed projects (Orbit, Pulsar). Reranking surfaces the most recent precedent (39% to 41%) above older weeks (37% to 39%) so the archive cannot invert time. Self-verification checks that historical numbers stay prior-week baselines and that no embargoed name appears. Caching stays off: the latest precedent changes every week, and a cached search can anchor the draft to an outdated baseline.

## 4. Memory map (your PM brain)

This matches the loop line: a run holds this request only, unapproved drafts are not appended to the governed record, and processed message IDs persist so the same request is not run twice.

| Memory type | What Cortex stores | Scope / TTL |
|---|---|---|
| **Working** (in-loop) | Current message ID, active project identifier, raw retrieved tool outputs (`get_activity`, the project roadmap slice), the working draft, critic rejection reasons, and run metrics. | This run only. It dies when the run ends. Unapproved or escalated drafts are purged immediately. |
| **Episodic** (past runs) | Processed inbound message IDs (dedupe) and the governed, read-only archive (`past-updates.json`, `decision-log.json`). | Bounded per-project history. Message IDs live 30 days, then drop. Unapproved or rejected drafts are never appended. Only human-approved records persist. |
| **Semantic** (durable facts/prefs) | Standing PM norms (`team-norms.md`), project metadata (`projects.json`), and roadmap status (`roadmap.md`). | Reloaded fresh each run. Updated by a deliberate human commit, not inferred or rewritten in-session by Cortex. |
| **Shared** (across agents) | The packet passed from drafter to critic: the generated draft and the retrieved evidence slice. | The active review cycle inside this run. Discarded when validation ends. The critic does not see the drafter's chat. |

## 5. Memory risks & mitigations

Stop each risk at write time. Read and write scope stays on the Module 1 line: Cortex does not post, and it does not choose what to escalate. The 30-day message-ID TTL is the retention bound to carry into Module 5.

| Risk | Where it bites | Mitigation |
|---|---|---|
| Drift | Internalized norms or project boundaries drift away from the repo, or an in-session summary invents a policy. | Semantic memory is read-only and loaded fresh from disk every run (`team-norms.md`, `projects.json`, `roadmap.md`). Cortex cannot write or update its own policies. Changes happen only by a deliberate human commit. |
| Poisoning | A rejected or unapproved draft, an adversarial injection in a task, or confidential embargo notes enter long-term memory and get cited as precedent. | Cortex has no write permission on the episodic archive. Only human-approved updates are committed there. Shared memory shows the critic only the packet and the retrieved evidence slice, so the drafter's conversation cannot contaminate the check. |
| Staleness | An old metric (prior week's 41% activation) or a cached roadmap (missing the new Pulsar embargo) is treated as this week's truth. | No cache on `get_activity`, `get_roadmap`, or `search_past_updates`. Fresh activity outranks the archive in the context budget. Past updates are reranked so the latest precedent wins. Message IDs expire after 30 days. |
| PII / retention | Confidential codenames (Orbit, Pulsar), contributor identities, or other sensitive internal data persist in memory, scratchpads, or logs after the task. | Document grading discards embargoed sections before drafting. Working memory and the shared critic packet are purged when the run ends. Message IDs are kept only for dedupe and drop after 30 days. |
