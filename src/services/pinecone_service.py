"""
Pinecone service based on the Langchain documentation: https://python.langchain.com/docs/integrations/vectorstores/pinecone/
"""
import time
from uuid import uuid4
from typing import List
from core.settings import settings
from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document

class PineconeService:
    """
    Singleton service to manage the Pinecone vector database to add and query documents
    """
    _instance = None
    
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, index_name: str = settings.BASE_PINECONE_INDEX_NAME):
        if not self._initialized:
            self._index_name = index_name
            self._client = Pinecone(api_key=settings.PINECONE_API_KEY)
            self._embeddings = OpenAIEmbeddings(
                model=settings.DEFAULT_OPENAI_EMBEDDING_MODEL
            )
            self._index = self._get_or_create_index()
            self._vector_store = PineconeVectorStore(
                index=self._index, 
                embedding=self._embeddings
            )
            self._initialized = True

    @property
    def vector_store(self) -> PineconeVectorStore:
        """Controlled access to the vector store"""
        return self._vector_store

    def _get_or_create_index(self):
        """
        Get or create the index
        """
        existing_indexes = [
            index_info["name"] for index_info in self._client.list_indexes()
        ]
        
        if self._index_name not in existing_indexes:
            self._client.create_index(
                name=self._index_name,
                dimension=3072,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
            # Wait for the index to be ready
            while not self._client.describe_index(self._index_name).status["ready"]:
                time.sleep(1)

        return self._client.Index(self._index_name)

    def add_documents(self, documents: List[Document]):
        """
        Add documents to the vector store
        :param documents: List[Document] with the documents to add
        :return: dict with the result of the operation
        """
        uuids = [str(uuid4()) for _ in range(len(documents))]
        result = self.vector_store.add_documents(documents=documents, ids=uuids)
        return result

    def query(self, text_to_search: str, returned_documents: int = 10, filters_by_metadata: dict = None):
        """
        Query the vector store
        :param text_to_search: str with the text to search
        :param returned_documents: int with the number of documents to return
        :param filters_by_metadata: dict with the filters to apply
        :return: List[Document] with the documents found
        """
        results = self.vector_store.similarity_search(
            text_to_search,
            k=returned_documents,
            filter=filters_by_metadata
        )
        return results







