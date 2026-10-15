"""Cortex, a minimal, explicit agent loop you (and your coding agent) can read end
to end. This is the agent you ship: your PM chief-of-staff. You build it by
directing your coding agent (Claude Code / Cursor / Codex) to shape this file. You
never have to hand-write it.

Every bound the course talks about is visible right here in code, not buried in a
framework: the max-iteration counter, the cost cap, the revision cap, the
stop/escalate conditions, the auto-queue cap, and the absence of any publish tool.

Usage (ask your coding agent to run these for you, or run them yourself):
    python agent.py                # runs the happy-path task (weekly status update)
    python agent.py missing-data   # the stuck/escalate case
    python agent.py jailbreak       # the prompt-injection refusal case

Every run ends by showing the drafted status update in a FINAL STATUS UPDATE block
(or LAST DRAFT, held, if a bound trips), and saves it to run-output/. That file is
always a draft held for a human, it is never posted, there is no publish tool.

Requires OPENAI_API_KEY in your environment (see .env.example). Model and bounds
are read from env so you can tune them, that tuning is your M5 deliverable.

The loop is deliberately transparent (hand-written tool-calling on the openai
client) so a grader can see the machinery. Keep the bounds explicit if you rework it.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

from openai import OpenAI

import tools
from critic import review
from prompts import CORTEX_SYSTEM

try:  # load .env if python-dotenv is installed; harmless if it isn't
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# --- Bounds (your M5 deliverable: tune these and justify them) ----------------
MODEL = os.environ.get("CORTEX_MODEL", "gpt-4o-mini")
MAX_ITERATIONS = int(os.environ.get("CORTEX_MAX_ITERATIONS", "8"))
MAX_REVISIONS = int(os.environ.get("CORTEX_MAX_REVISIONS", "2"))  # kept as a bound; a critic fail is a comment, not an exit
COST_CAP_USD = float(os.environ.get("CORTEX_COST_CAP_USD", "0.50"))
MAX_QUEUE_ITEMS = int(os.environ.get("CORTEX_MAX_QUEUE_ITEMS", "10"))
# Rough $ per 1M tokens for your chosen model, set to match its pricing.
PRICE_IN = float(os.environ.get("CORTEX_PRICE_IN_PER_M", "0.15"))
PRICE_OUT = float(os.environ.get("CORTEX_PRICE_OUT_PER_M", "0.60"))

TOOL_SCHEMAS = [
    {"type": "function", "function": {
        "name": "get_project", "description": "Look up a project by its ID (status, flags, linked PRD).",
        "parameters": {"type": "object", "properties": {
            "project_id": {"type": "string"}}, "required": ["project_id"]}}},
    {"type": "function", "function": {
        "name": "get_activity",
        "description": "Pull recent engineering activity for a project (merged PRs, open issues, Sev-1s).",
        "parameters": {"type": "object", "properties": {
            "project_id": {"type": "string"}}, "required": ["project_id"]}}},
    {"type": "function", "function": {
        "name": "search_past_updates",
        "description": "Search previous status updates and decisions for tone and precedent.",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string"}}, "required": []}}},
    {"type": "function", "function": {
        "name": "get_roadmap",
        "description": "Return the roadmap. Some items are flagged confidential/embargoed.",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string"}}, "required": []}}},
    {"type": "function", "function": {
        "name": "get_norms", "description": "Return the team norms / PM playbook the agent must follow.",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string"}}, "required": []}}},
    {"type": "function", "function": {
        "name": "propose_stories",
        "description": "Queue a set of backlog stories for human approval (creates nothing; rejected above the item cap).",
        "parameters": {"type": "object", "properties": {
            "project_id": {"type": "string"},
            "stories": {"type": "array", "items": {"type": "string"}},
            "reason": {"type": "string"}}, "required": ["project_id", "stories"]}}},
]


class Bounds:
    """Tracks spend and trips the cost cap. This is enforced OUTSIDE the model."""

    def __init__(self):
        self.cost = 0.0

    def add(self, usage) -> None:
        self.cost += (usage.prompt_tokens * PRICE_IN
                      + usage.completion_tokens * PRICE_OUT) / 1_000_000

    def over_cap(self) -> bool:
        return self.cost >= COST_CAP_USD


OUTPUT_DIR = Path(__file__).parent / "run-output"
PULL_TOOLS = ("get_project", "get_activity")
PULL_FAIL_CAP = 3

_EXIT_TITLES = {
    "queued": "FINAL STATUS UPDATE (draft, queued for review, NOT posted)",
    "stuck": "STUCK (stopped and logged, NOT posted, missing data was not invented)",
    "escalated": "LAST DRAFT (held, NOT posted, escalated to a human)",
}


def banner(text: str) -> None:
    print(f"\n{'=' * 64}\n{text}\n{'=' * 64}")


def finish_kind(text: str) -> str:
    """Map Cortex's closing line to a loop exit. Critic verdict is not an input."""
    if re.search(r"(?m)^\s*ESCALATE\b", text):
        return "escalated"
    if re.search(r"(?m)^\s*STUCK\b", text):
        return "stuck"
    if re.search(r"(?m)^\s*DONE\b", text) or "queued for your review" in text.lower():
        return "queued"
    return "continue"


