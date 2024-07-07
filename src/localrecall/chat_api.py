from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
from typing import List, Optional
from .chat import GoogleGeminiChat, LocalModelChat

app = FastAPI()

class ChatRequest(BaseModel):
    question: str
    strategy: str = "google_gemini"
    history: List[dict] = []
    filters: Optional[dict] = None

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        if not request.strategy:
            raise HTTPException(status_code=400, detail="Strategy is required")

        if request.strategy == "google_gemini":
            chat_strategy = GoogleGeminiChat()
            
        elif request.strategy == "local":
            chat_strategy = LocalModelChat()
            
        else:
            raise HTTPException(status_code=400, detail="Invalid strategy")

        chat_generator = chat_strategy.process_question(
            question=request.question,
            history=request.history,
            filters=request.filters
        )

        async def response_generator():
            async for chunk in chat_generator:
                if isinstance(chunk, list): 
                    yield f"data: list_{chunk}\n\n"
                elif isinstance(chunk, str):
                    yield f"data: {chunk}\n\n"
                await asyncio.sleep(0) 

        return StreamingResponse(response_generator(), media_type="text/event-stream")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=11011)