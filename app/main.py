#!/usr/bin/env python3

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI()

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")


class CaptureRequest(BaseModel):
    text: str


@app.get("/")
async def root():
    """Serve the main web interface"""
    return FileResponse("static/index.html")


@app.post("/api/capture")
async def capture_text(request: CaptureRequest):
    """Receive captured text and log it to console"""
    print(f"[CAPTURE] {request.text}")
    return {"status": "success", "message": "Text captured successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
