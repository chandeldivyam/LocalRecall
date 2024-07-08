from transformers import AutoProcessor, AutoModelForCausalLM
import torch
from PIL import Image
from typing import Tuple

class MLModel:
    def __init__(self, model_id: str = 'microsoft/Florence-2-large'):
        """
        Initialize the MLModel with the specified model.

        Args:
            model_id (str): The identifier for the pre-trained model.
        """
        self.model_id = model_id
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = AutoModelForCausalLM.from_pretrained(self.model_id, trust_remote_code=True).to(self.device).eval()
        self.processor = AutoProcessor.from_pretrained(self.model_id, trust_remote_code=True)

    def generate_caption(self, image: Image.Image, action_type: str = "<MORE_DETAILED_CAPTION>") -> str:
        """
        Generate a caption for the given image.

        Args:
            image (PIL.Image.Image): The input image.

        Returns:
            str: The generated caption.
        """
        prompt = action_type
        inputs = self.processor(text=prompt, images=image, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            generated_ids = self.model.generate(
                input_ids=inputs["input_ids"],
                pixel_values=inputs["pixel_values"],
                max_new_tokens=200,
                num_beams=3
            )
        
        generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
        parsed_answer = self.processor.post_process_generation(generated_text, task=prompt, image_size=(image.width, image.height))
        
        return parsed_answer

model = MLModel()
