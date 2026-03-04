"""
Centralised configuration — reads from .env and provides
typed, validated settings for the whole application. 

"""

import os
from dotenv import load_dotenv
from dataclasses import dataclass, field

load_dotenv()

@dataclass
class LLMConfig:
    api_key: str = field(default_factory=lambda: os.getenv("GROQ_API_KEY",""))
    model_name: str =field(default_factory=lambda: os.getenv("LLM_MODEL_NAME","llama-3.3-70b-versatile"))
    temperature: float = field(default_factory=lambda: float(os.getenv("LLM_TEMPERATURE", "0.3")))
    
    def validate(self) ->None:
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is required for LLMConfig")
        if not self.model_name:
            raise ValueError("LLM_MODEL_NAME is required for LLMConfig")
        if not (0.0 <= self.temperature <= 1.0):
            raise ValueError("LLM_TEMPERATURE must be between 0.0 and 1.0")


@dataclass 
class EmbeddingConfig:
    model_name: str = field(
        default_factory=lambda: os.getenv(
            "EMBEDDING_MODEL","sentence-transformers/all-MiniLM-L6-v2"
        )
    )

    def validate(self) -> None:
        if not self.model_name:
            raise ValueError("EMBEDDING_MODEL is required for EmbeddingConfig")


@dataclass
class ChunkingConfig:
    chunk_size: int = field(
        default_factory=lambda: int(os.getenv(
            "CHUNK_SIZE", "1000"
            )
        )
    )
    chunk_overlap: int = field(
        default_factory=lambda: int(os.getenv(
            "CHUNK_OVERLAP", "200"
            )
        )
    )
    
    def validate(self) -> None:
        if self.chunk_size <= 0:
            raise ValueError("CHUNK_SIZE must be a positive integer")
        if self.chunk_overlap < 0:
            raise ValueError("CHUNK_OVERLAP must be a non-negative integer")
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("CHUNK_OVERLAP must be less than CHUNK_SIZE")


@dataclass
class VectorStoreConfig:
    index_path: str = field(
        default_factory=lambda: os.getenv("FAISS_INDEX_PATH", "./data/faiss_index")
    )

    def validate(self) -> None:
        if not self.index_path:
            raise ValueError("FAISS_INDEX_PATH is required for VectorStoreConfig")


@dataclass 
class AppConfig:
    llm: LLMConfig = field(default_factory=LLMConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    title: str = field(default_factory=lambda: os.getenv("APP_TITLE", "ChatPDF"))
    chunking: ChunkingConfig = field(default_factory=ChunkingConfig)
    vector_store: VectorStoreConfig = field(default_factory=VectorStoreConfig)
    
    def validate(self) -> None:
        self.llm.validate()
        self.embedding.validate()
        self.chunking.validate()
        self.vector_store.validate()

settings = AppConfig()