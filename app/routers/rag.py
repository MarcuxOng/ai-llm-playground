import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.services.rag import ingest_service, query_service
from app.utils.auth import verify_api_key


logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/rag",
    tags=["RAG"],
    dependencies=[Depends(verify_api_key)]
)


class IngestRequest(BaseModel):
    text: str


class QueryRequest(BaseModel):
    provider: str
    model: str
    query: str


@router.post("/ingest")
async def ingest_documents(request: IngestRequest):
    """
    Ingest text into the Pinecone vector store.
    """
    try:
        num_chunks = ingest_service(request.text)
        return {
            "message": "Successfully ingested text",
            "chunks": num_chunks,
        }
    except Exception as e:
        logger.error(f"Ingestion API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query")
async def query_rag(request: QueryRequest):
    """
    Query the RAG pipeline.
    """
    try:
        response = query_service(
            request.query, 
            request.model, 
            request.provider
        )
        return {
            "query": request.query,
            "response": response
        }
    except Exception as e:
        logger.error(f"RAG Query API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
