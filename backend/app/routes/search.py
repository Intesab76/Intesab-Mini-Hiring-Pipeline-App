from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import CandidateResponse
from ..services.search import (
    understand_search,
    search_candidates
)
from ..routes.candidates import add_stage_duration


router = APIRouter(
    prefix="/search",
    tags=["Search"]
)


@router.get("/")
def search(
    query: str,
    db: Session = Depends(get_db)
):
    filters = understand_search(query)

    candidates = search_candidates(
        db,
        filters
    )
    if candidates is None:
        return {
            "message":(
                "I could not understand the search."
                "Try with a proper candidate name or stage or both."
            ),
            "results":[]
        }
    print("Search Filters",filters)

    return [
        add_stage_duration(candidate, db)
        for candidate in candidates
    ]