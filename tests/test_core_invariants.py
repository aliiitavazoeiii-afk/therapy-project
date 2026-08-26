from datetime import datetime, timezone

import pytest

from therapy_core.domain import (
    EvidenceKind,
    ExitCriterion,
    MemoryRecord,
    MemoryType,
    SafetyLevel,
    TargetStatus,
    TreatmentStage,
    TreatmentTarget,
    UserTreatmentState,
)
from therapy_core.memory import MemoryCorrection, RetrievalContext, apply_user_correction, retrieval_score
from therapy_core.orchestrator import TreatmentOrchestrator, TreatmentStateError
from therapy_core.progress import DimensionEvidence, ProgressDimensionConfig, ProgressEngine


def build_state() -> UserTreatmentState:
    stage1 = TreatmentStage(
        id="stage-1",
        name="Formulation",
        sequence=1,
        objectives=["Build a shared working formulation"],
        exit_criteria=[ExitCriterion(id="shared", description="User confirms formulation")],
    )
    stage2 = TreatmentStage(
        id="stage-2",
        name="Behavior change",
        sequence=2,
        objectives=["Run first real-world experiment"],
        exit_criteria=[ExitCriterion(id="experiment", description="Experiment reviewed")],
    )
    target = TreatmentTarget(
        id="target-1",
        user_defined_target="I want less social anxiety",
        operationalized_target="Reduce avoidance and improve functioning in evaluative social situations",
        status=TargetStatus.ACTIVE,
        baseline={"avoidance": 8, "distress": 8},
        stages=[stage1, stage2],
        next_best_action="Build formulation",
    )
    return UserTreatmentState(
        user_id="u1",
        primary_target_id=target.id,
        targets={target.id: target},
    )


def test_open_conversation_does_not_mutate_treatment_stage():
    state = build_state()
    orchestrator = TreatmentOrchestrator()
    before = state.primary_target.current_stage.id
    anchor = orchestrator.preserve_treatment_state_during_open_conversation(
        state, conversation_topic="user wants to talk about football"
    )
    assert state.primary_target.current_stage.id == before
    assert anchor["current_stage_id"] == "stage-1"


def test_stage_cannot_advance_without_exit_criteria():
    state = build_state()
    decision = TreatmentOrchestrator().try_advance_stage(state, "target-1")
    assert not decision.advanced
    assert state.primary_target.current_stage.id == "stage-1"


def test_stage_advances_when_exit_criteria_are_met():
    state = build_state()
    state.primary_target.current_stage.exit_criteria[0].satisfied = True
    decision = TreatmentOrchestrator().try_advance_stage(state, "target-1")
    assert decision.advanced
    assert state.primary_target.current_stage.id == "stage-2"


def test_red_safety_state_blocks_normal_treatment_flow():
    state = build_state()
    state.safety_level = SafetyLevel.RED
    with pytest.raises(TreatmentStateError):
        TreatmentOrchestrator().try_advance_stage(state, "target-1")


def test_ai_inference_cannot_be_saved_as_fact():
    memory = MemoryRecord(
        id="m1",
        user_id="u1",
        memory_type=MemoryType.FACT,
        payload={"claim": "perfectionism causes avoidance"},
        source_kind=EvidenceKind.AI_INFERRED,
        source_id="msg-1",
        confidence=0.6,
    )
    with pytest.raises(ValueError):
        memory.validate()


def test_user_correction_supersedes_instead_of_rewriting():
    memory = MemoryRecord(
        id="m2",
        user_id="u1",
        memory_type=MemoryType.FACT,
        payload={"occupation": "architect"},
        source_kind=EvidenceKind.USER_REPORTED,
        source_id="msg-2",
        confidence=1.0,
    )
    corrected = apply_user_correction(
        memory,
        MemoryCorrection(memory_id="m2", corrected_payload={"occupation": "designer"}, source_id="msg-3"),
    )
    assert memory.status.value == "superseded"
    assert corrected.payload["occupation"] == "designer"


def test_retrieval_prefers_target_relevant_memory():
    now = datetime.now(timezone.utc)
    relevant = MemoryRecord(
        id="rel",
        user_id="u1",
        memory_type=MemoryType.OUTCOME,
        payload={"event": "presentation"},
        source_kind=EvidenceKind.USER_REPORTED,
        source_id="msg-4",
        confidence=0.9,
        target_ids=["target-1"],
        tags=["work"],
    )
    irrelevant = MemoryRecord(
        id="irr",
        user_id="u1",
        memory_type=MemoryType.EVENT,
        payload={"event": "movie"},
        source_kind=EvidenceKind.USER_REPORTED,
        source_id="msg-5",
        confidence=0.9,
        tags=["entertainment"],
    )
    ctx = RetrievalContext(target_ids={"target-1"}, tags={"work"}, now=now)
    assert retrieval_score(relevant, ctx) > retrieval_score(irrelevant, ctx)


def test_progress_is_explainable_and_not_percent_cured():
    config = [
        ProgressDimensionConfig("functioning", 0.4),
        ProgressDimensionConfig("avoidance", 0.4),
        ProgressDimensionConfig("milestones", 0.2),
    ]
    evidence = {
        "functioning": DimensionEvidence(0.7, 0.9, "Functioning improved"),
        "avoidance": DimensionEvidence(0.5, 0.8, "Avoidance unchanged"),
        "milestones": DimensionEvidence(0.8, 1.0, "Stage milestones completed"),
    }
    snapshot = ProgressEngine().calculate("target-1", config, evidence)
    assert snapshot.score is not None
    assert 0 <= snapshot.score <= 100
    assert "not percent cured" in snapshot.explanation
