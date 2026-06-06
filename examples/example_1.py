"""This example illustrates the main endpoints of the Gogi platform, including index creation, document ingestion, and querying. 
It serves as a basic walkthrough of the typical workflow when interacting with the Gogi platform, 
and demonstrates how to use the Python client to perform common operations.
"""

from loguru import logger
import tempfile
from pathlib import Path
from rich import print as rich_print
import uuid

from gogi.gogi import Gogi
from gogi.clients.models.index_config import IndexConfig
from gogi.clients.models.ingest_document import IngestDocumentRequest
from gogi.utils.document_ingestion_polling import wait_for_document_ingest

def create_temp_document(filename: str) -> bytes:
    """Helper function to create a temporary PDF file for testing document ingestion."""

    file_content = """This is some dummy content for the PDF document. 
    It can be as long as needed to simulate a real document, and can include multiple paragraphs, sections, etc.
    Date: June 1, 2026

    Section 1: Paid Time Off
    All full-time employees receive exactly 27 days of paid vacation per year.
    Unused vacation days roll over, but the maximum carryover is 8 days.
    Employees in the Zurich office receive an additional 3 floating holidays.

    Section 2: Remote Work
    Employees may work remotely up to 3 days per week. Wednesday is a
    mandatory in-office day for all teams. Remote work from outside the
    employee's home country requires written approval from the VP of People
    Operations, Priya Chandrasekaran, at least 14 business days in advance.

    Section 3: Expense Policy
    The daily meal allowance during business travel is $67 USD. Flights
    over 6 hours qualify for business class. Employees must submit
    expense reports within 11 calendar days of trip completion using the
    internal tool "SpendTrack 4.0".

    Section 4: Annual Bonus
    The annual bonus target is 14% of base salary for individual contributors
    and 19% for managers. Bonuses are paid in the March payroll cycle.
    The bonus multiplier is determined by the "Quasar Score", a proprietary
    performance rating on a scale of 0-150.

    Section 5: Pet Policy
    GloboTech allows dogs under 25 pounds in the Austin and Portland offices
    on Tuesdays and Thursdays only. All pets must be registered with Facilities
    using form GT-PET-2026. The Zurich and Singapore offices do not permit pets.
    """.strip()

    doc_path = Path(tempfile.mkdtemp()) / filename
    doc_path.write_text(file_content)
    return doc_path.read_bytes()




if __name__ == '__main__':

    # connect to the Gogi platform. 
    # This will be the first step in any interaction with the platform, and will 
    # give you access to all of the available clients (indexes, documents, and queries).
    platform = Gogi(gateway_url="localhost:50051", logger=logger)


    # list indexes for a user
    response = platform.indexes.list_indexes(owner_name="user-123")
    rich_print(f"List indexes response: {response}")

    # create a new index. 
    # Documets can only be ingested into existing indexes, 
    # so this is a necessary step before we can add any documents.
    index_config = IndexConfig(
        name="my-first-doc-index",
        embedding_model="text-embedding-3-small",
        embedding_dimensions=756,
        chunking_strategy="overlap",
        chunk_size=500,
        chunk_overlap=50,
        metadata_schema={"source": "pdf", "author": "John Doe"})
    
    # create the index
    response = platform.indexes.create_index(owner_name="user-123", config=index_config)
    rich_print(f"Create index response: {response}")

    # get the index we just created
    response = platform.indexes.get_index(index_name=response.name)
    rich_print(f"Get index response: {response}")

    # list the documents associated with the index.
    # we shouldn't have any documents yet, so this should return an empty list.
    response = platform.documents.list_documents(index_name=response.name)
    rich_print(f"List documents response: {response}")


    doc_content = create_temp_document("my_first_doc.txt")

    # TODO: Right now we assume that document_id is UUID
    # This need not be the case
    ingest_request = IngestDocumentRequest(content=doc_content, content_type="UNKNOWN",
                                           index_name=index_config.name, 
                                           document_id=uuid.uuid4().hex,
                                           filename="my_first_doc.txt",
                                           embeddings_model="clip",
                                           embeddings_client="sentence-transformer",
                                           chunk_strategy="fixed",
                                           metadata={"format": "txt", "author": "John Doe", "source": "generated"})
    # ingest a document into the index. 
    # This will kick off an asynchronous job to process the document (e.g., chunking, embedding, etc.), 
    # so the response will contain information about the job status rather than the document itself.
    response = platform.documents.ingest_document(ingest_request)

    # Find out the job
    job = platform.documents.get_document_ingest_job(response.job_id)

    rich_print(f"Job status is {job.status}")
    
    # we need to wait for the ingest job to complete 
    # before we can query the document or see it in the list of documents for the index.
    # How you hanlde this will depend on your specific use case and requirements - you could poll the job status until it's complete,
    # or you could set up a webhook to be notified when the job is done, etc. For this example, we'll just do a simple polling loop with a sleep interval. 
    result = wait_for_document_ingest(platform=platform, job_id=response.job_id, 
                                      poll_interval=5, timeout=300)
    rich_print(f"Ingest document response: {result}")



    # response = platform.documents.get_document(index_name=response[0].index_name, 
    #                                            document_id=response[0].document_id)
    # rich_print(f"Get document response: {response}")

    # # delete a document
    # response = platform.documents.delete_document(index_name=response.index_name, 
    #                                               document_id=response.document_id)
    # rich_print(f"Delete document response: {response}") 


    # # finally, delete the index we created. 
    # # This will also delete all documents contained within the index, so use with caution!
    # response = platform.indexes.delete_index(index_name=index_config.name)
    # rich_print(f"Delete index response: {response}")
