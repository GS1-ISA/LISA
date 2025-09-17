"""
Data models for ISA SuperApp.

This module defines the core data models used throughout the application
for representing documents, vectors, metadata, and other entities.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from .exceptions import ISAValidationError


class DocumentType(Enum):
    """Document type enumeration."""

    TEXT = "text"
    MARKDOWN = "markdown"
    PDF = "pdf"
    HTML = "html"
    JSON = "json"
    YAML = "yaml"
    CSV = "csv"
    XML = "xml"
    CODE = "code"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    UNKNOWN = "unknown"


class DocumentStatus(Enum):
    """Document processing status."""

    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    ARCHIVED = "archived"
    DELETED = "deleted"


class VectorStoreType(Enum):
    """Vector store type enumeration."""

    CHROMA = "chroma"
    PINECONE = "pinecone"
    WEAVIATE = "weaviate"
    QDRANT = "qdrant"
    MILVUS = "milvus"
    FAISS = "faiss"
    ELASTICSEARCH = "elasticsearch"
    OPENSEARCH = "opensearch"


class EmbeddingProvider(Enum):
    """Embedding provider enumeration."""

    OPENAI = "openai"
    HUGGINGFACE = "huggingface"
    SENTENCE_TRANSFORMERS = "sentence_transformers"
    COHERE = "cohere"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    LOCAL = "local"


@dataclass
class DocumentMetadata:
    """Document metadata."""

    title: str | None = None
    author: str | None = None
    description: str | None = None
    keywords: list[str] = field(default_factory=list)
    language: str | None = None
    source: str | None = None
    category: str | None = None
    tags: list[str] = field(default_factory=list)
    custom_fields: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "author": self.author,
            "description": self.description,
            "keywords": self.keywords,
            "language": self.language,
            "source": self.source,
            "category": self.category,
            "tags": self.tags,
            "custom_fields": self.custom_fields,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DocumentMetadata":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class Document:
    """Document representation."""

    id: str
    content: str
    document_type: DocumentType
    metadata: DocumentMetadata
    file_path: Path | None = None
    file_size: int | None = None
    checksum: str | None = None
    status: DocumentStatus = DocumentStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    processed_at: datetime | None = None
    error_message: str | None = None
    version: int = 1

    def __post_init__(self) -> None:
        """Post-initialization validation."""
        if not self.id:
            self.id = str(uuid.uuid4())

        if not self.content:
            raise ISAValidationError(
                "Document content cannot be empty", field="content"
            )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "document_type": self.document_type.value,
            "metadata": self.metadata.to_dict(),
            "file_path": str(self.file_path) if self.file_path else None,
            "file_size": self.file_size,
            "checksum": self.checksum,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "processed_at": (
                self.processed_at.isoformat() if self.processed_at else None
            ),
            "error_message": self.error_message,
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Document":
        """Create from dictionary."""
        # Convert string values back to enums
        if isinstance(data.get("document_type"), str):
            data["document_type"] = DocumentType(data["document_type"])
        if isinstance(data.get("status"), str):
            data["status"] = DocumentStatus(data["status"])

        # Convert datetime strings
        for field in ["created_at", "updated_at", "processed_at"]:
            if isinstance(data.get(field), str):
                data[field] = datetime.fromisoformat(data[field])

        # Convert Path
        if data.get("file_path"):
            data["file_path"] = Path(data["file_path"])

        # Convert metadata
        if isinstance(data.get("metadata"), dict):
            data["metadata"] = DocumentMetadata.from_dict(data["metadata"])

        return cls(**data)


@dataclass
class DocumentChunk:
    """Document chunk for processing."""

    id: str
    document_id: str
    content: str
    chunk_index: int
    start_index: int
    end_index: int
    metadata: dict[str, Any] = field(default_factory=dict)
    embedding: list[float] | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Post-initialization validation."""
        if not self.id:
            self.id = str(uuid.uuid4())

        if not self.content:
            raise ISAValidationError("Chunk content cannot be empty", field="content")

        if self.start_index < 0 or self.end_index < 0:
            raise ISAValidationError(
                "Chunk indices must be non-negative", field="indices"
            )

        if self.start_index >= self.end_index:
            raise ISAValidationError(
                "Start index must be less than end index", field="indices"
            )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "document_id": self.document_id,
            "content": self.content,
            "chunk_index": self.chunk_index,
            "start_index": self.start_index,
            "end_index": self.end_index,
            "metadata": self.metadata,
            "embedding": self.embedding,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DocumentChunk":
        """Create from dictionary."""
        # Convert datetime
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])

        return cls(**data)


