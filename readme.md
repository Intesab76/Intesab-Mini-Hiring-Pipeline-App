# Mini Hiring Pipeline

A small recruitment pipeline application for managing candidates through different hiring stages.

The application allows a recruiter to:

- Add candidates
- View candidates grouped by hiring stage
- Move candidates forward one stage at a time
- Reject candidates before they are hired
- View a candidate's complete stage history
- See how long a candidate has been in their current stage
- Search candidates using natural language
- Combine different search conditions

## Hiring Stages

Candidates move through the following stages:

Applied → Screening → Interview → Offer → Hired

A candidate can also be rejected before reaching Hired.

Candidates cannot move backwards or skip stages.

---

## Tech Stack

### Frontend

- React
- Vite
- JavaScript
- Plain CSS

### Backend

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL

### Natural Language Search

- LangChain
- Hugging Face Inference API
- Llama 3.1 8B Instruct

### Database

- PostgreSQL

---

## Project Structure

```text
mini-hiring-pipeline/
│
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── main.py
│   │
│   ├── .env
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── package.json
│   └── ...
│
├── ai-logs/
│   └── development-log.md
│
├── docs/
│   └── screenshots/
│
├── .gitignore
└── README.md
```
