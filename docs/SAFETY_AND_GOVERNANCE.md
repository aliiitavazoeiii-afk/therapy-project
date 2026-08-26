# Safety & Clinical Governance V1

## Safety override

Safety is evaluated independently of the conversational model. A sufficiently elevated safety state can interrupt normal therapy, productivity, reminder, and general-assistant flows.

## Safety states

- `GREEN` — no current material risk signal.
- `YELLOW` — concerning signal requiring closer assessment/monitoring.
- `ORANGE` — elevated/ambiguous risk requiring direct assessment and escalation logic.
- `RED` — imminent/acute concern; normal treatment flow is suspended in favor of crisis-oriented response and appropriate real-world help.

Exact detection thresholds, jurisdiction-specific emergency information, and escalation procedures require clinical/legal review before launch.

## Safety principles

- Never rely on sentiment analysis alone.
- Ask direct clarifying safety questions when indicated.
- Do not hide or soften urgent risk for the sake of engagement.
- Do not treat an AI safety score as a diagnosis.
- Safety signals must be source-backed and auditable.
- Avoid over-alerting on ordinary negative emotion; calibration matters.
- High-risk pathways should encourage appropriate human/emergency support rather than attempting autonomous crisis treatment.

## Clinical governance

Before a treatment protocol can be marked `PRODUCTION_APPROVED`, it must have:
- defined target population;
- evidence/source references;
- inclusion/exclusion considerations;
- stage definitions;
- intervention definitions;
- measurement plan;
- exit criteria;
- deterioration/review rules;
- contraindication/caution notes;
- clinical reviewer approval/version/date.

## Assessment governance

Every formal instrument needs metadata:
- name/version;
- construct;
- language/version;
- scoring rules;
- interpretation limits;
- license/copyright status;
- validation population;
- review date.

No home-made scenario item may be presented as validated psychometric evidence until appropriately validated.

## Treatment claims

The product must not market speculative AI inference as diagnosis or guaranteed treatment effect. Clinical/medical claims must match actual evidence and applicable regulation in the target market.

## Medication and medical issues

Medication decisions, prescribing, stopping/changing doses, and medical differential diagnosis require appropriate licensed clinical involvement. The AI may provide general education within approved policy but should not autonomously manage medication.

## Human review hooks

Architecture must support later addition of:
- licensed clinician dashboard;
- case review queue;
- supervisor overrides;
- escalation notes;
- audit logs;
- protocol approval/versioning.

## Data and privacy requirements

At minimum:
- least-privilege access;
- encryption in transit and at rest where appropriate;
- server-side secret management;
- audit logging for sensitive access;
- user-visible memory controls;
- export/delete capability;
- separation of identity and highly sensitive clinical data where practical;
- explicit consent for integrations (calendar, notifications, etc.);
- retention policies by data class.

Production deployment should use an isolated environment rather than sharing infrastructure with unrelated experimental services.