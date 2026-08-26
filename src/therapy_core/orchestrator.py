from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .domain import SafetyLevel, TargetStatus, TreatmentTarget, UserTreatmentState


class TreatmentStateError(RuntimeError):
    pass


@dataclass(slots=True)
class StageDecision:
    advanced: bool
    reason: str
    new_stage_id: Optional[str] = None


class TreatmentOrchestrator:
    """Deterministic control plane for longitudinal treatment state.

    The conversational model may suggest actions, but it cannot bypass
    these invariants.
    """

    def assert_normal_flow_allowed(self, state: UserTreatmentState) -> None:
        if state.safety_level == SafetyLevel.RED:
            raise TreatmentStateError("Normal treatment flow blocked by RED safety state")

    def activate_target(self, state: UserTreatmentState, target_id: str, *, make_primary: bool = True) -> None:
        self.assert_normal_flow_allowed(state)
        target = state.targets.get(target_id)
        if target is None:
            raise TreatmentStateError(f"Unknown target: {target_id}")
        target.status = TargetStatus.ACTIVE
        if make_primary:
            state.primary_target_id = target_id

    def request_review(self, target: TreatmentTarget, reason: str) -> None:
        target.status = TargetStatus.REVIEW_REQUIRED
        target.supervisor_review_required = True
        target.next_best_action = f"Supervisor review: {reason}"

    def try_advance_stage(
        self,
        state: UserTreatmentState,
        target_id: str,
        *,
        unresolved_safety_blocker: bool = False,
        required_measurements_available: bool = True,
        supervisor_override: bool = False,
        override_reason: Optional[str] = None,
    ) -> StageDecision:
        self.assert_normal_flow_allowed(state)
        target = state.targets.get(target_id)
        if target is None:
            raise TreatmentStateError(f"Unknown target: {target_id}")
        if target.status not in {TargetStatus.ACTIVE, TargetStatus.REVIEW_REQUIRED}:
            return StageDecision(False, f"Target is not active: {target.status.value}")
        stage = target.current_stage
        if stage is None:
            return StageDecision(False, "No active stage")
        if unresolved_safety_blocker:
            return StageDecision(False, "Unresolved safety blocker")
        if not required_measurements_available and not supervisor_override:
            return StageDecision(False, "Required measurements unavailable")
        if not stage.can_complete and not supervisor_override:
            missing = [c.description for c in stage.exit_criteria if c.required and not c.satisfied]
            return StageDecision(False, "Exit criteria not met: " + "; ".join(missing))
        if supervisor_override and not override_reason:
            return StageDecision(False, "Supervisor override requires a documented reason")

        from .domain import utcnow

        stage.completed_at = utcnow()
        next_index = target.current_stage_index + 1
        if next_index >= len(target.stages):
            target.status = TargetStatus.COMPLETED
            target.next_best_action = "Create consolidation/maintenance plan"
            return StageDecision(True, "Final stage completed", None)

        target.current_stage_index = next_index
        target.status = TargetStatus.ACTIVE
        target.supervisor_review_required = False
        next_stage = target.current_stage
        target.next_best_action = next_stage.objectives[0] if next_stage and next_stage.objectives else None
        return StageDecision(True, "Stage advanced", next_stage.id if next_stage else None)

    def preserve_treatment_state_during_open_conversation(
        self,
        state: UserTreatmentState,
        *,
        conversation_topic: str,
    ) -> dict[str, str | None]:
        """Return mandatory anchors for the context builder.

        This intentionally does not mutate treatment state. It exists to enforce
        the product rule that an open-ended conversation never silently changes
        or erases the treatment trajectory.
        """
        target = state.primary_target
        return {
            "conversation_topic": conversation_topic,
            "primary_target_id": target.id if target else None,
            "current_stage_id": target.current_stage.id if target and target.current_stage else None,
            "next_best_action": target.next_best_action if target else None,
            "safety_level": state.safety_level.value,
        }
