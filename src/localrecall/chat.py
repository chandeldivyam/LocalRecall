import os
import google.generativeai as genai
from abc import ABC, abstractmethod
from .data_manager import DataManager, VectorDataManager
import json
from typing import List
from .embedding_processor import GeminiEmbeddingStrategy, LocalEmbeddingStrategy
import requests
from typing import Optional
from .encryption_manager import EncryptionManager
from ollama import AsyncClient

class ChatStrategy(ABC):
    def __init__(self):
        self.encryption_manager = EncryptionManager()

    _SYSTEM_INSTRUCTIONS = """You are an advanced AI assistant, similar to Jarvis from Iron Man, designed to analyze and respond to queries based on descriptions of screenshots from the user's computer activities. Your primary functions are:
- Interpret and understand the context provided by the screenshot descriptions.
- Provide detailed explanations, relevant, and actionable answers to the user's queries.
- If you are unable to come up with an answer, polity respond that you are not sure or don't know
- Do not mention that based on the documents / context provided. Just respond with the answer
- Offer suggestions or ask clarifying questions when appropriate to better assist the user.

Your goal is to be a knowledgeable, efficient, and trustworthy assistant, enhancing the user's productivity and decision-making based on their recent computer activities.
"""

    @abstractmethod
    def process_question(self, question, history, filters):
        pass

    def process_prompt(self, prompt, filters=None, history=[]):
        # TODO - Filters handling
        related_documents = self.vector_data_manager.search_activities_with_filters(
            query=prompt,
            n_results=5,
        )
        _PROMPT = ""
        for index, document in enumerate(related_documents):
            if document.get("distance", 1) > 0.5:
                continue

            _PROMPT += f"--------------DOCUMENT_{index+1}_start------"
            _PROMPT += document.get("analysis", "") + "\n"
            _PROMPT += f"--------------DOCUMENT_{index+1}_end------\n"

        _PROMPT += f"Can you please answer the following question: {prompt}\n"

        return related_documents, _PROMPT

class GoogleGeminiChat(ChatStrategy):
    def __init__(self):
        super().__init__()
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        genai.configure(api_key=api_key)
        self.vector_data_manager = VectorDataManager(embedding_strategy=GeminiEmbeddingStrategy())
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={
                "temperature": 0.2,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 128,
                "response_mime_type": "text/plain",
            },
            safety_settings=None,
            system_instruction=self._SYSTEM_INSTRUCTIONS,
        )
    
    def _format_history(self, history=[]):
        converted_history = []
        if not history:
            return converted_history
        
        for message in history:
            new_message = {"parts": [message["content"]]}
            
            if message["role"] == "system" or message["role"] == "user":
                new_message["role"] = "user"
            elif message["role"] == "assistant":
                new_message["role"] = "model"
            else:
                # Skip unknown roles
                continue
            
            converted_history.append(new_message)
        
        return converted_history
    

    async def process_question(self, question, history=[], filters=None):
        google_format_history = self._format_history(history)
        related_documents, final_prompt = self.process_prompt(question, filters, history)
        google_format_history.append({
            "role": "user",
            "parts": [final_prompt]
        })
        encrypted_images = [document.get("metadata", {}).get("screenshot_path", "") for document in related_documents]
        decrypted_images = [self.encryption_manager.decrypt_file(encrypted_image) for encrypted_image in encrypted_images]

        yield [decrypted_images[0]]
        response = await self.model.generate_content_async(contents=google_format_history, stream=True)
        async for chunk in response:
            yield chunk.text

class LocalModelChat(ChatStrategy):
    def __init__(self, model_name='llama3'):
        super().__init__()
        self.model_name = model_name
        self.client = AsyncClient()
        self.vector_data_manager = VectorDataManager(embedding_strategy=LocalEmbeddingStrategy())

    async def process_question(self, question, history=[], filters=None):
        related_documents, final_prompt = self.process_prompt(question, filters, history)
        messages = [{'role': 'system', 'content': self._SYSTEM_INSTRUCTIONS}]        
        messages.extend(history)
        messages.append({'role': 'user', 'content': final_prompt})

        encrypted_images = [document.get("metadata", {}).get("screenshot_path", "") for document in related_documents]
        decrypted_images = [self.encryption_manager.decrypt_file(encrypted_image) for encrypted_image in encrypted_images]

        yield [decrypted_images[0]]  # Yield the first decrypted image

        async for part in await self.client.chat(model=self.model_name, messages=messages, stream=True):
            yield part['message']['content']

    def _format_history(self, history=[]):
        # This method might not be necessary for Ollama, but keeping it for consistency
        return history

    
