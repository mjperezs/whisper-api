from fastapi import FastAPI, File, UploadFile, Header, HTTPException
import os, subprocess, wave, json
from vosk import Model, KaldiRecognizer

app = FastAPI()

# Load Vosk model (lightweight, fits in free tier)
# Vosk provides small models you can download (e.g. vosk-model-small-en-us-0.15)
if not os.path.exists("model"):
    raise RuntimeError("Vosk model not found. Please download and unzip a Vosk model into ./model")

model = Model("model")

API_KEY = os.getenv("API_KEY")

@app.post("/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    x_api_key: str = Header(None)
):
    # check API key
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    # Save uploaded file temporarily
    input_path = "temp_input.webm"
    wav_path = "temp.wav"
    with open(input_path, "wb") as buffer:
        buffer.write(await file.read())

    # Convert to WAV using ffmpeg (Render has ffmpeg preinstalled)
    subprocess.run([
        "ffmpeg", "-i", input_path, "-ar", "16000", "-ac", "1", wav_path, "-y"
    ], check=True)

    # Open wav file
    wf = wave.open(wav_path, "rb")
    rec = KaldiRecognizer(model, wf.getframerate())

    results = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            results.append(json.loads(rec.Result()))

    results.append(json.loads(rec.FinalResult()))

    # Extract text
    text = " ".join([res.get("text", "") for res in results])

    return {"text": text.strip()}
