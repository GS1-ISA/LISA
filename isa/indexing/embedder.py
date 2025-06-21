import numpy as np

class Embedder:
    def __init__(self, model_name: str = "text-embedding-004"):
        self.model_name = model_name
        # In a real scenario, this would initialize a connection to an embedding service (e.g., Genkit, Vertex AI)

    def generate_embedding(self, text: str) -> list[float]:
        """
        Generates a vector embedding for the given text.
        This is a placeholder implementation. In a real system, this would call an actual embedding model.
        """
        # For demonstration, return a fixed-size dummy embedding
        # A real embedding would be context-dependent and higher dimensional
        embedding_size = 768 # Common embedding size, e.g., for text-embedding-004
        np.random.seed(hash(text) % (2**32 - 1)) # Simple way to make dummy embedding somewhat "unique" per text
        dummy_embedding = np.random.rand(embedding_size).tolist()
        return dummy_embedding

# Example Usage
if __name__ == "__main__":
    embedder = Embedder()
    text1 = "This is a sample document chunk."
    text2 = "Another piece of text for embedding."
    
    embedding1 = embedder.generate_embedding(text1)
    embedding2 = embedder.generate_embedding(text2)
    
    print(f"Embedding for '{text1[:30]}...': {embedding1[:5]}...") # Print first 5 elements
    print(f"Embedding for '{text2[:30]}...': {embedding2[:5]}...") # Print first 5 elements
    print(f"Embedding size: {len(embedding1)}")