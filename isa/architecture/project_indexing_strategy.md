# Architectural Proposal: Project Directory Indexing for Enhanced Knowledge Retrieval

### 1. Scope of Indexing

The indexing strategy will encompass a comprehensive range of information from the entire project directory, excluding files and directories specified in `.rooignore`. The goal is to create a rich, multi-modal representation of the project's knowledge.

*   **File Paths and Structure:** Indexing of all file and directory paths to understand the project's organizational hierarchy. This includes relative paths, file types, and directory names.
*   **File Content (Textual):** Full-text indexing of all readable text-based files (e.g., `.md`, `.txt`, `.json`, `.yaml`, `.js`, `.ts`, `.py`, `.sh`, `.css`, `.html`, `.xml`, configuration files, log files, documentation). This will capture raw information, comments, and prose.
*   **Code Definitions and Structure:** For source code files, extract and index:
    *   Function, class, method, and variable names.
    *   Their signatures, parameters, and return types.
    *   Docstrings/comments associated with definitions.
    *   Import/export relationships between modules.
    *   High-level architectural patterns (e.g., microservices, components).
*   **Metadata:**
    *   File creation/modification timestamps.
    *   File size.
    *   Author information (if available, e.g., from Git history).
    *   Language/technology inferred from file extension or content.
*   **Semantic Relationships:** Identification and indexing of explicit and implicit relationships between different parts of the codebase and documentation, such as:
    *   References between files (e.g., imports, links).
    *   Mentions of concepts defined in the `isa/context/glossary.md`.
    *   Dependencies between modules or services.
    *   Cross-references within documentation.
*   **Operational Data & Logs:** Key information from structured log files (e.g., `isa/logs/agent_task_history.json`, `project_journal.md`) to track agent behavior, task outcomes, and system health.

### 2. Indexing Mechanism

The indexing mechanism will leverage an ELTVRE (Extract, Load, Transform, Validate, Refine, Enrich) pipeline, as outlined in `isa/architecture/eltvre_pipeline.md`, adapted for codebase indexing.

*   **Recursive File Traversal:** A dedicated indexing service will recursively traverse the project directory, respecting `.rooignore` rules.
*   **Content Extraction:**
    *   **Text Files:** Direct reading of file content.
    *   **Binary/Proprietary Formats (e.g., PDF, DOCX):** Utilize specialized parsers (e.g., `pdfminer.six`, `python-docx`) to extract text. For images within documents, OCR (Optical Character Recognition) may be employed.
*   **Code Parsing and AST Analysis:** For programming language files, use Abstract Syntax Tree (AST) parsers (e.g., `tree-sitter`, `esprima` for JS/TS, `ast` module for Python) to extract structured code definitions, relationships, and comments. This allows for semantic understanding beyond simple text matching.
*   **Metadata Extraction:** File system APIs will be used to extract metadata like timestamps and size. Git APIs can be used to extract author information.
*   **Chunking and Embedding:**
    *   **Textual Content:** Documents and code files will be chunked into manageable segments (e.g., paragraphs, functions, classes) suitable for embedding.
    *   **Embedding Generation:** Each chunk will be converted into a high-dimensional vector embedding using a suitable embedding model (e.g., `text-embedding-004` as mentioned in `docs/udm/03-Knowledge-Data-Management.md`). These embeddings capture the semantic meaning of the content.
*   **Relationship Extraction:**
    *   **Rule-based:** Regex patterns and static analysis for identifying imports, function calls, and explicit references.
    *   **LLM-based:** For more complex semantic relationships or implicit connections, an LLM can be used to extract entities and relationships from textual content (e.g., identifying "defines" or "appliesTo" relationships from documentation).

### 3. Storage Solution

A hybrid storage approach combining a Vector Database and a Knowledge Graph will provide optimal capabilities for both semantic search and structured reasoning, aligning with existing architectural plans (`isa/architecture/vector_data_storage.md`, `isa/architecture/knowledge_graph_implementation.md`, `docs/udm/03-Knowledge-Data-Management.md`).

