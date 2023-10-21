import os
import random
import string
from enum import Enum
from typing import Union

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pipeline import temporal
from pydantic import BaseModel

load_dotenv()

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
    # output_url: str
    status: JobStatus


JOBS = {}


@app.options("/jobs")
@app.post("/jobs")
async def create_job(job: Job):
    temporal_client = await temporal.get_client(os.getenv("TEMPORAL_URL"))
    print('job', job)
    job.id = generate_random_id()
    await temporal.start(temporal_client, job.input_url)
    job.status = JobStatus.created
    JOBS[job.id] = job
    return {"id": job.id}


@app.get("/jobs/{job_id}")
def get_job(job_id: str) -> Job:
    return JOBS[job_id]


def generate_random_id() -> str:
    return ''.join(random.choices(string.ascii_letters, k=12))
