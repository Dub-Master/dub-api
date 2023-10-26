# import asyncio
from common import params
from dotenv import load_dotenv
from temporalio.client import Client

load_dotenv()


async def get_client(url, namespace='default'):
    # Create client connected to server at the given address
    client = await Client.connect(url, namespace=namespace)
    return client


async def start(temporal_client, youtube_url):
    input = params.EncodingParams(
        url=youtube_url)

    # Execute a workflow
    source_data = await temporal_client.execute_workflow(
        "EncodingWorkflow",
        input,
        id="encoding-workflow",
        task_queue="encoding-task-queue",
    )

    s3_url_video_file = source_data[0]
    s3_url_audio_file = source_data[1]

    diarization = await temporal_client.execute_workflow(
        "DiarizationWorkflow",
        s3_url_audio_file,
        id="diarization-workflow",
        task_queue="diarization-task-queue",
    )

    print(f"Result: {diarization}")

    core_inputs = params.CoreParams(
        s3_url_audio_file=s3_url_audio_file,
        s3_url_video_file=s3_url_video_file,
        diarization=diarization)

    output = await temporal_client.execute_workflow(
        "CoreWorkflow",
        core_inputs,
        id="core-workflow",
        task_queue="core-task-queue",
    )

    print(f"Result: {output}")
    return output
