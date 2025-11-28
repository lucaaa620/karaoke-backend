from fastapi import FastAPI, UploadFile, File
import subprocess
import uuid
import os
import json

app = FastAPI()

UPLOAD_DIR = "uploads"
RESULTS_DIR = "results"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

@app.post("/transcribe/")
async def transcribe(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    input_path = f"{UPLOAD_DIR}/{file_id}.wav"
    output_path = f"{RESULTS_DIR}/{file_id}.json"

    with open(input_path, "wb") as f:
        f.write(await file.read())

    # Run whisper.cpp model
    subprocess.run([
        "./main",
        "-m", "models/ggml-base.bin",
        "-f", input_path,
        "-otxt",
        "-of", f"{RESULTS_DIR}/{file_id}"
    ])

    # Read generated transcript
    txt_path = f"{RESULTS_DIR}/{file_id}.txt"
    if not os.path.exists(txt_path):
        return {"error": "Transcription failed"}

    with open(txt_path, "r") as f:
        text = f.read()

    return {"text": text, "id": file_id}
