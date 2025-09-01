from fastapi import FastAPI, File, UploadFile, Header, HTTPException
import whisper, shutil, os

app = FastAPI()
model = whisper.load_model("base")

API_KEY = os.getenv("API_KEY")

@app.post("/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    x_api_key: str = Header(None)  # client must send header
):
    # check API key
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    with open("temp.webm", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = model.transcribe("temp.webm")
    return {"text": result["text"]}
