import os, subprocess
from fastapi import FastAPI, File, UploadFile, Header, HTTPException
from vosk import Model, KaldiRecognizer
import wave, json

MODEL_PATH = "model"
MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"


# Download model if not exists
if not os.path.exists(MODEL_PATH):
    subprocess.run(["curl", "-L", MODEL_URL, "-o", "model.zip"], check=True)
    subprocess.run(["unzip", "model.zip", "-d", "."], check=True)
    os.rename("vosk-model-small-en-us-0.15", MODEL_PATH)
#definition
app = FastAPI()
model = Model(MODEL_PATH)

API_KEY = os.getenv("API_KEY")

@app.post("/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    x_api_key: str = Header(None)
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    input_path = "temp_input.webm"
    wav_path = "temp.wav"

    with open(input_path, "wb") as buffer:
        buffer.write(await file.read())

    subprocess.run([
        "ffmpeg", "-i", input_path, "-ar", "16000", "-ac", "1", wav_path, "-y"
    ], check=True)

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
    text = " ".join([r.get("text", "") for r in results])

    return {"text": text.strip()}
