import hashlib
import logging
import time
from langchain_core.documents import Document
from pinecone import Pinecone
from typing import List

logger = logging.getLogger(__name__)


class PineconeStore:
    """
    Simplified VectorStore to interact with Pinecone using the SDK directly.
    """
    def __init__(self, index_name: str, embedding, api_key: str, namespace: str):
        self.pc = Pinecone(api_key=api_key)
        self.index = self.pc.Index(index_name)
        self.embedding = embedding
        self.namespace = namespace

    def add_documents(self, documents: List[Document]):
        """Add LangChain documents to Pinecone."""
        texts = [doc.page_content for doc in documents]
        metadatas = []
        ingestion_timestamp = str(int(time.time()))

        for i, doc in enumerate(documents):
            meta = dict(doc.metadata) if doc.metadata else {}
            meta["text"] = texts[i]  # Store text for retrieval
            meta["namespace"] = self.namespace
            metadatas.append(meta)
        embeddings = self.embedding.embed_documents(texts)

        vectors = []
        for i, (text, meta, vector) in enumerate(zip(texts, metadatas, embeddings, strict=True)):
            # Extract document identifier from metadata (source, doc_id, or fallback)
            doc_identifier = meta.get('source', meta.get('doc_id', 'unknown'))

            # Build hash input with disambiguating fields
            hash_input = f"{self.namespace}_{doc_identifier}_{i}_{ingestion_timestamp}_{text}"
            content_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:16]

            vectors.append({
                "id": f"{self.namespace}_{doc_identifier}_{i}_{content_hash}",
                "values": vector,
                "metadata": meta
            })

        self.index.upsert(
            vectors=vectors,
            namespace=self.namespace
        )

    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """Perform a similarity search."""
        query_embedding = self.embedding.embed_query(query)
        results = self.index.query(
            namespace=self.namespace,
            vector=query_embedding,
            top_k=k,
            include_metadata=True
        )
        
        docs = []
        for res in results.matches:
            if "text" in res.metadata:
                text = res.metadata.pop("text")
                docs.append(Document(page_content=text, metadata=res.metadata))
        return docs

    def as_retriever(self, search_kwargs: dict = None):
        """Mock LangChain retriever interface."""
        if search_kwargs is None:
            search_kwargs = {"k": 5}
        
        class Retriever:
            def __init__(self, store, kwargs):
                self.store = store
                self.kwargs = kwargs
            def invoke(self, query: str):
                return self.store.similarity_search(query, k=self.kwargs.get("k", 5))
            # Support for LangChain LCEL
            def __or__(self, other):
                from langchain_core.runnables import RunnableLambda
                return RunnableLambda(self.invoke) | other
                
        return Retriever(self, search_kwargs)