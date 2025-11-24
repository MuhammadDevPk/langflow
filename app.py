#!/usr/bin/env python3
"""
Voice AI Interface - FastAPI Backend
Orchestrates STT (Deepgram), Langflow Agent, and TTS (ElevenLabs)
"""

import os
import json
import base64
import io
from pathlib import Path
from typing import Optional
import httpx
from gtts import gTTS
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
LANGFLOW_FLOW_ID = os.getenv("LANGFLOW_FLOW_ID", "e4306c3a-8459-49c8-9339-baed51dc8fa4")
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


def synthesize_speech_google(text: str) -> bytes:
    """Convert text to speech using Google TTS (free, no API key needed)"""
    # Create gTTS object with US English
    tts = gTTS(text=text, lang='en', tld='us', slow=False)
    
    # Save to bytes buffer
    audio_buffer = io.BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    
    return audio_buffer.read()


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


@app.get("/get_greeting")
async def get_greeting():
    """
    Get the agent's greeting message from VAPI JSON and synthesize it
    """
    try:
        # Read VAPI JSON file
        vapi_json_path = Path("json/inputs/daniel_dental_agent.json")
        if not vapi_json_path.exists():
            raise HTTPException(status_code=404, detail="VAPI JSON file not found")
        
        with open(vapi_json_path, 'r') as f:
            vapi_data = json.load(f)
        
        # Extract first message from start node
        greeting_text = None
        nodes = vapi_data.get('workflow', {}).get('nodes', [])
        
        for node in nodes:
            if node.get('isStart') or node.get('name') == 'start':
                message_plan = node.get('messagePlan', {})
                greeting_text = message_plan.get('firstMessage', '')
                break
        
        if not greeting_text:
            greeting_text = "Thank you for calling Wellness Partners. This is Riley, your scheduling assistant. How may I help you today?"
        
        # Try to synthesize greeting - first with ElevenLabs, then fallback to Google
        try:
            audio_response = await synthesize_speech_elevenlabs(greeting_text)
            audio_base64 = base64.b64encode(audio_response).decode('utf-8')
            tts_engine = "ElevenLabs"
        except httpx.HTTPStatusError as tts_error:
            # If ElevenLabs fails, use Google TTS as fallback
            print(f"ElevenLabs failed ({tts_error.response.status_code}), using Google TTS fallback...")
            try:
                audio_response = synthesize_speech_google(greeting_text)
                audio_base64 = base64.b64encode(audio_response).decode('utf-8')
                tts_engine = "Google TTS (Fallback)"
            except Exception as google_error:
                print(f"Google TTS also failed: {google_error}")
                return JSONResponse(content={
                    "greeting_text": greeting_text,
                    "greeting_audio": None,
                    "tts_error": "All TTS engines failed"
                })
        
        return JSONResponse(content={
            "greeting_text": greeting_text,
            "greeting_audio": audio_base64,
            "tts_engine": tts_engine
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting greeting: {str(e)}")


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