*   **Primary Storage: Vector Database (e.g., AlloyDB AI pgvector / Vertex AI Vector Search)**
    *   **Purpose:** Store vector embeddings of all indexed content chunks.
    *   **Justification:**
        *   **Scalability:** Designed for high-volume, high-dimensional vector storage and retrieval.
        *   **Query Capabilities:** Enables efficient semantic similarity search (e.g., finding relevant code snippets or documentation based on natural language queries).
        *   **Integration:** Aligns with the existing `answerGs1QuestionsWithVectorSearch` flow and the `Context7` concept for advanced long-term context management.
        *   **RAG Support:** Directly supports Retrieval-Augmented Generation by providing relevant context to LLMs.
*   **Secondary Storage: Knowledge Graph (e.g., AlloyDB AI or dedicated graph database on GCP)**
    *   **Purpose:** Store structured metadata, code definitions, and semantic relationships between entities (files, functions, concepts, tasks).
    *   **Justification:**
        *   **Structured Reasoning:** Enables complex queries about project structure, dependencies, and logical connections (e.g., "Show all files that import `ModelManager`," "What documentation relates to `ELTVRE`?").
        *   **Contextual Understanding:** Provides a symbolic layer of knowledge that complements the semantic understanding from the vector store, crucial for NeSy AI approaches.
        *   **Traceability:** Helps in tracing changes, understanding impact, and navigating the codebase.
        *   **Integration:** Aligns with the existing Knowledge Graph implementation design.
*   **Metadata Store (e.g., PostgreSQL/Firestore):** A traditional database to store raw file metadata (paths, timestamps, sizes) and pointers to the vector and graph entries. This provides a robust and easily queryable source for basic file system information.

```mermaid
graph TD
    A[Project Directory] --> B(File Traversal & Filtering);
    B --> C{File Type?};
    C -- Text/Code --> D[Content Extraction & Parsing];
    C -- Binary/PDF --> E[Specialized Parsers];
    D --> F[Code Definition Extraction];
    E --> G[Text Content];
    F --> H[Structured Code Data];
    G & H --> I[Chunking & Embedding];
    I --> J[Vector Database];
    F --> K[Relationship Extraction];
    K --> L[Knowledge Graph];
    B --> M[Metadata Extraction];
    M --> N[Metadata Store];
    J & L & N --> O[Indexed Project Knowledge];
    O --> P[Roo Modes (Search, RAG, Analysis, Debugging)];
```

### 4. Update Strategy

Maintaining an up-to-date index is crucial for its utility. A hybrid approach combining real-time monitoring for critical changes and scheduled re-indexing for comprehensive updates will be employed.

*   **Real-time Monitoring (for critical files/directories):**
    *   **Mechanism:** Utilize file system event monitoring (e.g., `watchdog` in Python, `fs.watch` in Node.js) to detect `create`, `modify`, `delete`, and `rename` events.
    *   **Scope:** Initially, focus on core `isa/` directories, `src/` code, and key documentation files (`docs/`, `CHANGELOG.md`).
    *   **Process:** Upon detection, trigger a targeted re-indexing of the affected file(s) or directory. This involves re-extracting content, re-generating embeddings, and updating the vector database and knowledge graph.
*   **Scheduled Re-indexing (for full consistency):**
    *   **Mechanism:** A daily or weekly scheduled job (e.g., using cron or a cloud scheduler) to perform a full traversal and re-indexing of the entire project directory.
    *   **Process:** This ensures that any missed changes or inconsistencies are resolved. It can also be optimized to only process files that have changed since the last full index (using timestamps or content hashes).
*   **Version Control Integration:** Integrate with Git hooks (e.g., `post-commit`, `post-merge`) to trigger partial re-indexing of changed files after a commit or merge operation. This ensures the index reflects the latest committed state.
*   **Manual Trigger:** Provide a command-line tool or internal Roo function to manually trigger a full or partial re-indexing when needed (e.g., after a large refactoring or initial setup).

### 5. Integration Points

The indexed project directory will serve as a central knowledge base, significantly enhancing the capabilities of various Roo modes.

