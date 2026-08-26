from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class SafetyLevel(str, Enum):
    GREEN = "green"
    YELLOW = "yellow"
    ORANGE = "orange"
    RED = "red"


class EvidenceKind(str, Enum):
    USER_REPORTED = "user_reported"
    MEASURED = "measured"
    ASSESSED = "assessed"
    OBSERVED = "observed"
    AI_INFERRED = "ai_inferred"
    CLINICIAN_VERIFIED = "clinician_verified"


class MemoryType(str, Enum):
    FACT = "fact"
    ASSESSMENT_RESULT = "assessment_result"
    OBSERVATION = "observation"
    HYPOTHESIS = "hypothesis"
    TREATMENT_STATE = "treatment_state"
    OUTCOME = "outcome"
    EVENT = "event"
    PREFERENCE = "preference"
    ACHIEVEMENT = "achievement"
    RISK_SIGNAL = "risk_signal"


class MemoryStatus(str, Enum):
    ACTIVE = "active"
    DISPUTED = "disputed"
    SUPERSEDED = "superseded"
    EXPIRED = "expired"
    DELETED = "deleted"


class TargetStatus(str, Enum):
    PROPOSED = "proposed"
    ACTIVE = "active"
    PAUSED = "paused"
    REVIEW_REQUIRED = "review_required"
    COMPLETED = "completed"
    RELAPSED = "relapsed"
    ARCHIVED = "archived"


class HomeworkStatus(str, Enum):
    PROPOSED = "proposed"
    AGREED = "agreed"
    SCHEDULED = "scheduled"
    REMINDED = "reminded"
    ATTEMPTED = "attempted"
    COMPLETED = "completed"
    NOT_COMPLETED = "not_completed"
    REVIEWED = "reviewed"


@dataclass(slots=True)
class EvidenceRef:
    id: str
    kind: EvidenceKind
    source_id: str
    summary: str
    observed_at: datetime = field(default_factory=utcnow)
    reliability: float = 1.0


@dataclass(slots=True)
class Hypothesis:
    id: str
    statement: str
    confidence: float
    supports: list[EvidenceRef] = field(default_factory=list)
    contradicts: list[EvidenceRef] = field(default_factory=list)
    falsification_test: Optional[str] = None
    status: str = "active"
    first_proposed_at: datetime = field(default_factory=utcnow)
    last_reviewed_at: datetime = field(default_factory=utcnow)

    def validate(self) -> None:
        if not 0 <= self.confidence <= 1:
            raise ValueError("Hypothesis confidence must be between 0 and 1")


@dataclass(slots=True)
class MemoryRecord:
    id: str
    user_id: str
    memory_type: MemoryType
    payload: dict[str, Any]
    source_kind: EvidenceKind
    source_id: str
    confidence: float
    sensitivity: str = "normal"
    status: MemoryStatus = MemoryStatus.ACTIVE
    created_at: datetime = field(default_factory=utcnow)
    event_time: Optional[datetime] = None
    last_confirmed_at: Optional[datetime] = None
    contradiction_ids: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    target_ids: list[str] = field(default_factory=list)

    def validate(self) -> None:
        if not 0 <= self.confidence <= 1:
            raise ValueError("Memory confidence must be between 0 and 1")
        if self.source_kind == EvidenceKind.AI_INFERRED and self.memory_type == MemoryType.FACT:
            raise ValueError("AI inference cannot be stored as a FACT")


@dataclass(slots=True)
class ExitCriterion:
    id: str
    description: str
    required: bool = True
    satisfied: bool = False
    evidence_ids: list[str] = field(default_factory=list)


@dataclass(slots=True)
class TreatmentStage:
    id: str
    name: str
    sequence: int
    objectives: list[str]
    exit_criteria: list[ExitCriterion]
    entered_at: datetime = field(default_factory=utcnow)
    completed_at: Optional[datetime] = None

    @property
    def can_complete(self) -> bool:
        return all((not c.required) or c.satisfied for c in self.exit_criteria)


@dataclass(slots=True)
class Homework:
    id: str
    title: str
    rationale: str
    target_id: str
    stage_id: str
    status: HomeworkStatus = HomeworkStatus.PROPOSED
    expected_difficulty: Optional[int] = None
    scheduled_for: Optional[datetime] = None
    pre_prediction: Optional[dict[str, Any]] = None
    actual_outcome: Optional[dict[str, Any]] = None
    barriers: list[str] = field(default_factory=list)
    user_reflection: Optional[str] = None
    clinical_interpretation: Optional[str] = None


@dataclass(slots=True)
class ProgressSnapshot:
    target_id: str
    score: Optional[float]
    confidence: float
    dimensions: dict[str, float]
    positive_driver: Optional[str] = None
    negative_driver: Optional[str] = None
    explanation: Optional[str] = None
    recorded_at: datetime = field(default_factory=utcnow)


@dataclass(slots=True)
class TreatmentTarget:
    id: str
    user_defined_target: str
    operationalized_target: str
    status: TargetStatus
    baseline: dict[str, Any]
    formulation_version: int = 1
    formulation: dict[str, Any] = field(default_factory=dict)
    hypotheses: list[Hypothesis] = field(default_factory=list)
    protocol_id: Optional[str] = None
    stages: list[TreatmentStage] = field(default_factory=list)
    current_stage_index: int = 0
    homework: list[Homework] = field(default_factory=list)
    progress_history: list[ProgressSnapshot] = field(default_factory=list)
    next_best_action: Optional[str] = None
    supervisor_review_required: bool = False

    @property
    def current_stage(self) -> Optional[TreatmentStage]:
        if not self.stages:
            return None
        if self.current_stage_index >= len(self.stages):
            return None
        return self.stages[self.current_stage_index]


@dataclass(slots=True)
class UserTreatmentState:
    user_id: str
    safety_level: SafetyLevel = SafetyLevel.GREEN
    primary_target_id: Optional[str] = None
    targets: dict[str, TreatmentTarget] = field(default_factory=dict)
    updated_at: datetime = field(default_factory=utcnow)

    @property
    def primary_target(self) -> Optional[TreatmentTarget]:
        if self.primary_target_id is None:
            return None
        return self.targets.get(self.primary_target_id)
