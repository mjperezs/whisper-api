from fastapi import FastAPI, File, UploadFile
import whisper
import shutil

app = FastAPI()
model = whisper.load_model("base")  # or "small", "medium"

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    with open("temp.webm", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = model.transcribe("temp.webm")
    return {"text": result["text"]}
