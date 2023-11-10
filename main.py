import os
import random
import string

import boto3
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pipeline import temporal
from pipeline.lib import Job, JobStatus, is_status_final


load_dotenv()

app = FastAPI()

TEMPORAL_URL = os.getenv("TEMPORAL_URL")
TEMPORAL_NAMESPACE = os.getenv("TEMPORAL_NAMESPACE") or "default"

AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")

s3 = boto3.client('s3',
    endpoint_url = AWS_S3_ENDPOINT_URL,
    aws_access_key_id = AWS_ACCESS_KEY_ID,
    aws_secret_access_key = AWS_SECRET_ACCESS_KEY
)

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
    if is_status_final(job.status):
        return job
    temporal_client = await temporal.get_client(
        TEMPORAL_URL, TEMPORAL_NAMESPACE)
    status, output = await temporal.describe_workflow(temporal_client, job_id)
    job.status = status
    job.output_url = get_presigned_url(output) if output else ""
    JOBS[job_id] = job
    return job

def random_id() -> str:
    return "".join(random.choices(string.ascii_letters, k=12))

def get_presigned_url(key: str) -> str:
    url = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': AWS_S3_BUCKET,
            'Key': key
        }
    )
    return url
