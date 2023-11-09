from common import params
from dotenv import load_dotenv
from temporalio.client import Client, WorkflowHandle, WorkflowExecutionStatus
from .lib import JobStatus, LanguageCode, LANGUAGE_NAMES

load_dotenv()


async def get_client(url, namespace='default') -> Client:
    return await Client.connect(url, namespace=namespace)

async def start(temporal_client: Client, youtube_url: str, target_language: LanguageCode) -> str:
    input = params.E2EParams(
        url=youtube_url,
        language=LANGUAGE_NAMES[target_language],
    )

    handle = await temporal_client.start_workflow(
        "E2EWorkflow",
        input,
        id="e2e-workflow",
        task_queue="e2e-task-queue",
    )
    print("Started workflow execution:", handle)

    return handle.run_id

async def describe(temporal_client: Client, run_id: str) -> [JobStatus, str | None]:
    handle: WorkflowHandle = temporal_client.get_workflow_handle("E2EWorkflow", run_id)
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
