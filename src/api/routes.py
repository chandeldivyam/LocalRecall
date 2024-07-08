from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from PIL import Image
import io
from .ml_model import model
from typing import Dict
from typing import Optional

router = APIRouter()

@router.post("/generate_caption", response_model=Dict[str, str])
async def generate_caption(file: UploadFile = File(...), action_type: Optional[str] = Form(None)):
    """
    Generate a caption for the uploaded image.

    Args:
        file (UploadFile): The uploaded image file.
        action_type (Optional[str]): The type of action to perform. Defaults to None.

    Returns:
        Dict[str, dict]: A dictionary containing the generated caption.

    Raises:
        HTTPException: If there's an error processing the image.
    """
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        caption = model.generate_caption(image, action_type=action_type)
        return JSONResponse(content={"caption": caption})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")


@router.get("/", response_model=Dict[str, str])
def initial_route() -> Dict[str, str]:
    """
    Initial route to welcome users.

    Returns:
        Dict[str, str]: A dictionary containing a welcome message.
    """
    return {"message": "Welcome to the Image Caption Generator API"}
