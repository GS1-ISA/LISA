import os
from isa.indexing.loader import IndexDataLoader

def main():
    """
    Main function to run the project indexing process.
    """
    base_path = os.getcwd() # Assuming the script is run from the isa_workspace root
    
    print(f"Starting project indexing from base path: {base_path}")
    
    loader = IndexDataLoader(base_path=base_path)
    indexed_data = loader.load_project_data()
    
    print("\n--- Indexing Summary ---")
    print(f"Total Document Chunks Generated: {len(indexed_data['document_chunks'])}")
    print(f"Total Knowledge Graph Entities Generated: {len(indexed_data['kg_entities'])}")
    
    # In a real scenario, this data would then be pushed to a Vector Database and Knowledge Graph
    # For now, we just print a summary and some examples.
    
    if indexed_data['document_chunks']:
        print("\nFirst 5 Document Chunks (simplified view):")
        for i, chunk in enumerate(indexed_data['document_chunks'][:5]):
            print(f"  Chunk {i+1}: ID={chunk['id']}, Source={chunk['source_ref']}, Content_Snippet='{chunk['content'][:50]}...'")

    if indexed_data['kg_entities']:
        print("\nFirst 5 Knowledge Graph Entities (simplified view):")
        for i, entity in enumerate(indexed_data['kg_entities'][:5]):
            print(f"  Entity {i+1}: ID={entity['id']}, Type={entity['type']}, Name={entity['name']}")

    print("\nIndexing process completed. Data is ready for storage in Vector DB and KG.")

if __name__ == "__main__":
    main()