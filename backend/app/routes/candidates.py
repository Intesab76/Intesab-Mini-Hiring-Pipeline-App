from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Candidate,CandidateHistory
from ..schemas import CandidateCreate,CandidateResponse,HistoryResponse
from ..services.pipeline import get_next_stage,can_reject,get_days_in_stage

router = APIRouter(prefix="/candidates",tags=["Candidates"])

def add_stage_duration(candidate, db):
    latest_history = (
        db.query(CandidateHistory)
        .filter(
            CandidateHistory.candidate_id == candidate.id
        )
        .order_by(CandidateHistory.changed_at.desc())
        .first()
    )

    if latest_history:
        candidate.days_in_current_stage = get_days_in_stage(
            latest_history.changed_at
        )
    else:
        candidate.days_in_current_stage = 0

    return candidate


@router.post("/",response_model=CandidateResponse)
def create_candidate(candidate_data: CandidateCreate,
                     db: Session = Depends(get_db)):
    candidate = Candidate(
        name = candidate_data.name,
        email = candidate_data.email,
        role = candidate_data.role,
        current_stage = "Applied"
    )

    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    history = CandidateHistory(candidate_id = candidate.id,
                               from_stage = None,
                               to_stage = "Applied")

    db.add(history)
    db.commit()

    return  add_stage_duration(candidate, db)


@router.get("/",response_model = list[CandidateResponse])
def get_candidates(
    db: Session = Depends(get_db)
):
    candidates = (
        db.query(Candidate).order_by(Candidate.created_at.desc()).all()
    )

    return [
    add_stage_duration(candidate, db)
    for candidate in candidates
]


@router.get("/{candidate_id}", response_model=CandidateResponse)
def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    candidate = (
        db.query(Candidate)
        .filter(Candidate.id == candidate_id)
        .first()
    )

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    return add_stage_duration(candidate, db)

@router.get(
    "/{candidate_id}/history",
    response_model=list[HistoryResponse]
)
def get_candidate_history(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    candidate = (
        db.query(Candidate)
        .filter(Candidate.id == candidate_id)
        .first()
    )

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    history = (
        db.query(CandidateHistory)
        .filter(
            CandidateHistory.candidate_id == candidate_id
        )
        .order_by(CandidateHistory.changed_at.asc())
        .all()
    )

    return history


@router.post("/{candidate_id}/advance", response_model=CandidateResponse)
def advance_candidate(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    candidate = (
        db.query(Candidate)
        .filter(Candidate.id == candidate_id)
        .first()
    )

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    try:
        next_stage = get_next_stage(candidate.current_stage)
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    old_stage = candidate.current_stage

    candidate.current_stage = next_stage

    history = CandidateHistory(
        candidate_id=candidate.id,
        from_stage=old_stage,
        to_stage=next_stage
    )

    db.add(history)
    db.commit()
    db.refresh(candidate)

    return add_stage_duration(candidate, db)


@router.post("/{candidate_id}/reject", response_model=CandidateResponse)
def reject_candidate(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    candidate = (
        db.query(Candidate)
        .filter(Candidate.id == candidate_id)
        .first()
    )

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    if not can_reject(candidate.current_stage):
        raise HTTPException(
            status_code=400,
            detail="Candidate cannot be rejected from the current stage."
        )

    old_stage = candidate.current_stage

    candidate.current_stage = "Rejected"

    history = CandidateHistory(
        candidate_id=candidate.id,
        from_stage=old_stage,
        to_stage="Rejected"
    )

    db.add(history)
    db.commit()
    db.refresh(candidate)

    return add_stage_duration(candidate, db)