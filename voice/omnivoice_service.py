#!/usr/bin/env python3
"""
OmniVoice Local TTS Service for J.A.R.V.I.S.
Exposes a lightweight, high-performance HTTP API on port 8008.
Supports Zero-Shot Voice Cloning and Voice Design via k2-fsa/OmniVoice on Apple Silicon (MPS).
"""

import io
import os
import sys
import time
import logging
import soundfile as sf
import torch
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("omnivoice_service")

app = FastAPI(title="OmniVoice TTS Service for JARVIS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

VALID_EN_INSTRUCTS = {
    "american accent", "australian accent", "british accent", "canadian accent",
    "child", "chinese accent", "elderly", "female", "high pitch", "indian accent",
    "japanese accent", "korean accent", "low pitch", "male", "middle-aged",
    "moderate pitch", "portuguese accent", "russian accent", "teenager",
    "very high pitch", "very low pitch", "whisper", "young adult"
}
DEFAULT_INSTRUCT = "male, british accent, low pitch"

def sanitize_instruct(raw: Optional[str]) -> str:
    if not raw:
        return DEFAULT_INSTRUCT
    tokens = [t.strip().lower() for t in raw.split(",") if t.strip()]
    matched = [t for t in tokens if t in VALID_EN_INSTRUCTS]
    if matched:
        return ", ".join(matched)
    # If the user passed free-form text like "British butler", match known keywords
    inferred = []
    raw_lower = raw.lower()
    if "british" in raw_lower or "uk" in raw_lower:
        inferred.append("british accent")
    elif "american" in raw_lower or "us" in raw_lower:
        inferred.append("american accent")
    if "female" in raw_lower or "woman" in raw_lower:
        inferred.append("female")
    else:
        inferred.append("male")
    if "low" in raw_lower or "deep" in raw_lower or "baritone" in raw_lower:
        inferred.append("low pitch")
    elif "high" in raw_lower:
        inferred.append("high pitch")
    if "middle" in raw_lower or "mature" in raw_lower:
        inferred.append("middle-aged")
    elif "young" in raw_lower:
        inferred.append("young adult")
    elif "old" in raw_lower or "elderly" in raw_lower:
        inferred.append("elderly")
    if "whisper" in raw_lower:
        inferred.append("whisper")
        
    return ", ".join(inferred) if inferred else DEFAULT_INSTRUCT

class SynthesizeRequest(BaseModel):
    text: str
    instruct: Optional[str] = DEFAULT_INSTRUCT
    ref_audio: Optional[str] = None
    ref_text: Optional[str] = None
    language: Optional[str] = "en"
    num_step: Optional[int] = 2
    speed: Optional[float] = 1.0

model = None
is_ready = False
AUDIO_CACHE = {}

def get_cache_key(text: str, instruct: str, num_step: int) -> str:
    norm_text = "".join(c.lower() for c in text.strip() if c.isalnum() or c.isspace())
    return f"{norm_text}|{instruct}|{num_step}"

def get_device():
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"

def prewarm_cache():
    common_phrases = [
        "Online and ready, sir.",
        "Hello sir, how may I assist you today?",
        "Hello, sir. How may I assist you today?",
        "Hello, sir. At your service.",
        "All systems nominal, sir. How may I be of service?",
        "Yes, sir. I am always prepared for your inquiries.",
        "At your service, sir.",
        "Right away, sir.",
        "Working on it, sir.",
        "My name is JARVIS, sir. At your service.",
        "I am Jarvis, sir. At your service.",
        "I am Jarvis.",
        "I'm as functional as ever, sir. How can I serve you better today?",
        "Very good, sir.",
        "Certainly, sir.",
        "I can hear you clearly, sir.",
        "I am functioning normally, sir.",
        "Systems are fully operational, sir.",
        "I have inspected the application, sir.",
        "Reverse engineering analysis complete, sir.",
        "Decompilation finished, sir.",
        "I've inspected your browser tabs via Agent Reach, sir.",
        "Developer agent engaged, sir.",
        "OpenClaw autonomous agent task initiated, sir.",
        "Launching the application now, sir.",
        "Task completed successfully, sir.",
    ]
    for phrase in common_phrases:
        for steps in (2, 4):
            try:
                k = get_cache_key(phrase, DEFAULT_INSTRUCT, steps)
                if k not in AUDIO_CACHE and model is not None:
                    audios = model.generate(text=phrase, language="en", num_step=steps, instruct=DEFAULT_INSTRUCT)
                    buf = io.BytesIO()
                    sf.write(buf, audios[0], 24000, format="WAV")
                    AUDIO_CACHE[k] = buf.getvalue()
                    logger.info(f"Prewarmed cache for ({steps} steps): '{phrase}' ({len(AUDIO_CACHE[k])} bytes)")
            except Exception as e:
                logger.warning(f"Prewarm skipped for '{phrase}': {e}")

def load_model():
    global model, is_ready
    from omnivoice.models.omnivoice import OmniVoice
    logger.info("Loading OmniVoice model from 'k2-fsa/OmniVoice' (CPU float16 -> MPS)...")
    t0 = time.time()
    try:
        model = OmniVoice.from_pretrained(
            "k2-fsa/OmniVoice",
            device_map="cpu",
            dtype=torch.float16,
        )
        if torch.backends.mps.is_available():
            try:
                model = model.to("mps")
                logger.info("OmniVoice successfully moved to MPS!")
            except Exception as e:
                logger.warning(f"Could not move to MPS ({e}), staying on CPU")
        is_ready = True
        logger.info(f"OmniVoice loaded successfully in {time.time() - t0:.2f}s!")
        import threading
        threading.Thread(target=prewarm_cache, daemon=True).start()
    except Exception as e:
        logger.error(f"Failed to load OmniVoice model: {e}", exc_info=True)

@app.on_event("startup")
def startup_event():
    import threading
    threading.Thread(target=load_model, daemon=True).start()

@app.get("/health")
def health():
    return {
        "status": "ok",
        "ready": is_ready,
        "device": get_device(),
        "model": "k2-fsa/OmniVoice",
        "cache_size": len(AUDIO_CACHE),
    }

@app.post("/synthesize")
def synthesize(req: SynthesizeRequest):
    if not is_ready or model is None:
        raise HTTPException(status_code=503, detail="OmniVoice model is still loading, please wait.")
    
    clean_text = req.text.strip()
    if not clean_text:
        raise HTTPException(status_code=400, detail="Empty text provided.")
        
    num_step = req.num_step if (req.num_step and req.num_step > 0) else 2
    kwargs = {
        "text": clean_text,
        "language": req.language or "en",
        "num_step": num_step,
    }
    if req.speed and req.speed != 1.0:
        kwargs["speed"] = req.speed
    
    if req.ref_audio and os.path.exists(req.ref_audio):
        kwargs["ref_audio"] = req.ref_audio
        kwargs["ref_text"] = req.ref_text or "At your service, sir. All systems are operational."
    elif req.instruct:
        kwargs["instruct"] = sanitize_instruct(req.instruct)
    else:
        kwargs["instruct"] = DEFAULT_INSTRUCT

    cache_key = get_cache_key(clean_text, kwargs.get("instruct", ""), num_step)
    if cache_key in AUDIO_CACHE:
        logger.info(f"INSTANT CACHE HIT ({len(clean_text)} chars): '{clean_text[:50]}' -> 0.001s")
        return Response(content=AUDIO_CACHE[cache_key], media_type="audio/wav")

    logger.info(f"Synthesizing ({len(clean_text)} chars, {num_step} steps): '{clean_text[:60]}'...")
    t0 = time.time()

    try:
        audios = model.generate(**kwargs)
        if not audios or len(audios) == 0:
            raise HTTPException(status_code=500, detail="No audio generated.")
            
        audio_arr = audios[0]
        buf = io.BytesIO()
        sf.write(buf, audio_arr, 24000, format="WAV")
        wav_bytes = buf.getvalue()
        
        # Store in cache
        AUDIO_CACHE[cache_key] = wav_bytes
        if len(AUDIO_CACHE) > 300:
            AUDIO_CACHE.pop(next(iter(AUDIO_CACHE)))

        logger.info(f"Generated {len(wav_bytes)} bytes WAV in {time.time() - t0:.2f}s")
        return Response(content=wav_bytes, media_type="audio/wav")
    except Exception as e:
        logger.error(f"Generation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("OMNIVOICE_PORT", 8008))
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")
