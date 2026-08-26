from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from math import exp

from .domain import EvidenceKind, MemoryRecord, MemoryStatus


@dataclass(slots=True)
class RetrievalContext:
    target_ids: set[str]
    tags: set[str]
    now: datetime
    include_sensitive: bool = False


def _age_days(memory: MemoryRecord, now: datetime) -> float:
    reference = memory.event_time or memory.created_at
    if reference.tzinfo is None:
        reference = reference.replace(tzinfo=timezone.utc)
    return max(0.0, (now - reference).total_seconds() / 86400)


def recency_score(memory: MemoryRecord, now: datetime, half_life_days: float = 90.0) -> float:
    if memory.memory_type.value in {"treatment_state", "assessment_result"}:
        return 1.0
    return exp(-0.69314718056 * _age_days(memory, now) / half_life_days)


def retrieval_score(memory: MemoryRecord, ctx: RetrievalContext) -> float:
    if memory.status != MemoryStatus.ACTIVE:
        return 0.0
    if memory.sensitivity == "high" and not ctx.include_sensitive:
        return 0.0

    tag_overlap = len(set(memory.tags) & ctx.tags)
    target_overlap = len(set(memory.target_ids) & ctx.target_ids)
    relevance = min(1.0, 0.2 + 0.2 * tag_overlap + 0.4 * target_overlap)
    provenance_bonus = {
        EvidenceKind.CLINICIAN_VERIFIED: 1.00,
        EvidenceKind.MEASURED: 0.95,
        EvidenceKind.ASSESSED: 0.90,
        EvidenceKind.USER_REPORTED: 0.90,
        EvidenceKind.OBSERVED: 0.75,
        EvidenceKind.AI_INFERRED: 0.55,
    }[memory.source_kind]

    return memory.confidence * provenance_bonus * relevance * recency_score(memory, ctx.now)


def rank_memories(memories: list[MemoryRecord], ctx: RetrievalContext, *, limit: int = 20) -> list[MemoryRecord]:
    ranked = sorted(memories, key=lambda m: retrieval_score(m, ctx), reverse=True)
    return [m for m in ranked if retrieval_score(m, ctx) > 0][:limit]


def mark_contradiction(a: MemoryRecord, b: MemoryRecord) -> None:
    if b.id not in a.contradiction_ids:
        a.contradiction_ids.append(b.id)
    if a.id not in b.contradiction_ids:
        b.contradiction_ids.append(a.id)


@dataclass(slots=True)
class MemoryCorrection:
    memory_id: str
    corrected_payload: dict
    source_id: str


def apply_user_correction(memory: MemoryRecord, correction: MemoryCorrection) -> MemoryRecord:
    """Preserve provenance by superseding old memory instead of rewriting history."""
    if correction.memory_id != memory.id:
        raise ValueError("Correction does not target this memory")
    memory.status = MemoryStatus.SUPERSEDED
    return MemoryRecord(
        id=f"{memory.id}:corrected",
        user_id=memory.user_id,
        memory_type=memory.memory_type,
        payload=correction.corrected_payload,
        source_kind=EvidenceKind.USER_REPORTED,
        source_id=correction.source_id,
        confidence=1.0,
        sensitivity=memory.sensitivity,
        tags=list(memory.tags),
        target_ids=list(memory.target_ids),
        last_confirmed_at=datetime.now(timezone.utc),
    )
