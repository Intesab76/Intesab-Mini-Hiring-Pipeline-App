import os
import json

from datetime import datetime, timedelta, timezone

from difflib import SequenceMatcher

from sqlalchemy.orm import Session
from sqlalchemy import func 

from ..models import Candidate, CandidateHistory

from dotenv import load_dotenv
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint


load_dotenv()

def get_search_model():
    token = os.getenv("HUGGINGFACE_API_TOKEN")

    if not token:
        raise RuntimeError("LLM TOKEN NOT FOUND. TRY AGAIN.")

    llm = HuggingFaceEndpoint(
        repo_id = "meta-llama/Llama-3.1-8B-Instruct",
        task="text-generation",
        max_new_tokens = 256,
        temperature = 0,
        huggingfacehub_api_token = token
    )

    return ChatHuggingFace(llm=llm)


def understand_search(user_query : str):
    model = get_search_model()

    prompt = f""" You are helping a recruiter search candidates.

Understand the user's search request and return ONLY valid JSON.

Possible fields:

{{
    "name": null,
    "stage": null,
    "exclude_rejected": false,
    "minimum_days": null,
    "moved_to_stage": null,
    "moved_since_days": null,
    "reached_stage_not_hired": null,
    "understood":true
}}

Rules:

- name: candidate name if the user mentions a person.
- stage: current candidate stage if the user asks who is currently in a stage.
- exclude_rejected: true if the user wants everyone except rejected candidates.
- The following requests must set exclude_rejected to true:
  "Everyone except rejected candidates."
  "Everyone except rejected."
  "All candidates except rejected."
  "Show everyone who is not rejected."
  "Show all active candidates."
- These are valid hiring-pipeline searches and understood must be true.- minimum_days: number of days if the user asks who has been in a stage
  for more than a certain number of days.
- moved_to_stage: stage if the user asks who moved to that stage.
- If a value is not relevant, use null.
- Do not invent values.
- moved_since_days: number of days back from today if the user asks
  when someone moved to a stage, such as "since Monday".
- For "since Monday", calculate the number of days from today to Monday.
- If no date/time condition is mentioned, use null.
- Do not invent values.
- reached_stage_not_hired: the stage if the user asks who reached that
  stage but was not hired.
- For example, "Who reached the Offer stage but didn't get hired?"
  should return "Offer".
- understood: true if the request contains a candidate name,
  a hiring stage, or any hiring-pipeline condition.
- A candidate name by itself is a valid search.
  For example:
  "Priya"
  "Rahul"
  "Priya Sharma"
  "Find Priya"
  should all have understood set to true.
- understood: false only if the request is clearly unrelated
  to candidates, recruitment, stages, or hiring.
User query:

{user_query}
"""
    response = model.invoke(prompt)

    content = response.content
    
    if content.startswith("```json"):
        content = content[len("```json"):]

    if content.startswith("```"):
        content = content[len("```"):]

    if content.endswith("```"):
        content = content[:-3]

    content = content.strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        raise ValueError(f"LLM returned invalid JSON : {content}")


def search_candidates(
    db: Session,
    filters: dict
):

    if filters.get("understood") is False:
        return None
    
    query = db.query(Candidate)

    name = filters.get("name")
    stage = filters.get("stage")
    exclude_rejected = filters.get("exclude_rejected", False)
    minimum_days = filters.get("minimum_days")
    moved_to_stage = filters.get("moved_to_stage")
    moved_since_days = filters.get("moved_since_days")
    reached_stage_not_hired = filters.get(
        "reached_stage_not_hired"
    )

    # Search by candidate name
    if name:
        candidates = query.all()

        name_lower = name.lower()
        matches = []

        for candidate in candidates:
            candidate_name = candidate.name.lower()

            if name_lower == candidate_name:
                similarity = 1.0
                matches.append((candidate, similarity))
                continue

            if name_lower in candidate_name:
                similarity = 0.9
                matches.append((candidate, similarity))
                continue

            similarity = SequenceMatcher(
                None,
                name_lower,
                candidate_name
            ).ratio()

            if similarity >= 0.6:
                matches.append((candidate,similarity))
        
        matches.sort(key=lambda item : item[1],
                     reverse=True)

        candidates = [
            candidate for candidate, similarity in matches
        ]

    else:
        candidates = query.all()

    # Current stage filter
    if stage:
        candidates = [
            candidate
            for candidate in candidates
            if candidate.current_stage.lower()
            == stage.lower()
        ]

    # Exclude rejected candidates
    if exclude_rejected:
        candidates = [
            candidate
            for candidate in candidates
            if candidate.current_stage.lower()
            != "rejected"
        ]
    if minimum_days is not None:
        cutoff_time = (
            datetime.now(timezone.utc) - timedelta(days=minimum_days)
        )

        matching_candidates = []

        for candidate in candidates:
            latest_history = (
                db.query(CandidateHistory).filter(CandidateHistory.candidate_id == candidate.id)
            .order_by(
                CandidateHistory.changed_at.desc()
            ).first()
            )

            if (
                latest_history and latest_history.changed_at <= cutoff_time
            ):
                matching_candidates.append(candidate)
        candidates = matching_candidates

    if moved_to_stage:
        history_query = (
            db.query(CandidateHistory)
            .filter(func.lower(CandidateHistory.to_stage) == moved_to_stage.lower())
        )

        if moved_since_days is not None:
            try:
                moved_since_days = int(moved_since_days)
            except(ValueError,TypeError):
                moved_since_days=None

        if moved_since_days is not None:
            cutoff_time = (
                    datetime.now(timezone.utc) - timedelta(days=moved_since_days)
                )

            history_query = history_query.filter(CandidateHistory.changed_at >= cutoff_time)

        history_records = history_query.all()

        candidate_ids = {
                history.candidate_id
                for history in history_records
                }
            
        candidates = [
                candidate for candidate in candidates
                if candidate.id in candidate_ids
            ]

    if reached_stage_not_hired:

        history_records = (
            db.query(CandidateHistory)
            .filter(
                func.lower(CandidateHistory.to_stage)
                == reached_stage_not_hired.lower()
            )
            .all()
        )

        candidate_ids = {
            history.candidate_id
            for history in history_records
        }

        candidates = [
            candidate
            for candidate in candidates
            if candidate.id in candidate_ids
            and candidate.current_stage.lower() != "hired"
        ]
                
    return candidates