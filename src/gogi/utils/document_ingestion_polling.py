import time


from gogi.utils.job_status_enum import JobStatus

def wait_for_document_ingest(platform, job_id: str, poll_interval: int = 5, timeout: int = 300):
    """Utility function to poll the status of a document ingest job until it's complete or a timeout is reached."""
    
    start = time.time()
    while time.time() - start < timeout:
        job = platform.documents.get_document_ingest_status(job_id)
        if job.status == JobStatus.COMPLETED:
            return job
        if job.status == JobStatus.FAILED:
            raise RuntimeError(f"Ingestion failed: {job.error}")
        time.sleep(poll_interval)
    raise TimeoutError("Ingestion timed out")