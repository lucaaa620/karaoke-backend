from fastapi import FastAPI, UploadFile, File
import subprocess
import os
import uuid

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Backend is live and working!"}


# ------------------------------
# Audio Transcription Endpoint
# ------------------------------
@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    # Step 1: Save uploaded audio temporarily
    file_id = str(uuid.uuid4())
    input_path = f"/app/{file_id}.wav"

    with open(input_path, "wb") as f:
        f.write(await file.read())

    # Step 2: Whisper binary path (from whisper_bin folder in Dockerfile)
    whisper_path = "/whisper/whisper_bin/whisper"

    # Step 3: Output file
    output_path = f"/app/{file_id}.txt"

    # Step 4: Run Whisper command
    command = [
        whisper_path,
        input_path,
        "--language", "auto",
        "--model", "base",
        "--output_format", "txt",
        "--output_file", output_path
    ]

    try:
        subprocess.run(command, check=True)
    except Exception as e:
        return {"error": f"Whisper failed: {e}"}

    # Step 5: Read output
    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        text = "Transcription failed."

    # Clean up temporary files
    os.remove(input_path)
    if os.path.exists(output_path):
        os.remove(output_path)

    return {"transcription": text}
