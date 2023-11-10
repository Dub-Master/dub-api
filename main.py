import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pipeline import temporal
from pipeline.lib import Job, JobStatus
import random
import string


load_dotenv()

app = FastAPI()

TEMPORAL_URL = os.getenv("TEMPORAL_URL")
TEMPORAL_NAMESPACE = os.getenv("TEMPORAL_NAMESPACE") or "default"

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


JOBS: dict[str, Job] = dict()


@app.options("/jobs")
@app.post("/jobs")
async def create_job(job: Job):
    job.id = random_id()
    job.status = JobStatus.created
    print("creating job", job)

    temporal_client = await temporal.get_client(
        TEMPORAL_URL, TEMPORAL_NAMESPACE)
    
    await temporal.start_workflow(
        temporal_client,
        job.id,
        job.input_url, 
        job.target_language)
    
    JOBS[job.id] = job
    return job


@app.get("/jobs/{job_id}")
async def get_job(job_id: str) -> Job:
    job = JOBS.get(job_id)
    if not job:
        return Job(id=job_id, status=JobStatus.failed)
    temporal_client = await temporal.get_client(
        TEMPORAL_URL, TEMPORAL_NAMESPACE)
    status, output = await temporal.describe_workflow(temporal_client, job_id)
    job.status = status
    job.output_url = output
    JOBS[job_id] = job
    return job

def random_id() -> str:
    return "".join(random.choices(string.ascii_letters, k=12))