*   **Enhanced Search (All Modes):**
    *   **Semantic Search:** Users (and Roo itself) can query the project using natural language (e.g., "Find code related to GS1 product identification," "Show documentation on data ingestion pipelines"). The vector database will return semantically similar results.
    *   **Structured Search:** Query the knowledge graph for specific code definitions, dependencies, or relationships (e.g., "List all functions that call `ModelManager`," "Show all markdown files discussing `RAG`").
*   **Retrieval-Augmented Generation (RAG) (Code, Ask, Architect Modes):**
    *   LLMs can retrieve highly relevant code snippets, documentation sections, or architectural decisions from the indexed knowledge base to inform their responses, code generation, or problem-solving. This directly supports flows like `answerGs1QuestionsWithVectorSearch`.
*   **Code Analysis (Code, Debug Modes):**
    *   **Dependency Mapping:** Automatically generate dependency graphs for modules, functions, and services.
    *   **Impact Analysis:** Identify all affected files or components when a specific function or class is modified.
    *   **Code Comprehension:** Provide context-aware explanations of code sections by linking to related documentation or other code.
*   **Debugging and Error Resolution (Debug Mode):**
    *   **Contextual Error Lookup:** When an error occurs, automatically search the index for relevant code, logs, or documentation that might explain the error or suggest a fix.
    *   **Traceability:** Trace the execution flow through different parts of the codebase by leveraging the indexed relationships.
*   **Architectural Planning (Architect Mode):**
    *   **System Overview:** Quickly generate diagrams or summaries of the current system architecture based on indexed code structure and relationships.
    *   **Gap Analysis:** Identify missing documentation or unlinked components.
*   **Self-Improvement and Learning (Orchestrator Mode):**
    *   The indexed knowledge base becomes a foundational component for Roo's "self-perfecting" and "exponential adaptability" principles, allowing it to learn from its own codebase, past actions, and project evolution.

### 6. Initial Implementation Steps

A high-level outline of the first steps to implement this indexing strategy:

1.  **Define Core Schemas:**
    *   Formalize the data schemas for indexed content chunks (as per `docs/udm/03-Knowledge-Data-Management.md`) and knowledge graph entities/relationships.
    *   Prioritize key entity types (e.g., `File`, `Function`, `Class`, `Concept`, `Task`) and relationship types (e.g., `imports`, `defines`, `references`, `relatesTo`).
2.  **Select and Set Up Storage Solutions:**
    *   Finalize the choice of Vector Database (e.g., AlloyDB AI pgvector) and Knowledge Graph solution.
    *   Provision and configure the chosen databases.
3.  **Develop Initial ELTVRE Components:**
    *   **Extractor:** Implement a basic recursive file traversal and content extraction module, respecting `.rooignore`.
    *   **Parser:** Develop initial code parsers for common languages (e.g., TypeScript/JavaScript, Python) to extract function/class names and basic relationships.
    *   **Loader:** Implement logic to load extracted text chunks and metadata into the chosen Vector Database and Metadata Store.
    *   **Embedder:** Integrate with an embedding model (e.g., via Genkit) to generate and store embeddings.
4.  **Implement Initial Indexing Script:**
    *   Create a script that performs a full initial indexing of the project directory, populating the Vector Database and Metadata Store.
5.  **Develop Basic Search Interface:**
    *   Create a simple internal tool or function that allows Roo to perform semantic searches against the vector database and retrieve relevant content.
6.  **Integrate with a Core Roo Mode:**
    *   As a first integration, enhance the `Ask` mode or `answerGs1QuestionsWithVectorSearch` flow to leverage the new semantic search capabilities for answering questions about the project's codebase or documentation.
7.  **Establish Update Mechanism (Basic):**
    *   Implement a simple scheduled re-indexing job for daily updates.
8.  **Documentation and Testing:**
    *   Document the indexing process, schemas, and storage.
    *   Develop unit and integration tests for the indexing pipeline.

This phased approach allows for incremental development and validation of the indexing system, building towards a comprehensive and highly effective knowledge retrieval system for ISA.