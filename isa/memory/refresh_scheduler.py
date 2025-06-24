import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Callable
import json
import os

# Assuming these are available from other ISA modules
from isa.indexing.file_extractor import FileExtractor
from isa.indexing.text_chunker import TextChunker
from isa.indexing.embedder import Embedder
# from isa.core.vector_store_client import VectorStoreClient # Placeholder for actual vector store client

class RefreshScheduler:
    def __init__(self, 
                 file_extractor: FileExtractor, 
                 text_chunker: TextChunker, 
                 embedder: Embedder,
                 # vector_store_client: VectorStoreClient, # Uncomment when actual client is ready
                 refresh_interval_hours: float = 24.0,
                 metadata_store_path: str = "isa/memory/refresh_metadata.json"):
        
        self.file_extractor = file_extractor
        self.text_chunker = text_chunker
        self.embedder = embedder
        # self.vector_store_client = vector_store_client # Uncomment when actual client is ready
        self.refresh_interval = timedelta(hours=refresh_interval_hours)
        self.metadata_store_path = metadata_store_path
        self.knowledge_metadata: Dict[str, Any] = self._load_metadata()
        print(f"RefreshScheduler initialized with refresh interval: {self.refresh_interval}")

    def _load_metadata(self) -> Dict[str, Any]:
        """Loads knowledge metadata from a JSON file."""
        if os.path.exists(self.metadata_store_path):
            try:
                with open(self.metadata_store_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error decoding metadata JSON: {e}. Starting with empty metadata.")
                return {}
        return {}

    def _save_metadata(self):
        """Saves knowledge metadata to a JSON file."""
        os.makedirs(os.path.dirname(self.metadata_store_path), exist_ok=True)
        with open(self.metadata_store_path, 'w') as f:
            json.dump(self.knowledge_metadata, f, indent=2)

    def _calculate_content_hash(self, content: str) -> str:
        """Calculates SHA256 hash of the content for change detection."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def _process_source(self, source_identifier: str, content: str, source_url: str | None = None):
        """
        Processes content from a source: chunks, embeds, and stores.
        Includes data versioning.
        """
        print(f"Processing source: {source_identifier}")
        current_hash = self._calculate_content_hash(content)
        last_processed_info = self.knowledge_metadata.get(source_identifier, {})

        if last_processed_info.get("content_hash") == current_hash:
            print(f"Content for {source_identifier} unchanged. Skipping re-processing.")
            return

        print(f"Content for {source_identifier} changed or new. Re-processing...")
        
        # Chunking
        # Assuming content_type can be inferred or passed. For simplicity, defaulting to plain_text.
        # In a real scenario, file_extractor might provide content type.
        chunks = self.text_chunker.chunk_document(content, file_type="plain_text") # Adjust file_type as needed

        # Embedding and Storage
        new_embeddings_count = 0
        for i, chunk_data in enumerate(chunks):
            chunk_content = chunk_data["content"]
            chunk_metadata = chunk_data["metadata"]
            
            embedding = self.embedder.generate_embedding(chunk_content)
            
            # Prepare metadata for vector store, including versioning info
            vector_metadata = {
                "source_identifier": source_identifier,
                "source_url": source_url,
                "timestamp": datetime.now().isoformat(),
                "content_hash": current_hash,
                "chunk_index": i,
                **chunk_metadata # Include chunk-specific metadata
            }
            
            # In a real system, upsert to vector store
            # self.vector_store_client.upsert(
            #     vectors=[{"id": f"{source_identifier}_chunk_{i}_{current_hash}", "values": embedding, "metadata": vector_metadata}]
            # )
            new_embeddings_count += 1
            # print(f"  - Stored chunk {i+1} for {source_identifier}")

        # Update metadata
        self.knowledge_metadata[source_identifier] = {
            "last_processed": datetime.now().isoformat(),
            "content_hash": current_hash,
            "source_url": source_url,
            "total_chunks": len(chunks),
            "status": "processed_successfully"
        }
        self._save_metadata()
        print(f"Finished processing {source_identifier}. Stored {new_embeddings_count} new embeddings.")

    def schedule_refresh(self, sources: Dict[str, str]):
        """
        Schedules and performs refresh for given sources.
        Sources is a dict: {source_identifier: url_or_path}
        """
        print(f"Starting scheduled knowledge refresh at {datetime.now()}")
        for identifier, source_loc in sources.items():
            last_processed_time_str = self.knowledge_metadata.get(identifier, {}).get("last_processed")
            last_processed_time = datetime.fromisoformat(last_processed_time_str) if last_processed_time_str else None

            if last_processed_time and (datetime.now() - last_processed_time) < self.refresh_interval:
                print(f"Skipping {identifier}: last processed less than {self.refresh_interval} ago.")
                continue

            content = None
            source_url = None
            if source_loc.startswith("http://") or source_loc.startswith("https://"):
                print(f"Fetching web content from {source_loc}")
                content = self.file_extractor.extract_from_url(source_loc)
                source_url = source_loc
            elif os.path.exists(os.path.join(self.file_extractor.base_path, source_loc)):
                print(f"Extracting local file content from {source_loc}")
                content = self.file_extractor.extract_content(source_loc)
            else:
                print(f"Source {source_loc} not found or unsupported.")
                continue

            if content:
                self._process_source(identifier, content, source_url)
            else:
                print(f"Failed to retrieve content for {identifier} from {source_loc}")
        print(f"Finished scheduled knowledge refresh at {datetime.now()}")

    def run_scheduler_loop(self, sources: Dict[str, str], interval_seconds: int = 3600):
        """
        Runs the scheduler in a continuous loop.
        This is a simplified loop for demonstration. In production, use a proper scheduler like APScheduler.
        """
        print(f"Starting refresh scheduler loop. Checking every {interval_seconds} seconds.")
        while True:
            self.schedule_refresh(sources)
            print(f"Next refresh in {interval_seconds} seconds...")
            time.sleep(interval_seconds)

# Example Usage (for testing purposes)
if __name__ == "__main__":
    # Initialize dependencies
    base_path = os.getcwd() # Assuming current working directory is the base
    extractor = FileExtractor(base_path)
    chunker = TextChunker(max_chunk_size=200, overlap=20)
    embedder = Embedder()
    # vector_client = VectorStoreClient(...) # Initialize your actual vector store client here

    # Define some volatile information sources
    # For local files, ensure they exist in your workspace or provide full paths
    # For URLs, ensure they are accessible
    test_sources = {
        "readme_doc": "README.md",
        "example_html_page": "http://example.com",
        "dummy_json_api": "https://jsonplaceholder.typicode.com/todos/1",
        "non_existent_file": "path/to/non_existent_file.txt"
    }

    # Create a dummy README.md if it doesn't exist for testing local file extraction
    if not os.path.exists("README.md"):
        with open("README.md", "w") as f:
            f.write("# Test README\n\nThis is a test markdown file for the refresh scheduler.")
        print("Created dummy README.md for testing.")

    # Initialize the scheduler
    scheduler = RefreshScheduler(
        file_extractor=extractor,
        text_chunker=chunker,
        embedder=embedder,
        # vector_store_client=vector_client, # Pass actual client
        refresh_interval_hours=0.01 # Very short interval for testing (e.g., 36 seconds)
    )
    # Ensure the metadata directory exists for the example usage
    os.makedirs(os.path.dirname(scheduler.metadata_store_path), exist_ok=True)
    
    # Create a dummy README.md if it doesn't exist for testing local file extraction
    if not os.path.exists("README.md"):
        with open("README.md", "w") as f:
            f.write("# Test README\n\nThis is a test markdown file for the refresh scheduler.")
        print("Created dummy README.md for testing.")

    # Initialize the scheduler
    scheduler = RefreshScheduler(
        file_extractor=extractor,
        text_chunker=chunker,
        embedder=embedder,
        # vector_store_client=vector_client, # Pass actual client
        refresh_interval_hours=0.01 # Very short interval for testing (e.g., 36 seconds)
    )
    )

    # To run the scheduler once:
    print("\n--- Running scheduler once ---")
    scheduler.schedule_refresh(test_sources)

    # To run the scheduler in a loop (uncomment with caution, will run indefinitely)
    # print("\n--- Running scheduler in a loop (Ctrl+C to stop) ---")
    # scheduler.run_scheduler_loop(test_sources, interval_seconds=60) # Check every 60 seconds