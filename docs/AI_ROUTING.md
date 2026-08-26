# AI Routing & Context Policy V1

## Principle

Use the strongest intelligence at high-leverage clinical moments. Use cheaper models for routine deterministic/extraction work. The user should not experience a quality cliff.

## High-leverage tier
Use the strongest available reasoning model for:
- initial assessment synthesis;
- first psychological model;
- first deep session/formulation;
- treatment plan selection;
- major formulation revisions;
- complex/high-uncertainty sessions;
- stage-change decisions requiring synthesis;
- supervisor reviews after important sessions;
- difficult contradiction resolution;
- clinically sensitive reasoning after safety gating.

## Mid tier
Use a capable general model for:
- ordinary therapeutic conversation when no complex formulation work is needed;
- general-assistant questions;
- event preparation/debrief;
- coaching around active homework;
- routine weekly reviews.

## Low-cost tier
Use efficient models for:
- memory candidate extraction;
- tagging/classification;
- summarization;
- reminder wording;
- check-in normalization;
- structured field extraction;
- duplicate detection candidates;
- non-sensitive analytics.

Deterministic code should replace LLM calls where rules are sufficient.

## Context packet

Never send the entire lifetime transcript by default.

Therapy context packet:
1. system safety policy;
2. current safety state;
3. current treatment target/state/stage;
4. active formulation + hypothesis ledger;
5. active homework;
6. relevant high-confidence memories;
7. recent significant events;
8. relevant outcome/progress trend;
9. recent conversation window;
10. current user message.

General-assistant context packet is smaller and should not inject unrelated sensitive clinical memories.

## Context selection rules

- treatment state is mandatory in therapy mode;
- safety state is always available to the safety layer;
- retrieve only relevant personal context;
- hypotheses remain labeled as hypotheses;
- disputed memory is excluded unless resolving it;
- token budget is explicit;
- prefer structured state over repeated raw transcript;
- sensitive data is minimized.

## Cost telemetry

Log per model call:
- user/session/task type;
- model/tier;
- input/output/cached/reasoning token counts when available;
- latency;
- estimated cost;
- route reason;
- quality/supervisor signal;
- context size and memory count.

Admin metrics:
- cost/user/day and month;
- cost per treatment session;
- cost by agent;
- P50/P95/P99 user cost;
- percent of calls by tier;
- quality failures by tier;
- token savings from retrieval/consolidation.

## Quality fallback

If a cheaper route produces uncertainty, inconsistency, or a clinically material conflict, escalate to the stronger tier rather than forcing a low-quality answer.