@dataclass
class Vector:
    """Vector representation."""

    id: str
    vector: list[float]
    metadata: dict[str, Any] = field(default_factory=dict)
    document_id: str | None = None
    chunk_id: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Post-initialization validation."""
        if not self.id:
            self.id = str(uuid.uuid4())

        if not self.vector:
            raise ISAValidationError("Vector cannot be empty", field="vector")

        if not all(isinstance(x, int | float) for x in self.vector):
            raise ISAValidationError(
                "Vector must contain only numeric values", field="vector"
            )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "vector": self.vector,
            "metadata": self.metadata,
            "document_id": self.document_id,
            "chunk_id": self.chunk_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Vector":
        """Create from dictionary."""
        # Convert datetime
        for field in ["created_at", "updated_at"]:
            if isinstance(data.get(field), str):
                data[field] = datetime.fromisoformat(data[field])

        return cls(**data)


@dataclass
class SearchResult:
    """Search result."""

    vector_id: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)
    document_id: str | None = None
    chunk_id: str | None = None
    content: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "vector_id": self.vector_id,
            "score": self.score,
            "metadata": self.metadata,
            "document_id": self.document_id,
            "chunk_id": self.chunk_id,
            "content": self.content,
        }


@dataclass
class SearchQuery:
    """Search query."""

    query: str
    top_k: int = 10
    threshold: float = 0.0
    filters: dict[str, Any] = field(default_factory=dict)
    metadata_fields: list[str] = field(default_factory=list)

    def validate(self) -> None:
        """Validate the search query."""
        if not self.query:
            raise ISAValidationError("Query cannot be empty", field="query")

        if self.top_k <= 0:
            raise ISAValidationError("top_k must be positive", field="top_k")

        if not 0 <= self.threshold <= 1:
            raise ISAValidationError(
                "threshold must be between 0 and 1", field="threshold"
            )


@dataclass
class IngestionResult:
    """Document ingestion result."""

    document_id: str
    success: bool
    chunks_created: int = 0
    vectors_created: int = 0
    error_message: str | None = None
    processing_time_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "document_id": self.document_id,
            "success": self.success,
            "chunks_created": self.chunks_created,
            "vectors_created": self.vectors_created,
            "error_message": self.error_message,
            "processing_time_ms": self.processing_time_ms,
            "metadata": self.metadata,
        }


@dataclass
class ProcessingJob:
    """Processing job."""

    id: str
    job_type: str
    status: str
    priority: int = 1
    data: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error_message: str | None = None
    retry_count: int = 0
    max_retries: int = 3

    def __post_init__(self) -> None:
        """Post-initialization validation."""
        if not self.id:
            self.id = str(uuid.uuid4())

        if not self.job_type:
            raise ISAValidationError("Job type cannot be empty", field="job_type")

        if self.priority < 1:
            raise ISAValidationError("Priority must be positive", field="priority")

        if self.retry_count < 0:
            raise ISAValidationError(
                "Retry count cannot be negative", field="retry_count"
            )

        if self.max_retries < 0:
            raise ISAValidationError(
                "Max retries cannot be negative", field="max_retries"
            )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "job_type": self.job_type,
            "status": self.status,
            "priority": self.priority,
            "data": self.data,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "error_message": self.error_message,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProcessingJob":
        """Create from dictionary."""
        # Convert datetime
        for field in ["created_at", "started_at", "completed_at"]:
            if isinstance(data.get(field), str):
                data[field] = datetime.fromisoformat(data[field])

        return cls(**data)


@dataclass
class DataCatalog:
    """Data catalog entry."""

    id: str
    name: str
    description: str | None = None
    data_type: str = "unknown"
    source: str | None = None
    location: str | None = None
    schema: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: datetime | None = None
    access_count: int = 0
    tags: list[str] = field(default_factory=list)
    owner: str | None = None
    size_bytes: int | None = None
    row_count: int | None = None

    def __post_init__(self) -> None:
        """Post-initialization validation."""
        if not self.id:
            self.id = str(uuid.uuid4())

        if not self.name:
            raise ISAValidationError("Name cannot be empty", field="name")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "data_type": self.data_type,
            "source": self.source,
            "location": self.location,
            "schema": self.schema,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_accessed": (
                self.last_accessed.isoformat() if self.last_accessed else None
            ),
            "access_count": self.access_count,
            "tags": self.tags,
            "owner": self.owner,
            "size_bytes": self.size_bytes,
            "row_count": self.row_count,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DataCatalog":
        """Create from dictionary."""
        # Convert datetime
        for field in ["created_at", "updated_at", "last_accessed"]:
            if isinstance(data.get(field), str):
                data[field] = datetime.fromisoformat(data[field])

        return cls(**data)


@dataclass
class ModelCard:
    """Model card for AI models."""

    id: str
    name: str
    description: str | None = None
    model_type: str = "unknown"
    version: str = "1.0.0"
    framework: str | None = None
    architecture: str | None = None
    parameters: int | None = None
    training_data: str | None = None
    performance_metrics: dict[str, Any] = field(default_factory=dict)
    limitations: list[str] = field(default_factory=list)
    use_cases: list[str] = field(default_factory=list)
    ethical_considerations: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    owner: str | None = None
    license: str | None = None
    url: str | None = None

    def __post_init__(self) -> None:
        """Post-initialization validation."""
        if not self.id:
            self.id = str(uuid.uuid4())

        if not self.name:
            raise ISAValidationError("Name cannot be empty", field="name")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "model_type": self.model_type,
            "version": self.version,
            "framework": self.framework,
            "architecture": self.architecture,
            "parameters": self.parameters,
            "training_data": self.training_data,
            "performance_metrics": self.performance_metrics,
            "limitations": self.limitations,
            "use_cases": self.use_cases,
            "ethical_considerations": self.ethical_considerations,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "owner": self.owner,
            "license": self.license,
            "url": self.url,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ModelCard":
        """Create from dictionary."""
        # Convert datetime
        for field in ["created_at", "updated_at"]:
            if isinstance(data.get(field), str):
                data[field] = datetime.fromisoformat(data[field])

        return cls(**data)


# Utility functions for model operations
def validate_document_type(file_path: str | Path) -> DocumentType:
    """
    Validate and determine document type from file path.

    Args:
        file_path: File path

    Returns:
        DocumentType enum value

    Raises:
        ISAValidationError: If file type is not supported
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)

    extension = file_path.suffix.lower()

    type_mapping = {
        ".txt": DocumentType.TEXT,
        ".md": DocumentType.MARKDOWN,
        ".markdown": DocumentType.MARKDOWN,
        ".pdf": DocumentType.PDF,
        ".html": DocumentType.HTML,
        ".htm": DocumentType.HTML,
        ".json": DocumentType.JSON,
        ".yaml": DocumentType.YAML,
        ".yml": DocumentType.YAML,
        ".csv": DocumentType.CSV,
        ".xml": DocumentType.XML,
        ".py": DocumentType.CODE,
        ".js": DocumentType.CODE,
        ".ts": DocumentType.CODE,
        ".java": DocumentType.CODE,
        ".cpp": DocumentType.CODE,
        ".c": DocumentType.CODE,
        ".go": DocumentType.CODE,
        ".rs": DocumentType.CODE,
        ".jpg": DocumentType.IMAGE,
        ".jpeg": DocumentType.IMAGE,
        ".png": DocumentType.IMAGE,
        ".gif": DocumentType.IMAGE,
        ".svg": DocumentType.IMAGE,
        ".mp4": DocumentType.VIDEO,
        ".avi": DocumentType.VIDEO,
        ".mov": DocumentType.VIDEO,
        ".mp3": DocumentType.AUDIO,
        ".wav": DocumentType.AUDIO,
        ".flac": DocumentType.AUDIO,
    }

    if extension in type_mapping:
        return type_mapping[extension]

    return DocumentType.UNKNOWN


