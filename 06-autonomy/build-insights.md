# Build Insights: Cortex PM Chief-of-Staff Agent

> Module 6 · ★ Deliverable 4, what you learned building it
>
> ✅ **What this validates:** you can reflect on what building it taught you, by the end you'll have proven the friction, the learning, and the aha that changes how you'd design your next agent.

## Friction

The hardest friction was not model reasoning, but prompt brittleness in the critic loop. The critic repeatedly rejected innocuous, forward-looking phrasing ("expected to enhance user follow-up engagement"), reading aspirational scope as a public GA commitment. That exhausted the 2-revision cap before a clean HITL approval. Catching prompt injections by redraft exhaustion, rather than a front-door classifier, also wasted iterations and budget.

## Learning

1. Autonomy is a user-segmented contract, not a global slider. A seasoned eng operator needs a supervised dial and citation inspectability. An executive audience stays in shadow until a human has vetted the artifact.
2. Deterministic harness invariants beat prompt instructions. Ephemeral runs, revision caps, iteration bounds, spend ceilings, and zero standing write tokens are what keep the system shippable.
3. Trust is a ladder, not a slide. Higher autonomy requires measurable replay gates over a sustained window, not a demo impression.

## Aha moment

True safety is architectural, not behavioral. When Cortex hit the revision cap or an injection probe, no unauthorized write ran, no ticket was created, and nothing was broadcast. The agent failed safely because write permission is separate from drafting.

## What you'd do differently

Implement a lightweight, deterministic Turn-1 classifier at the harness front door, so an injection is classified before the drafting loop. Downstream critic exhaustion burns tokens and delays the triage.
