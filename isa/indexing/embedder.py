import numpy as np
import time
from typing import List, Dict, Any, Optional
import vertexai
from vertexai.preview.language_models import TextEmbeddingModel
import os
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
import requests
from google.cloud import aiplatform # Added import

class Embedder:
    def __init__(self, model_name: str = "textembedding-gecko@001", project: Optional[str] = None, location: Optional[str] = None): # Changed model_name back to gecko
        self.model_name = model_name
        
        # Use environment variables as a fallback
        if project is None:
            project = os.environ.get("GCP_PROJECT")
        if location is None:
            location = os.environ.get("GCP_LOCATION")
            
        if not project or not location:
            raise ValueError("Google Cloud project and location must be provided either as arguments or environment variables (GCP_PROJECT, GCP_LOCATION)")

        vertexai.init(project=project, location=location)
        self.embedding_client = TextEmbeddingModel.from_pretrained(self.model_name)
        print(f"Embedder initialized with model: {self.model_name}")

    @retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(5),
           retry=retry_if_exception_type((requests.exceptions.RequestException, aiplatform.exceptions.TooManyRequests, aiplatform.exceptions.ResourceExhausted)))
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generates a vector embedding for the given text with retry logic.
        """
        try:
            # Added parameters for task_type, output_dimensionality, and autoTruncate
            embeddings = self.embedding_client.get_embeddings(
                [text],
                parameters={
                    "task_type": "RETRIEVAL_DOCUMENT",
                    "output_dimensionality": 512,
                    "autoTruncate": True # Added autoTruncate
                }
            )
            return embeddings[0].values
        except requests.exceptions.RequestException as e:
            print(f"Retrying embedding generation for text: {text[:50]}... Error: {e}")
            time.sleep(2) # Additional small delay before retry
            raise # Re-raise to allow tenacity to catch and retry
        except Exception as e:
            print(f"Non-retryable error generating embedding for text: {text[:50]}... Error: {e}")
            return []

    @retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(5),
           retry=retry_if_exception_type((requests.exceptions.RequestException, aiplatform.exceptions.TooManyRequests, aiplatform.exceptions.ResourceExhausted)))
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generates vector embeddings for a list of texts in a batch with retry logic.
        """
        try:
            # Added parameters for task_type, output_dimensionality, and autoTruncate
            embeddings = self.embedding_client.get_embeddings(
                texts,
                parameters={
                    "task_type": "RETRIEVAL_DOCUMENT",
                    "output_dimensionality": 512,
                    "autoTruncate": True # Added autoTruncate
                }
            )
            return [embedding.values for embedding in embeddings]
        except requests.exceptions.RequestException as e:
            print(f"Retrying batch embedding generation. Error: {e}")
            time.sleep(2) # Additional small delay before retry
            raise # Re-raise to allow tenacity to catch and retry
        except Exception as e:
            print(f"Non-retryable error generating batch embeddings. Error: {e}")
            return [[] for _ in texts]

# Example Usage
if __name__ == "__main__":
    # NOTE: To run this, you need to be authenticated with Google Cloud CLI
    # and have the project and location set.
    # gcloud auth application-default login
    # You can set project and location via environment variables or by passing them to the constructor.
    # export GCP_PROJECT="your-gcp-project-id"
    # export GCP_LOCATION="your-gcp-location"
    try:
        embedder = Embedder(model_name="text-embedding-004")
        
        text1 = "This is a sample document chunk."
        text2 = "Another piece of text for embedding."
        text3 = "A third piece of text."
        
        embedding1 = embedder.generate_embedding(text1)
        if embedding1:
            print(f"Embedding for '{text1[:30]}...': {embedding1[:5]}...") # Print first 5 elements
            print(f"Embedding size: {len(embedding1)}")

        batch_texts = [text1, text2, text3]
        batch_embeddings = embedder.generate_embeddings_batch(batch_texts)
        if batch_embeddings and all(batch_embeddings):
            print(f"\nGenerated {len(batch_embeddings)} embeddings in batch.")
            for i, emb in enumerate(batch_embeddings):
                print(f"Batch Embedding {i+1} for '{batch_texts[i][:30]}...': {emb[:5]}...")
    except ValueError as e:
        print(e)