import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from app.services.rag import ingest_service, query_service
from app.utils.auth import verify_api_key


logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/api/v1/rag",
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
        num_chunks = await run_in_threadpool(ingest_service, request.text)
        return {
            "message": "Successfully ingested text",
            "chunks": num_chunks,
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.exception("Ingestion API error")
        raise HTTPException(status_code=500, detail="Failed to ingest text.") from e


@router.post("/query")
async def query_rag(request: QueryRequest):
    """
    Query the RAG pipeline.
    """
    try:
        response = await run_in_threadpool(
            query_service, 
            request.query, 
            request.model, 
            request.provider
        )
        return {
            "query": request.query,
            "response": response
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.exception("RAG query API error")
        raise HTTPException(status_code=500, detail="Failed to execute RAG query.") from e
