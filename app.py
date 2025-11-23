#!/usr/bin/env python3
"""
Voice AI Interface - FastAPI Backend
Orchestrates STT (Deepgram), Langflow Agent, and TTS (ElevenLabs)
"""

import os
import base64
from pathlib import Path
from typing import Optional
import httpx
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

# Configuration
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LANGFLOW_BASE_URL = os.getenv("LANGFLOW_BASE_URL", "http://localhost:7860")
LANGFLOW_FLOW_ID = os.getenv("LANGFLOW_FLOW_ID", "ec2db58a-812e-461c-ba83-8054092225bc")
LANGFLOW_API_KEY = os.getenv("LANGFLOW_API_KEY")

# Validate required keys
if not all([DEEPGRAM_API_KEY, ELEVENLABS_API_KEY, LANGFLOW_API_KEY]):
    raise ValueError("Missing required API keys in .env file")

app = FastAPI(title="Voice AI Interface")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories
Path("templates").mkdir(exist_ok=True)
Path("static").mkdir(exist_ok=True)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")


async def transcribe_audio_deepgram(audio_data: bytes) -> str:
    """Transcribe audio using Deepgram API"""
    url = "https://api.deepgram.com/v1/listen"
    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": "audio/webm"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, headers=headers, content=audio_data)
        response.raise_for_status()
        result = response.json()
        
        # Extract transcript
        transcript = result.get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0].get("transcript", "")
        return transcript


async def query_langflow(text: str, session_id: str = "default") -> str:
    """Send text to Langflow and get agent response"""
    # Use the /run endpoint (correct for Langflow v1.5+)
    url = f"{LANGFLOW_BASE_URL}/api/v1/run/{LANGFLOW_FLOW_ID}"
    
    payload = {
        "input_value": text,
        "output_type": "chat",
        "input_type": "chat"
    }
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": LANGFLOW_API_KEY
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        # Extract response text from Langflow response
        try:
            outputs = result.get("outputs", [])
            if outputs and len(outputs) > 0:
                first_output = outputs[0]
                output_list = first_output.get("outputs", [])
                if output_list and len(output_list) > 0:
                    results = output_list[0].get("results", {})
                    message = results.get("message", {})
                    
                    # Extract text from message object
                    if isinstance(message, dict):
                        text_response = message.get("text", "")
                        if text_response:
                            return text_response
                    elif isinstance(message, str):
                        return message
        except Exception as e:
            print(f"Error parsing Langflow response: {e}")
        
        return "No response from agent"


async def synthesize_speech_elevenlabs(text: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM") -> bytes:
    """Convert text to speech using ElevenLabs API"""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    
    payload = {
        "text": text,
        "model_id": "eleven_turbo_v2_5",  # Free tier compatible model
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.content


@app.get("/")
async def read_root():
    """Serve the main HTML page"""
    return FileResponse("templates/index.html")


@app.post("/process_audio")
async def process_audio(audio: UploadFile = File(...)):
    """
    Main orchestration endpoint:
    1. Transcribe audio (Deepgram)
    2. Get agent response (Langflow)
    3. Synthesize speech (ElevenLabs)
    """
    try:
        # Read audio data
        audio_data = await audio.read()
        
        # Step 1: Transcribe
        transcript = await transcribe_audio_deepgram(audio_data)
        if not transcript or transcript.strip() == "":
            return JSONResponse(
                status_code=400,
                content={"error": "Could not transcribe audio. Please speak clearly."}
            )
        
        # Step 2: Query Langflow
        agent_response = await query_langflow(transcript)
        
        # Step 3: Synthesize
        audio_response = await synthesize_speech_elevenlabs(agent_response)
        
        # Return both text and audio (base64)
        audio_base64 = base64.b64encode(audio_response).decode('utf-8')
        
        return JSONResponse(content={
            "transcript": transcript,
            "response_text": agent_response,
            "response_audio": audio_base64
        })
        
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=500, detail=f"API Error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "langflow_url": LANGFLOW_BASE_URL}


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
