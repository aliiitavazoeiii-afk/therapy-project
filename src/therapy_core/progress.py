from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .domain import ProgressSnapshot


@dataclass(slots=True, frozen=True)
class ProgressDimensionConfig:
    name: str
    weight: float


@dataclass(slots=True, frozen=True)
class DimensionEvidence:
    normalized_progress: float
    confidence: float
    explanation: str

    def validate(self) -> None:
        if not 0 <= self.normalized_progress <= 1:
            raise ValueError("normalized_progress must be between 0 and 1")
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")


class ProgressEngine:
    def calculate(
        self,
        target_id: str,
        config: list[ProgressDimensionConfig],
        evidence: Mapping[str, DimensionEvidence],
    ) -> ProgressSnapshot:
        if not config:
            return ProgressSnapshot(target_id=target_id, score=None, confidence=0.0, dimensions={})

        total_weight = sum(c.weight for c in config)
        if total_weight <= 0:
            raise ValueError("Progress weights must sum to a positive value")

        weighted_score = 0.0
        weighted_confidence = 0.0
        used_weight = 0.0
        dimensions: dict[str, float] = {}
        positive: tuple[float, str] | None = None
        negative: tuple[float, str] | None = None

        for item in config:
            ev = evidence.get(item.name)
            if ev is None:
                continue
            ev.validate()
            normalized_weight = item.weight / total_weight
            contribution = normalized_weight * ev.normalized_progress
            weighted_score += contribution
            weighted_confidence += normalized_weight * ev.confidence
            used_weight += normalized_weight
            dimensions[item.name] = round(ev.normalized_progress * 100, 1)

            signed_from_midpoint = ev.normalized_progress - 0.5
            if positive is None or signed_from_midpoint > positive[0]:
                positive = (signed_from_midpoint, ev.explanation)
            if negative is None or signed_from_midpoint < negative[0]:
                negative = (signed_from_midpoint, ev.explanation)

        if used_weight == 0:
            return ProgressSnapshot(target_id=target_id, score=None, confidence=0.0, dimensions={})

        # Do not pretend missing dimensions are known. Renormalize observed evidence,
        # then reduce confidence according to coverage.
        score = weighted_score / used_weight
        confidence = (weighted_confidence / used_weight) * used_weight
        return ProgressSnapshot(
            target_id=target_id,
            score=round(score * 100, 1),
            confidence=round(confidence, 3),
            dimensions=dimensions,
            positive_driver=positive[1] if positive and positive[0] > 0 else None,
            negative_driver=negative[1] if negative and negative[0] < 0 else None,
            explanation="Progress is an estimate toward this treatment target, not percent cured.",
        )
