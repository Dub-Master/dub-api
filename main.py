import os
import random
import string

import boto3
import databases
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pipeline import temporal
from pipeline.types import Job, JobIn, JobStatus, is_status_final, LanguageCode
import sqlalchemy


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is not None and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

TEMPORAL_URL = os.getenv("TEMPORAL_URL")
TEMPORAL_NAMESPACE = os.getenv("TEMPORAL_NAMESPACE") or "default"

AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

jobs_table = sqlalchemy.Table(
    "jobs",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("input_url", sqlalchemy.String, nullable=False, server_default=""),
    sqlalchemy.Column("output_url", sqlalchemy.String, nullable=False, server_default=""),
    sqlalchemy.Column("target_language", sqlalchemy.String, nullable=False, server_default=LanguageCode.en),
    sqlalchemy.Column("status", sqlalchemy.String, nullable=False, server_default=JobStatus.created),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, nullable=False, server_default=sqlalchemy.sql.func.now()),
)

engine = sqlalchemy.create_engine(
    DATABASE_URL
)
metadata.create_all(engine)


app = FastAPI()

@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


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


@app.options("/jobs")
@app.post("/jobs")
async def create_job(job_in: JobIn) -> Job:
    job = Job(
        id=random_id(),
        status=JobStatus.created,
        input_url=job_in.input_url,
        target_language=job_in.target_language,
    )

    query = jobs_table.insert().values(
        id=job.id,
        input_url=job.input_url,
        target_language=job.target_language,
        status=job.status,
    )
    await database.execute(query)

    temporal_client = await temporal.get_client(
        TEMPORAL_URL, TEMPORAL_NAMESPACE)
    
    await temporal.start_workflow(
        temporal_client,
        job.id,
        job.input_url, 
        job.target_language)

    return job


@app.get("/jobs/{job_id}")
async def get_job(job_id: str) -> Job:
    query = jobs_table.select().where(jobs_table.c.id == job_id)
    row = await database.fetch_one(query)
    if not row:
        raise HTTPException(status_code=404, detail="Job not found")
    job = Job(**row)

    if is_status_final(job.status):
        return job

    temporal_client = await temporal.get_client(
        TEMPORAL_URL, TEMPORAL_NAMESPACE)
    status, output = await temporal.describe_workflow(temporal_client, job_id)
    
    job.status = status
    job.output_url = get_presigned_url(output) if output else ""

    query = jobs_table.update().where(jobs_table.c.id == job_id).values(
        status=job.status,
        output_url=job.output_url,
    )
    await database.execute(query)

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
