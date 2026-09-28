from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from . import models
from .routes import candidates, search


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Mini Hiring Pipeline"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(candidates.router)
app.include_router(search.router)


@app.get("/")
def root():
    return {
        "message": "Mini Hiring Pipeline API is running"
    }