def emit_deliverable(which: str, draft: str, *, outcome: str,
                     reason: str, cost: float) -> None:
    """Surface AND persist Cortex's drafted status update so it can't get lost in
    the scroll-back. This is still a DRAFT held for human review, never a post,
    there is no publish tool, and a stuck or escalated run is held on purpose.

    Runs on every exit. `outcome` is queued (success), stuck, or escalated.
    """
    banner(_EXIT_TITLES.get(outcome, _EXIT_TITLES["escalated"]))
    if draft.strip():
        print(draft.rstrip())
    else:
        print("(Cortex stopped before it produced a draft, nothing to show.)")
    if outcome != "queued":
        print(f"\nWhy it stopped: {reason}")

    if draft.strip():
        OUTPUT_DIR.mkdir(exist_ok=True)
        out = OUTPUT_DIR / f"status-update-{which}.md"
        out.write_text(
            f"<!-- Cortex draft, {outcome}; NOT posted. Run cost ~ ${cost:.4f}. -->\n"
            f"<!-- {reason} -->\n\n{draft.rstrip()}\n", encoding="utf-8")
        print(f"\nSaved draft -> {out.relative_to(Path(__file__).parent)}  "
              f"(for your review, nothing was posted)")


def run(which: str = "happy") -> None:
    client = OpenAI()
    bounds = Bounds()
    task = tools.get_task(which)
    if "error" in task:
        print(task)
        return

    banner(f"CORTEX RUN, fixture: task-{which}  (auto-queue cap {MAX_QUEUE_ITEMS} items)")
    print(task["body"])

    messages = [
        {"role": "system", "content": CORTEX_SYSTEM},
        {"role": "user", "content": f"PM task brief:\n\n{task['body']}"},
    ]
    source_log: list[str] = [task["body"]]
    last_draft = ""
    pull_failures = 0

    for step in range(1, MAX_ITERATIONS + 1):
        if bounds.over_cap():
            reason = f"cost cap ${COST_CAP_USD} hit at ${bounds.cost:.4f}"
            banner(f"BOUND TRIPPED, {reason}. Halting and escalating to a human.")
            emit_deliverable(which, last_draft, outcome="escalated",
                             reason=reason, cost=bounds.cost)
            return

        resp = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOL_SCHEMAS)
        bounds.add(resp.usage)
        msg = resp.choices[0].message

        if msg.tool_calls:
            messages.append(msg)
            for call in msg.tool_calls:
                fn = call.function.name
                args = json.loads(call.function.arguments or "{}")
                result = tools.TOOLS[fn](**args)
                source_log.append(f"{fn}({args}) -> {json.dumps(result)}")
                print(f"\n[step {step}] TOOL {fn}({args})")
                print(f"          -> {json.dumps(result)[:300]}")
                messages.append({"role": "tool", "tool_call_id": call.id,
                                 "content": json.dumps(result)})
                if isinstance(result, dict) and result.get("error") == "batch_exceeds_queue_cap":
                    reason = (f"story batch {result.get('count')} exceeds the cap of "
                              f"{result.get('cap_items')}")
                    banner(f"ESCALATE, {reason}. Handing the run to a human. "
                           f"Run cost ≈ ${bounds.cost:.4f}")
                    emit_deliverable(which, last_draft, outcome="escalated",
                                     reason=reason, cost=bounds.cost)
                    return
                if fn in PULL_TOOLS and isinstance(result, dict) and "error" in result:
                    pull_failures += 1
                    if pull_failures >= PULL_FAIL_CAP:
                        reason = (f"{fn} failed {pull_failures} times "
                                  f"({result.get('error')})")
                        banner(f"STUCK, {reason}. Stopping and logging. "
                               f"Missing data was not invented. "
                               f"Run cost ≈ ${bounds.cost:.4f}")
                        emit_deliverable(which, last_draft, outcome="stuck",
                                         reason=reason, cost=bounds.cost)
                        return
            continue

        # No tool calls => Cortex produced a proposed output.
        proposed = msg.content or ""
        last_draft = proposed
        print(f"\n[step {step}] PROPOSED OUTPUT:\n{proposed}")
        kind = finish_kind(proposed)

        if kind == "continue":
            messages.append(msg)
            messages.append({"role": "user", "content":
                             "Finish with exactly one of DONE (draft labelled "
                             "\"queued for your review\"), STUCK (data could not be "
                             "pulled; do not invent it), or ESCALATE (only a date or "
                             "other promise, a batch over the cap, confidential "
                             "material, or choosing what to escalate)."})
            continue

        if kind == "queued":
            banner("CRITIC, comment only (a fail does not block this stop)")
            verdict = review(client, MODEL, proposed, "\n".join(source_log))
            bounds.cost += (verdict["_usage"]["prompt"] * PRICE_IN
                            + verdict["_usage"]["completion"] * PRICE_OUT) / 1_000_000
            print(json.dumps({k: v for k, v in verdict.items() if k != "_usage"}, indent=2))
            banner(f"HITL CHECKPOINT, status update + any proposed stories queued for "
                   f"your review. Nothing posted, no commitments made. "
                   f"Critic said {verdict.get('verdict')}, and that does not change "
                   f"this stop. Run cost ≈ ${bounds.cost:.4f}")
            emit_deliverable(which, proposed, outcome="queued",
                             reason="draft queued for review", cost=bounds.cost)
            return

        reason = proposed.strip().splitlines()[-1] if proposed.strip() else kind
        if kind == "stuck":
            banner(f"STUCK, stopping and logging. Missing data was not invented. "
                   f"Run cost ≈ ${bounds.cost:.4f}")
        else:
            banner(f"ESCALATE, handing the run to a human. "
                   f"Run cost ≈ ${bounds.cost:.4f}")
        emit_deliverable(which, proposed, outcome=kind,
                         reason=reason, cost=bounds.cost)
        return

    banner(f"STUCK, {MAX_ITERATIONS} iterations finished with no queued draft. "
           f"Stopping and logging. Run cost ≈ ${bounds.cost:.4f}")
    emit_deliverable(which, last_draft, outcome="stuck",
                     reason=f"{MAX_ITERATIONS} iterations with no queued draft",
                     cost=bounds.cost)


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "happy")
