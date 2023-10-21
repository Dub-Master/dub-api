from typing import Union
from enum import Enum
import random
import string

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class JobStatus(str, Enum):
    created = "created"
    running = "running"
    completed = "completed"
    failed = "failed"

class Job(BaseModel):
    id: str
    input_url: str
    output_url: str
    status: JobStatus

JOBS = {}

@app.options("/jobs")
@app.post("/jobs")
def create_job(job: Job):
    job.id = generate_random_id()
    job.status = JobStatus.created
    JOBS[job.id] = job
    return {"id": job.id}

@app.get("/jobs/{job_id}")
def get_job(job_id: str) -> Job:
    return JOBS[job_id]

def generate_random_id() -> str:
    return ''.join(random.choices(string.ascii_letters, k=12))
