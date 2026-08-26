# Onboarding & Assessment V1

## Goal

The onboarding is not a decorative personality quiz. It produces a structured baseline that lets the first conversation begin with meaningful personalization while avoiding false certainty.

## Sequence

### 1. Consent & expectations
Explain:
- what the system does and does not do;
- that assessment is used to personalize care;
- that AI interpretations are working hypotheses;
- privacy/data controls;
- emergency limitations.

### 2. Baseline assessment battery
The final production battery must be selected/reviewed for psychometric validity, licensing, target population, language validation, and clinical governance before public launch.

Construct domains to cover:
- broad personality traits;
- current depression/low-mood symptoms;
- anxiety/distress;
- sleep;
- functioning/impairment;
- avoidance/behavioral patterns;
- emotion regulation/coping;
- interpersonal functioning where relevant;
- motivation/reward/activation;
- current life context and stressors;
- treatment history and prior response;
- goals and desired outcomes.

### Scenario-based UX
Scenario questions may make assessment engaging, but they may only infer constructs for which the item set has been designed and validated. Projective “choose a nail/room/person and we reveal your unconscious personality” interpretations are not allowed as clinical evidence.

Scenario items can be used as:
- UX wrappers around validated constructs;
- exploratory prompts;
- low-confidence hypotheses requiring later confirmation.

### 3. Initial Psychological Model
Strong-model interpretation converts assessment into separate objects:
- FACT: directly reported user information;
- ASSESSMENT_RESULT: scored result from a named instrument/domain;
- OBSERVATION: behavior observed in interaction;
- HYPOTHESIS: model inference that can be confirmed/rejected;
- PREFERENCE: interaction preference;
- GOAL: desired change;
- RISK_SIGNAL: safety-relevant signal.

Every item stores source, timestamp, confidence, and status.

### 4. “Map of You” feedback
Show a small number of high-value, non-diagnostic insights. Each insight asks for confirmation:
- accurate;
- partly accurate;
- inaccurate;
- edit/explain.

Do not overwhelm the user with trait scores. Use scores internally where useful and provide interpretable feedback.

### 5. First treatment target
Prompt concept:

> If this platform could meaningfully improve one part of your life first, what would you want to be different?

Then gather enough detail to define:
- target behavior/state;
- contexts/triggers;
- impact;
- baseline frequency/intensity;
- previous attempts;
- user-defined success condition.

### 6. First Deep Session
The first substantive conversation uses:
- assessment summary;
- confirmed/rejected initial insights;
- target definition;
- relevant personal context;
- recent state;
- safety state.

The therapist should demonstrate understanding naturally, not announce a percentage of “how much we know you.”

### 7. Understanding Verification
At the end of the first formulation:
- show a concise plain-language reflection;
- ask “How accurately did I understand you?” (0–10);
- ask “What did I get wrong or miss?”;
- corrections immediately update model confidence/provenance.

## First-session output

When appropriate, the system should leave the user with:
- primary treatment target;
- baseline measurements;
- initial formulation;
- a small set of active hypotheses;
- first stage/objective;
- one minimal effective next action;
- next review/check-in timing;
- perceived-understanding score.

## Model policy

Initial assessment synthesis, first formulation, and first major treatment plan use the strongest available model/reasoning tier. Cost optimization begins after the high-leverage onboarding window.