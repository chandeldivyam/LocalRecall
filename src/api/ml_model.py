from transformers import AutoProcessor, AutoModelForCausalLM
import torch

class MLModel:
    def __init__(self):
        self.model_id = 'microsoft/Florence-2-large'
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = AutoModelForCausalLM.from_pretrained(self.model_id, trust_remote_code=True).to(self.device).eval()
        self.processor = AutoProcessor.from_pretrained(self.model_id, trust_remote_code=True)

    def generate_caption(self, image):
        prompt = "<MORE_DETAILED_CAPTION>"
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