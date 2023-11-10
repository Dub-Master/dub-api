from typing import Tuple, Union

from common import params
from dotenv import load_dotenv
from temporalio.client import Client, WorkflowExecutionStatus, WorkflowHandle

from .lib import LANGUAGE_NAMES, JobStatus, LanguageCode

load_dotenv()


async def get_client(url, namespace='default') -> Client:
    return await Client.connect(url, namespace=namespace)

async def start_workflow(
    temporal_client: Client,
    id: str,
    youtube_url: str,
    target_language: LanguageCode
) -> str:
    workflow_id = f"e2e-{id}"
    input = params.E2EParams(
        url=youtube_url,
        target_language=LANGUAGE_NAMES[target_language],
    )
    await temporal_client.start_workflow(
        "E2EWorkflow",
        input,
        id=workflow_id,
        task_queue="e2e-task-queue",
    )


async def describe_workflow(
    temporal_client: Client,
    id: str
) -> Tuple[JobStatus, Union[str, None]]:
    workflow_id = f"e2e-{id}"
    handle = temporal_client.get_workflow_handle(workflow_id)
    desc = await handle.describe()
    status = convert_status(desc.status)
    if status == JobStatus.completed:
        output = await handle.result()
        return status, output
    return status, None


def convert_status(status: WorkflowExecutionStatus | None) -> JobStatus:
    if not status:
        return JobStatus.failed
    elif status == WorkflowExecutionStatus.RUNNING:
        return JobStatus.running
    elif status == WorkflowExecutionStatus.COMPLETED:
        return JobStatus.completed
    elif status == WorkflowExecutionStatus.FAILED:
        return JobStatus.failed
    else:
        return JobStatus.failed
