# Product Specification — Core Behavior

## Product identity

Therapy Project is a treatment-first personal AI. Therapy is the primary axis. Daily planning, work support, reminders, research, and general AI assistance exist to improve adherence, functioning, and contextual understanding — not to dilute the treatment mission.

## What the user comes for

The default assumption is not “I want to chat.” The user has arrived because something in life is not working well enough and they want meaningful change. The product therefore starts with structured assessment and personalization rather than an empty chat box.

## First-session objective

The first experience must create two outcomes:

1. **Perceived understanding:** the user feels the system has understood meaningful parts of who they are and how they operate.
2. **Treatment traction:** a concrete initial target, working formulation, baseline, and next action exist by the end of the first deep interaction when clinically appropriate.

The first assessment interpretation and initial formulation are high-leverage operations and should use the strongest available reasoning model.

## Two simultaneous tracks

### A. Present State
What does the user need right now?
- distress regulation
- being heard and accurately reflected
- decision support
- event preparation/debrief
- practical help
- ordinary questions

### B. Treatment State
What are we treating over time?
- primary/secondary targets
- current working formulation
- active hypotheses
- treatment protocol
- current stage
- stage exit criteria
- homework
- outcome trend
- next clinical action

Present State may change many times per day. Treatment State must remain persistent.

## Experience principles

### No generic AI reset
The user should not repeatedly re-explain their occupation, goals, key relationships, active stressors, treatment target, prior interventions, or current stage.

### Natural conversation, deterministic control plane
The conversational model can be flexible. Treatment advancement, homework state, risk state, measurement schedules, and stage completion are controlled by structured state and rules.

### Insight must be falsifiable
The platform can surface patterns, but it must phrase uncertain causal interpretations as hypotheses and actively gather evidence for and against them.

### Progress itself is the reward
Avoid childish gamification as the primary reinforcement mechanism. Reward is:
- visible symptom/function change;
- completed real-world experiments;
- stage advancement;
- capabilities gained;
- achievements the user did not notice;
- evidence that a previously difficult pattern is changing.

### Progress can decrease
No fake upward-only bar. If functioning, avoidance, symptoms, adherence, or stability worsen, progress can decline. The system explains why.

## Personal companion layer

With explicit user consent, treatment context may incorporate:
- daily schedule;
- upcoming stressful events;
- goals and projects;
- work/business context;
- reminders;
- past event outcomes.

Example lifecycle:
1. User records a difficult meeting tomorrow.
2. System flags it as a clinically relevant event.
3. Pre-event check-in measures prediction/anxiety and recalls relevant patterns.
4. AI gives context-specific work + psychological preparation.
5. Post-event debrief compares prediction with outcome.
6. Result updates the formulation, memory, and progress evidence.

## General AI behavior

The user may ask ordinary questions unrelated to therapy. The system should answer as a capable general assistant, but use personal context only when relevant and beneficial. It should not pathologize every ordinary problem.

## Success metrics

Core product metrics:
- First-session Perceived Understanding Score
- Day-1 / Day-7 / Day-30 retention
- treatment-target improvement
- functional improvement
- homework adherence
- stage completion rate
- memory precision / correction rate
- clinically relevant contradiction rate
- cost per active user
- escalation/safety pathway correctness

## Hard product invariant

> The user may talk about anything for as long as they want; the system must never forget what change process it is responsible for.