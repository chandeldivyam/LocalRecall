import os
import google.generativeai as genai
from abc import ABC, abstractmethod
from .data_manager import DataManager, VectorDataManager
import json
from typing import List
from .embedding_processor import GeminiEmbeddingStrategy, LocalEmbeddingStrategy
import requests
from typing import Optional

class VisionStrategy(ABC):
    @abstractmethod
    def process_image(self, image_path, prompt):
        pass

    def generate_prompt(self, activity):
        current_activity = json.loads(activity.get("active_window", "{}"))
        self.prompt = f"""Please generate the caption for the screenshot provided. Try to focus on the apps being used on the screen. From the computer, this the app currntly in the use:
title: f{current_activity.get("title", "")}
process: f{current_activity.get("process_name", "")}
"""
        return self.prompt

class GoogleGeminiStrategy(VisionStrategy):
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={
                "temperature": 1,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 128,
                "response_mime_type": "text/plain",
            }
        )

    def process_image(self, image_path, prompt):
        file = genai.upload_file(image_path, mime_type="image/jpeg")
        chat_session = self.model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [
                        file,
                        prompt,
                    ],
                }
            ]
        )
        response = chat_session.send_message("Analyze the image")
        return response.text


class LocalModelStrategy(VisionStrategy):
    def __init__(self, url: str = "http://localhost:8989/generate_caption", timeout: int = 40):
        self.url = url
        self.timeout = timeout

    def process_image(self, image_path: str, prompt: str) -> str:
        if not os.path.exists(image_path):
            raise Exception("Error: Image file does not exist")

        if not os.path.isfile(image_path):
            raise Exception("Error: Provided path is not a file")

        try:
            with open(image_path, "rb") as image_file:
                files = {"file": image_file}
                response = requests.post(self.url, files=files, timeout=self.timeout)
            
            response.raise_for_status()  # Raises an HTTPError for bad responses

            caption_data = response.json()
            detailed_caption = caption_data.get('caption', {}).get('<MORE_DETAILED_CAPTION>')
            
            if not detailed_caption:
                return "Error: No detailed caption found in response"

            return detailed_caption

        except Exception as e:
            raise e

class VisionProcessor:
    def __init__(self, strategy: str = "google"):
        self.data_manager = DataManager()
        if strategy == "google":
            self.strategy = GoogleGeminiStrategy()
            self.embedding_strategy = GeminiEmbeddingStrategy()
        elif strategy == "local":
            self.strategy = LocalModelStrategy()
            self.embedding_strategy = LocalEmbeddingStrategy()
        else:
            raise ValueError("Invalid strategy")
        self.vector_data_manager = VectorDataManager(embedding_strategy=self.embedding_strategy)

    def process_unprocessed_activities(self):
        activities = self.data_manager.get_unprocessed_activities()
        for activity in activities:
            screenshot_path = activity['screenshot']
            prompt = self.strategy.generate_prompt(activity=activity)
            current_activity = json.loads(activity.get("active_window", "{}"))
            analysis = f"Current Activity Title: {current_activity.get('title', '')}\n" + self.strategy.process_image(screenshot_path, prompt)
            # Update activity with analysis
            activity['analysis'] = analysis
            self.data_manager.update_activity(activity['timestamp'], activity)
            self.data_manager.mark_activity_as_processed(activity['timestamp'])
            
            self.vector_data_manager.add_activity(
                timestamp=activity['timestamp'],
                created_at=activity['created_at'],
                screenshot_path=screenshot_path,
                active_window=json.loads(activity['active_window']),
                analysis=analysis
            )