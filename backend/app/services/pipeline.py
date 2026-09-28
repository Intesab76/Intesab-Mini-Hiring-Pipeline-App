STAGES = [
    "Applied",
    "Screening",
    "Interview",
    "Offer",
    "Hired"
]

REJECTED = "Rejected"  # Should not be added inside the Stages List as it has not be inside the pipeline.


def get_next_stage(current_stage: str) -> str:
    if current_stage == REJECTED:
        raise ValueError("Rejected candidates cannot move to another stage.")

    if current_stage == "Hired":
        raise ValueError("Hired candidates cannot move to another stage.")

    if current_stage not in STAGES:
        raise ValueError("Invalid candidate stage.")

    current_index = STAGES.index(current_stage)

    return STAGES[current_index + 1]


def can_reject(current_stage: str) -> bool:
    return current_stage not in [REJECTED, "Hired"]


from datetime import datetime, timezone

def get_days_in_stage(changed_at: datetime) -> int:
    now = datetime.now(timezone.utc)

    if changed_at.tzinfo is None:
        changed_at = changed_at.replace(tzinfo=timezone.utc)

    duration = now - changed_at

    return duration.days