# Memory Engine V1

## Objective

Memory is not a transcript archive. It is a source-backed longitudinal model of the person that lets the system remain coherent over months or years without repeatedly sending the full conversation history to the LLM.

## Memory classes

### FACT
Directly reported or verified facts: occupation, relationship status, important people, schedules, goals, preferences.

### ASSESSMENT_RESULT
Named scale/domain results with instrument/version, date, score, interpretation bounds, and validation metadata.

### OBSERVATION
Behavior observed in interactions. Must not be silently promoted to fact.

### HYPOTHESIS
Clinical/personality inference with confidence and evidence ledger.

### TREATMENT_STATE
Target, formulation version, protocol, stage, objectives, homework, next action.

### OUTCOME
What happened after an intervention/experiment and whether it appeared helpful, unhelpful, mixed, or unclear.

### EVENT
Important life event with date/time, expected stress, actual outcome, and treatment relevance.

### PREFERENCE
Communication style, reminder tolerance, preferred timing, disliked interventions, accessibility needs.

### ACHIEVEMENT
Meaningful change the user may not have noticed. Must reference evidence.

### RISK_SIGNAL
Safety-relevant information with stricter access/audit policy.

## Required metadata

Every memory stores:
- id
- user_id
- type
- content/structured payload
- source_type
- source_id (message, assessment, event, clinician/supervisor, system measurement)
- created_at
- event_time if different
- last_confirmed_at
- confidence
- sensitivity
- status: active / disputed / superseded / expired / deleted
- contradiction links
- tags/entities
- treatment target linkage where relevant

## Source hierarchy

Reliability is contextual, but provenance must remain visible. Direct user statements are not automatically objective truth; AI hypotheses are never equal to direct statements.

The system must distinguish:
`USER_REPORTED` / `MEASURED` / `ASSESSED` / `OBSERVED` / `AI_INFERRED` / `CLINICIAN_VERIFIED`.

## Write pipeline

```text
Conversation/Event/Assessment
 -> Candidate extraction
 -> Sensitivity classification
 -> Type classification
 -> Duplicate detection
 -> Contradiction detection
 -> Clinical relevance scoring
 -> Confidence assignment/update
 -> Store or discard
 -> Link to target/hypothesis/event
```

Not every conversation detail deserves long-term memory.

## Retrieval pipeline

```text
Current user message + current treatment state
 -> intent/context analysis
 -> mandatory context (safety + treatment state)
 -> relevant entity/time/target retrieval
 -> recency + relevance + confidence ranking
 -> contradiction-aware filtering
 -> token budget
 -> context packet
 -> LLM
```

Treatment state is mandatory context during therapy interactions. Long raw history is not.

## Memory precision safeguards

1. The model must not claim “you told me X” unless the supplied memory is source-backed.
2. Low-confidence hypotheses are phrased as tentative.
3. Disputed/superseded memories are excluded unless relevant to resolving a contradiction.
4. Sensitive memories have explicit access rules.
5. Important recalled claims can internally carry source IDs for audit/debugging.
6. The user can inspect, correct, dispute, or delete memories.

## Contradiction handling

Never overwrite silently.

Example:
- old: “I avoid all presentations.”
- new: “I have presented three times this month.”

Possible interpretation:
- behavior changed over time;
- earlier statement was contextual;
- memory was inaccurate.

Create a contradiction/revision task, preserve timestamps, and update only after context-aware reconciliation.

## Consolidation

Repeated episodic memories are periodically consolidated into a higher-level model while retaining raw references.

Example:
- many work-event memories
- repeated pre-event anxiety
- actual outcomes often better than predicted

Consolidated pattern:
`anticipatory threat overestimation in evaluative work contexts`, with supporting event IDs and confidence.

Consolidation is reversible and evidence-linked.

## Decay and confirmation

Not all memories remain valid forever.
- stable facts: slow/no decay unless contradicted;
- preferences: moderate decay;
- current stressors: faster decay;
- treatment state: explicit versioning, no probabilistic decay;
- hypotheses: confidence changes by evidence;
- risk signals: follow clinical/safety retention policy.

## Psychological Model

The user-level model is generated from structured memories, not free-text summaries alone.

Domains:
- identity/context
- goals/values
- strengths/protective factors
- trait tendencies
- emotional patterns
- coping/avoidance
- interpersonal patterns
- motivation/reward
- work/academic context
- important relationships
- recurring triggers
- treatment response history
- communication/preferences
- active hypotheses

## Achievement detection

The system periodically asks:
- What is easier now that used to be hard?
- What behavior occurs sooner/more often?
- Has recovery after setbacks shortened?
- Are feared outcomes disproven more often?
- Did the user stop mentioning a previously dominant blocker?
- Has function improved even if subjective mood has not?

Achievements must be evidence-backed and can be surfaced as “Changes you may have missed.”

## Product KPI

**Memory Precision** = proportion of surfaced/referenced memories judged correct and relevant by audit/user feedback.

Target should be high enough that memory increases trust rather than creating uncanny or false recollections.