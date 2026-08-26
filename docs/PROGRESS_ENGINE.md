# Progress Engine V1

## Goal

Treatment progress is a clinical feedback signal and a user reward. It must be explainable, bidirectional, target-specific, and resistant to cosmetic manipulation.

## Never show a fake universal percentage

A progress percentage may be shown only when the active target has a configured progress model. The score is an estimate of progress toward the operationalized target, not “percent cured.”

## Evidence dimensions

Per target/protocol, configure weighted dimensions such as:
- symptom change;
- functioning/impairment;
- avoidance/safety behavior change;
- real-world behavior/exposure completion;
- skill acquisition;
- stage milestones;
- recovery speed after setbacks;
- user-defined goal attainment;
- stability/maintenance.

Weights are protocol-specific and versioned.

## Baseline

At treatment start capture enough baseline to distinguish:
- severity;
- frequency;
- impairment;
- avoidance/behavior;
- user-defined success.

No baseline => no confident progress number.

## Example scoring contract

```text
Progress(target) = weighted normalized evidence
confidence = coverage × recency × reliability
```

The UI may display:
- `Progress estimate: 43%`
- `Confidence: moderate`
- `Change this week: -4%`
- `Why: increased work avoidance; symptoms stable; homework incomplete`

The exact scoring formula must be configured and validated per target/protocol rather than assumed globally.

## Bidirectional behavior

Progress can:
- rise;
- remain stable;
- fall;
- become uncertain.

A decline is not automatically “treatment failed.” The engine explains contributing evidence and can trigger review.

## Changes You May Have Missed

A separate achievement detector finds clinically meaningful changes such as:
- user completes a behavior previously avoided;
- anticipatory anxiety remains high but avoidance falls;
- recovery from a setback shortens;
- user needs fewer reassurance loops;
- functioning improves before mood catches up;
- feared predictions repeatedly fail to occur;
- adherence improves;
- user independently uses a learned skill.

Every surfaced achievement includes evidence references and comparison window.

## Progress events

Every score update emits a structured event:
- target_id
- old score/new score
- confidence
- evidence added/removed
- strongest positive driver
- strongest negative driver
- whether review is triggered
- explanation suitable for user

## Guardrails

- Never infer improvement solely from positive language in one conversation.
- Never infer deterioration solely from one bad day.
- Separate symptom improvement from functioning improvement.
- Avoid comparing different instruments as if scores are interchangeable.
- Preserve scale direction and clinically meaningful-change metadata where available.
- Do not use the progress score to shame or pressure the user.

## Treatment reward design

Primary reward hierarchy:
1. capability gained;
2. behavior changed;
3. functioning improved;
4. symptoms changed;
5. stage completed;
6. previously unnoticed achievement surfaced.

Confetti/points may exist only as secondary UX, never as a substitute for meaningful progress.