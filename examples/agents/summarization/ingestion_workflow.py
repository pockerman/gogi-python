"""Document ingestion workflow for the summarization agent.

Embedding a document may take a while (chunking, calling the embeddings model for every chunk, storing
the vectors), so it is run as an asynchronous Gogi workflow rather than inline in the agent.
The agent registers the workflow once, and creates a workflow job every time the user uploads a document.

The workflow itself asks the Gogi document service to ingest the document into the agent's index,
using OpenAI to embed the chunks, and reports its progress back through the workflow job.
"""

import base64
import json
import mimetypes
import os
import time

from gogi.gogi import Gogi
from gogi.models.ingest_document import IngestDocumentRequest
from gogi.models.workflow.reliability_config import ReliabilityConfig
from gogi.models.workflow.requests.complete_job_request import CompleteJobRequest
from gogi.models.workflow.requests.create_job_request import CreateJobRequest
from gogi.models.workflow.requests.fail_job_request import FailJobRequest
from gogi.models.workflow.requests.get_job_status_request import GetJobStatusRequest
from gogi.models.workflow.requests.register_workflow_request import RegisterWorkflowRequest
from gogi.models.workflow.requests.update_job_progress_request import UpdateJobProgressRequest
from gogi.models.workflow.resource_config import ResourceConfig
from gogi.models.workflow.scaling_config import ScalingConfig
from gogi.models.workflow.workflow_job import WorkflowJob
from gogi.models.workflow.workflow_spec import WorkflowSpec
from gogi.utils.document_ingestion_polling import wait_for_document_ingest
from gogi.utils.job_status_enum import JobStatus
from gogi.utils.workflow import workflow

EMBEDDINGS_CLIENT = "openai"
EMBEDDINGS_MODEL = "text-embedding-3-small"
CHUNK_STRATEGY = "fixed"

# image the deploy CLI builds for this workflow. Only needed when the workflow runs on the platform
CONTAINER_IMAGE = "gogi/summarization-ingestion:latest"


@workflow(
    name="summarization-document-ingestion",
    api_path="/agents/summarization/ingest",
    response_mode="async",
    min_replicas=0,
    max_replicas=3,
    cpu="500m",
    memory="1Gi",
    timeout_seconds=600,
    max_retries=2,
)
def ingest_document_workflow(job_id: str, index_name: str, document_id: str, filename: str, content_b64: str) -> dict:
    """Embed a user document with OpenAI and store it in the agent's index.

    Args:
        job_id: The workflow job this invocation serves. Progress and the final result are reported on it.
        index_name: The index the document is ingested into.
        document_id: Id the document is stored under. The RAG pipeline uses it to restrict retrieval.
        filename: Original name of the uploaded file.
        content_b64: The file contents, base64 encoded so they can travel inside the job's JSON input.
    """

    # the workflow runs in its own container, so it opens its own connection to the platform
    platform = Gogi(gateway_url=os.getenv("GOGI_GATEWAY_URL", "localhost:50051"))

    try:
        platform.workflows.update_job_progress(
            UpdateJobProgressRequest(job_id=job_id, progress_message=f"Embedding {filename} with {EMBEDDINGS_MODEL}")
        )

        content_type, _ = mimetypes.guess_type(filename)
        ingest_job = platform.documents.ingest_document(
            IngestDocumentRequest(
                index_name=index_name,
                document_id=document_id,
                filename=filename,
                content=base64.b64decode(content_b64),
                content_type=content_type or "UNKNOWN",
                chunk_strategy=CHUNK_STRATEGY,
                embeddings_client=EMBEDDINGS_CLIENT,
                embeddings_model=EMBEDDINGS_MODEL,
                metadata={"filename": filename},
            )
        )
        ingest_job = wait_for_document_ingest(platform=platform, job_id=ingest_job.job_id, poll_interval=2, timeout=540)

        document = platform.documents.get_document(index_name=index_name, document_id=document_id)
        result = {"document_id": document_id, "index_name": index_name, "chunk_count": document.chunk_count}
        platform.workflows.complete_job(CompleteJobRequest(job_id=job_id, result_json=json.dumps(result)))
        return result
    except Exception as e:
        platform.workflows.fail_job(FailJobRequest(job_id=job_id, error=str(e)))
        raise


def register_ingestion_workflow(platform: Gogi) -> str:
    """Register the ingestion workflow with the Gogi workflow registry and return its id.
    The spec is built from the metadata the ``@workflow`` decorator attached to the function.
    """
    meta = ingest_document_workflow._workflow_metadata
    spec = WorkflowSpec(
        name=meta["name"],
        api_path=meta["api_path"],
        container_image=CONTAINER_IMAGE,
        response_mode=meta["response_mode"],
        scaling=ScalingConfig(
            min_replicas=meta["min_replicas"],
            max_replicas=meta["max_replicas"],
            target_cpu_percent=meta["target_cpu_percent"],
        ),
        resources=ResourceConfig(
            cpu=meta["cpu"], memory=meta["memory"], gpu_type=meta["gpu_type"], num_gpus=meta["num_gpus"]
        ),
        reliability=ReliabilityConfig(timeout_seconds=meta["timeout_seconds"], max_retries=meta["max_retries"]),
    )
    response = platform.workflows.register_workflow(RegisterWorkflowRequest(spec=spec))
    return response.workflow_id


def submit_ingestion_job(
    platform: Gogi, workflow_id: str, index_name: str, document_id: str, filename: str, content: bytes
) -> tuple[str, dict]:
    """Create an ingestion job for a document. Returns the job id and the job input."""
    job_input = {
        "index_name": index_name,
        "document_id": document_id,
        "filename": filename,
        "content_b64": base64.b64encode(content).decode("ascii"),
    }
    response = platform.workflows.create_job(
        CreateJobRequest(workflow_id=workflow_id, input_json=json.dumps(job_input))
    )
    return response.job_id, job_input


def wait_for_workflow_job(platform: Gogi, job_id: str, poll_interval: int = 2, timeout: int = 600) -> WorkflowJob:
    """Poll a workflow job until it completes, fails or the timeout is reached."""
    start = time.time()
    while time.time() - start < timeout:
        job = platform.workflows.get_job_status(GetJobStatusRequest(job_id=job_id)).job
        if job.status == JobStatus.JobCompleted:
            return job
        if job.status == JobStatus.JobFailed:
            raise RuntimeError(f"Ingestion workflow failed: {job.error}")
        time.sleep(poll_interval)
    raise TimeoutError(f"Ingestion workflow job {job_id} timed out")