def create_document_from_file(
    file_path: str | Path,
    content: str,
    metadata: DocumentMetadata | None = None,
) -> Document:
    """
    Create a document from a file.

    Args:
        file_path: File path
        content: File content
        metadata: Optional metadata

    Returns:
        Document instance

    Raises:
        ISAValidationError: If document creation fails
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)

    if not file_path.exists():
        raise ISAValidationError(f"File does not exist: {file_path}", field="file_path")

    document_type = validate_document_type(file_path)

    if metadata is None:
        metadata = DocumentMetadata()

    # Set default metadata from file
    if not metadata.title:
        metadata.title = file_path.stem

    if not metadata.source:
        metadata.source = str(file_path)

    # Get file size
    try:
        file_size = file_path.stat().st_size
    except OSError:
        file_size = None

    return Document(
        id=str(uuid.uuid4()),
        content=content,
        document_type=document_type,
        metadata=metadata,
        file_path=file_path,
        file_size=file_size,
    )


@dataclass
class Agent:
    """Agent representation."""
    id: str
    name: str
    type: str
    status: str = "inactive"
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Workflow:
    """Workflow representation."""
    id: str
    name: str
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.utcnow)


class AgentStatus(Enum):
    """Agent status enumeration."""
    IDLE = "idle"
    ACTIVE = "active"
    WORKING = "working"
    ERROR = "error"
    STOPPED = "stopped"


class AgentCapability(Enum):
    """Agent capability enumeration."""
    INFORMATION_RETRIEVAL = "information_retrieval"
    DOCUMENT_ANALYSIS = "document_analysis"
    SEARCH = "search"
    SUMMARIZATION = "summarization"
    QUESTION_ANSWERING = "question_answering"


class AgentType(Enum):
    """Agent type enumeration."""
    RESEARCH = "research"
    ANALYSIS = "analysis"
    COORDINATION = "coordination"


class TaskType(Enum):
    """Task type enumeration."""
    RESEARCH = "research"
    ANALYSIS = "analysis"
    SEARCH = "search"


class MessageType(Enum):
    """Message type enumeration."""
    TASK = "task"
    RESULT = "result"
    QUERY = "query"
    RESPONSE = "response"
    COMMAND = "command"
    STATUS = "status"


class TaskPriority(Enum):
    """Task priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(Enum):
    """Task status enumeration."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Message:
    """Message representation."""
    message_id: str
    sender_id: str
    receiver_id: str
    message_type: MessageType
    content: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Task:
    """Task representation."""
    task_id: str
    type: TaskType
    data: dict[str, Any]
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    assigned_agent_id: str | None = None
    assigned_at: datetime | None = None
    completed_at: datetime | None = None
    error_message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "task_id": self.task_id,
            "type": self.type.value,
            "data": self.data,
            "priority": self.priority.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "assigned_agent_id": self.assigned_agent_id,
            "assigned_at": self.assigned_at.isoformat() if self.assigned_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Task":
        """Create from dictionary."""
        # Convert string values back to enums
        if isinstance(data.get("type"), str):
            data["type"] = TaskType(data["type"])
        if isinstance(data.get("priority"), str):
            data["priority"] = TaskPriority(data["priority"])
        if isinstance(data.get("status"), str):
            data["status"] = TaskStatus(data["status"])

        # Convert datetime strings
        for field in ["created_at", "assigned_at", "completed_at"]:
            if isinstance(data.get(field), str):
                data[field] = datetime.fromisoformat(data[field])

        return cls(**data)
