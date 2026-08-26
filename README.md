# Therapy Project

A treatment-first AI mental-health platform designed around longitudinal memory, measurement-based care, explicit treatment state, proactive follow-up, and a general personal assistant layer.

## Core product promise

The user is not entering a generic chatbot. They are entering a structured change process. Conversation remains natural and open-ended, but the system must never lose the treatment target, current treatment stage, active hypotheses, homework, outcome trend, or safety state.

## Non-negotiable principles

1. **Present-state first, treatment-state always preserved.** The therapist responds to what the user needs now, while the Treatment Orchestrator preserves the long-term plan.
2. **No invented certainty.** User facts, assessment results, observations, and AI hypotheses are stored separately with source, timestamp, and confidence.
3. **Progress is measured, not decorated.** Treatment progress can rise or fall and must be explainable from symptoms, functioning, avoidance/behavior, protocol milestones, and real-world outcomes.
4. **Memory is source-backed.** Important memories retain provenance and confidence; contradictions are reconciled rather than silently overwritten.
5. **Treatment has explicit stages and exit criteria.** Conversation cannot accidentally advance or abandon the protocol.
6. **Homework is part of treatment.** Assignments are tracked from assignment through attempt, completion, outcome, and clinical interpretation.
7. **Safety overrides everything.** High-risk states interrupt normal therapy/productivity flows and invoke the safety pathway.
8. **Best intelligence at high-leverage moments.** Initial assessment interpretation, first formulation, major treatment decisions, difficult sessions, and supervision use the strongest available model; routine extraction/check-ins may use cheaper models.
9. **The system is not a diagnosis machine.** Diagnostic labels require appropriate clinical governance. Early outputs are working formulations and hypotheses unless validated otherwise.
10. **User agency and data control.** The user can inspect/correct/delete remembered information; sensitive data must be designed for privacy from day one.

## Architecture

```text
Clients (Web / Mobile)
        |
        v
API / Auth / Consent
        |
        +--> Safety Engine --------------------+
        |                                      |
        +--> Therapist Agent                   |
        |       |                              |
        |       v                              |
        |   Context Builder <---- Memory Engine|
        |       |                  |           |
        |       v                  v           |
        |   Model Router       Psychological   |
        |                      Model            |
        |                                      |
        +--> Treatment Orchestrator <----------+
        |       |                              |
        |       +--> Protocol Engine           |
        |       +--> Homework Engine           |
        |       +--> Progress Engine           |
        |       +--> Outcome Engine            |
        |                                      |
        +--> Supervisor Agent -----------------+
        |
        +--> Daily Life / Events / Reminders
        +--> General Assistant
```

## Repository map

- `docs/PRODUCT_SPEC.md` — product behavior agreed so far.
- `docs/ONBOARDING_AND_ASSESSMENT.md` — treatment-first first experience.
- `docs/TREATMENT_ENGINE.md` — state machine, stages, exit criteria, homework and review.
- `docs/MEMORY_ENGINE.md` — source-backed longitudinal memory architecture.
- `docs/PROGRESS_ENGINE.md` — explainable treatment progress model.
- `docs/AI_ROUTING.md` — model routing and cost/quality policy.
- `docs/SAFETY_AND_GOVERNANCE.md` — safety boundary and clinical governance.
- `src/therapy_core/domain.py` — typed domain model.
- `src/therapy_core/orchestrator.py` — deterministic treatment control plane.
- `src/therapy_core/memory.py` — memory scoring/reconciliation primitives.
- `src/therapy_core/progress.py` — explainable progress calculation primitives.
- `tests/` — invariant tests.

## Status

Phase 0: Core architecture and treatment logic. No production diagnosis, no clinical claims, no OpenAI key required yet.

Next phase: deploy backend/database on an isolated server, connect the AI gateway, then implement onboarding and first-session UX against this core.