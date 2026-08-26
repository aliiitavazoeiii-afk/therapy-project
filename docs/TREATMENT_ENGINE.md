# Treatment Engine V1

## Purpose

The Treatment Engine prevents the AI from becoming a reactive question-answer bot that forgets the treatment trajectory.

## Core invariant

Conversation may wander. Treatment state may not.

## Treatment state object

Each active treatment target stores:

- `target_id`
- user-defined target
- operationalized target
- baseline
- status: proposed / active / paused / completed / relapsed / archived
- working formulation
- active hypotheses
- selected protocol or treatment strategy
- current stage
- stage objectives
- stage entry criteria
- stage exit criteria
- current homework
- measurements due
- progress evidence
- supervisor review status
- next best clinical action

## State machine

```text
ASSESSMENT
  -> TARGET_DEFINITION
  -> FORMULATION
  -> PLAN_SELECTION
  -> ACTIVE_STAGE_1
  -> ACTIVE_STAGE_N
  -> CONSOLIDATION
  -> MAINTENANCE
  -> COMPLETED

Any state can branch to:
  -> REVIEW_REQUIRED
  -> PAUSED
  -> SAFETY_OVERRIDE
```

## Stage advancement

The conversational model cannot independently mark a stage complete.

A stage advances only when:
1. mandatory objectives are satisfied;
2. exit criteria are met or a supervisor explicitly records a justified override;
3. required measurements are available or marked unavailable with reason;
4. unresolved safety blockers are absent;
5. next stage is defined.

## Exit criteria

Exit criteria must be explicit and protocol-specific. Examples of criterion types:
- knowledge/skill demonstrated;
- behavior attempted/completed;
- exposure hierarchy milestone;
- symptom threshold/change;
- functioning improvement;
- adherence threshold;
- repeated evidence across a defined period;
- user-reported readiness;
- supervisor approval.

Never hard-code the same criteria across disorders or protocols.

## Present-state interruption

A difficult day does not erase treatment state.

Flow:
1. detect current need;
2. if safety risk: Safety Override;
3. otherwise address immediate distress/problem;
4. extract clinically relevant information;
5. decide whether treatment state changes;
6. when appropriate, reconnect to the active stage/homework.

## Working formulation

A formulation describes maintaining mechanisms and relevant context. It is versioned.

Example structure:
- target/problem;
- triggers;
- thoughts/interpretations;
- emotions/physiology;
- behaviors/avoidance/safety behaviors;
- short-term consequences;
- long-term maintaining consequences;
- protective factors;
- contextual factors;
- unresolved hypotheses.

## Hypothesis ledger

Every causal or mechanistic inference is a hypothesis, not a fact.

Fields:
- statement;
- confidence;
- supporting evidence IDs;
- contradicting evidence IDs;
- first proposed / last reviewed;
- status: active / weakened / rejected / supported;
- falsification test / next observation.

The system should prefer hypotheses that are clinically useful and testable.

## Homework Engine

Homework is a first-class treatment object.

Lifecycle:
`PROPOSED -> AGREED -> SCHEDULED -> REMINDED -> ATTEMPTED -> COMPLETED / NOT_COMPLETED -> REVIEWED`

Each assignment stores:
- therapeutic rationale;
- linkage to target/stage/hypothesis;
- smallest useful action;
- expected difficulty;
- schedule/event trigger;
- pre-task prediction/state if relevant;
- actual outcome;
- post-task state;
- barriers;
- user reflection;
- clinical interpretation.

Homework should use the **minimum effective dose**: do not create unnecessary burden merely to increase engagement.

## Real-world experiment lifecycle

For exposure/behavioral experiments when appropriate:
1. define feared/predicted outcome;
2. record predicted probability/intensity;
3. define behavior and safety behaviors to reduce;
4. execute in real life;
5. record actual outcome;
6. compare prediction vs outcome;
7. update hypothesis confidence;
8. update progress evidence;
9. decide repeat/step-up/reformulate.

## Treatment review triggers

Trigger supervisor/review when:
- outcome worsens across repeated measurements;
- stage is stalled;
- homework repeatedly fails;
- user reports treatment mismatch;
- formulation has accumulating contradictory evidence;
- major life event changes context;
- risk state changes;
- therapist repeatedly deviates from plan;
- user requests a new target;
- progress is unclear for a configured period.

## Multi-target treatment

Users may have multiple problems. Do not run every protocol simultaneously.

Each target has priority and state:
- primary active target;
- secondary monitored targets;
- deferred targets.

Priority considers user preference, impairment, safety, tractability, dependencies, and current context.

## Completion and relapse

Completion requires documented outcome and maintenance plan. A later recurrence creates a relapse/recurrence event linked to the prior target; the system should recall previously effective/ineffective interventions instead of restarting from zero.