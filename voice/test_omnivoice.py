import os
import sys
import time
import torch
import soundfile as sf
from omnivoice.models.omnivoice import OmniVoice

print("[omnivoice] Initializing OmniVoice on MPS...", flush=True)
t0 = time.time()
model = OmniVoice.from_pretrained(
    "k2-fsa/OmniVoice",
    device_map="mps",
    dtype=torch.float16
)
print(f"[omnivoice] Model loaded in {time.time() - t0:.2f}s", flush=True)

test_text = "At your service, sir. All systems are operational."
instruct = "male, british accent, low pitch"

print(f"[omnivoice] Generating: '{test_text}' with instruct='{instruct}'...", flush=True)
t1 = time.time()
audios = model.generate(
    text=test_text,
    instruct=instruct,
    num_step=16, # fast inference for low latency
)
out_path = "voice/test_jarvis.wav"
sf.write(out_path, audios[0], 24000)
print(f"[omnivoice] Successfully generated {out_path} in {time.time() - t1:.2f}s!", flush=True)
