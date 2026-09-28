from datetime import datetime,timezone
from sqlalchemy import DateTime,ForeignKey,String
from sqlalchemy.orm import Mapped,mapped_column,relationship

from .database import Base

class Candidate(Base):
    __tablename__="candidates"

    id:Mapped[int] = mapped_column(primary_key=True)
    name:Mapped[str] = mapped_column(String(100),nullable=False)
    email:Mapped[str] = mapped_column(String(100),nullable=False)
    role:Mapped[str] = mapped_column(String(100),nullable=False)

    current_stage : Mapped[str] = mapped_column(String(20),nullable=False,default="applied")

    created_at:Mapped[datetime] = mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc),nullable=False)

    history = relationship("CandidateHistory",back_populates="candidate",cascade="all, delete-orphan")


class CandidateHistory(Base):
    __tablename__ = "candidate_history"

    id:Mapped[int] = mapped_column(primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"),
                                              nullable=False)
    from_stage:Mapped[str | None] = mapped_column(String(20),nullable=False)
    
    to_stage:Mapped[str] = mapped_column(String(20),nullable=False)

    changed_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc),nullable=False)



    candidate = relationship("Candidate",back_populates="history")

