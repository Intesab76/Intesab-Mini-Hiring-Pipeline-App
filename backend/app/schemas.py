from datetime import datetime
from pydantic import BaseModel,ConfigDict

class CandidateCreate(BaseModel):
    name:str
    email:str
    role:str


class CandidateResponse(CandidateCreate):
    id:int
    current_stage:str
    created_at:datetime
    days_in_current_stage:int

    model_config = ConfigDict(from_attributes=True)


class HistoryResponse(BaseModel):
    id:int
    from_stage:str | None
    to_stage:str
    changed_at:datetime

    model_config = ConfigDict(from_attributes=True)