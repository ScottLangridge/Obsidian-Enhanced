#!/usr/bin/env python3

import logging
from fastapi import FastAPI, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from vault_handler import VaultHandler
from quick_capture import QuickCapture
from logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI()

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")


class CaptureRequest(BaseModel):
    text: str


# Initialize components
vault_handler = VaultHandler("/vault")
quick_capture = QuickCapture(vault_handler)

logger.info("================================")
logger.info("         Server Started         ")
logger.info("================================")

@app.get("/")
def root():
    """Serve the main web interface"""
    return FileResponse("static/index.html")


@app.post("/api/capture")
def capture_text(request: CaptureRequest, background_tasks: BackgroundTasks):
    """Receive captured text and process in background"""
    logger.info(f"Received: {request.text}")
    background_tasks.add_task(quick_capture.process, request.text)
    return {"status": "success", "message": "Text captured successfully"}
