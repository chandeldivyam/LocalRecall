from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image
import io
from .ml_model import model

router = APIRouter()

@router.post("/generate_caption")
async def generate_caption(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    caption = model.generate_caption(image)
    return JSONResponse(content={"caption": caption})

@router.get("/")
def initial_route():
    return JSONResponse(content={"message": "welcome"})