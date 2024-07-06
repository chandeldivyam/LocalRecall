import os
import google.generativeai as genai
from abc import ABC, abstractmethod
from typing import List
import requests
import json


class EmbeddingStrategy(ABC):
    @abstractmethod
    def create_embedding(self, text: str) -> List[float]:
        pass

    @abstractmethod
    def create_embedding_retrieval(self, text: str) -> List[float]:
        pass

class GeminiEmbeddingStrategy(EmbeddingStrategy):
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        genai.configure(api_key=api_key)

    def create_embedding(self, text: str) -> List[float]:
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="semantic_similarity"
        )
        return result['embedding']
    
    def create_embedding_retrieval(self, text: str) -> List[float]:
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
        )
        return result['embedding']
    
class LocalEmbeddingStrategy(EmbeddingStrategy):
    def __init__(self, base_url: str = "http://localhost:11434", timeout: int = 40):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self._check_service_availability()

    def _check_service_availability(self):
        try:
            response = requests.get(f"{self.base_url}/", timeout=self.timeout)
            response.raise_for_status()
        except Exception as e:
            raise Exception(f"Failed to connect to the embedding service at {self.base_url}. Error: {str(e)}")

    def create_embedding(self, text: str) -> List[float]:
        if not text.strip():
            raise ValueError("Input text cannot be empty or whitespace only.")

        url = f"{self.base_url}/api/embeddings"
        payload = json.dumps({
            "model": "mxbai-embed-large",
            "prompt": text
        })
        headers = {
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, headers=headers, data=payload, timeout=self.timeout)
            response.raise_for_status()
            embedding = response.json().get("embedding")
            
            if not embedding or not isinstance(embedding, list):
                raise ValueError("Invalid embedding format received from the server.")
            
            return embedding

        except Exception as e:
            raise Exception(f"Failed to create embedding. Error: {str(e)}")

    def create_embedding_retrieval(self, text: str) -> List[float]:
        if not text.strip():
            raise ValueError("Input text cannot be empty or whitespace only.")

        url = f"{self.base_url}/api/embeddings"
        payload = json.dumps({
            "model": "mxbai-embed-large",
            "prompt": text
        })
        headers = {
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, headers=headers, data=payload, timeout=self.timeout)
            response.raise_for_status()
            embedding = response.json().get("embedding")
            
            if not embedding or not isinstance(embedding, list):
                raise ValueError("Invalid embedding format received from the server.")
            
            return embedding

        except Exception as e:
            raise Exception(f"Failed to create embedding. Error: {str(e)}")

    def __repr__(self):
        return f"LocalEmbeddingStrategy(base_url='{self.base_url}')"