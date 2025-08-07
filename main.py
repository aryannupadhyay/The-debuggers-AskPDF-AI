import os
import fitz
import requests
from fastapi import FastAPI, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def index():
    return FileResponse("static/index.html")

def get_text_from_pdf(url):
    if "drive.google.com" in url:
        if "/file/d/" in url:
            file_id = url.split("/file/d/")[1].split("/")[0]
            url = f"https://drive.google.com/uc?export=download&id={file_id}"
    resp = requests.get(url)
    if resp.status_code != 200:
        raise RuntimeError("Could not download PDF")
    with open("temp.pdf", "wb") as f:
        f.write(resp.content)
    text = ""
    with fitz.open("temp.pdf") as doc:
        for page in doc:
            text += page.get_text()
    os.remove("temp.pdf")
    return text

@app.post("/ask")
async def ask(file_url: str = Form(...), question: str = Form(...)):
    try:
        text = get_text_from_pdf(file_url)
        if not text:
            return JSONResponse(content={"error": "Empty PDF content"}, status_code=400)

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "tngtech/deepseek-r1t2-chimera:free",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Context:\n{text[:3000]}\n\nQuestion: {question}"}
            ],
            "temperature": 0.5
        }

        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        if res.status_code == 200:
            answer = res.json()["choices"][0]["message"]["content"]
            return {"answer": answer}
        else:
            return JSONResponse(content={"error": f"Model error: {res.text}"}, status_code=res.status_code)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
