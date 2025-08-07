from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv
import openai
import requests
import fitz  # PyMuPDF
from openai import OpenAI

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# Serve static files like index.html
app.mount("/static", StaticFiles(directory="static"), name="static")

# Route to show the HTML UI
@app.get("/")
def serve_ui():
    return FileResponse("static/index.html")

import requests

@app.post("/ask")
def ask_question(file_url: str = Form(...), question: str = Form(...)):
    # Dummy text for now – replace later with actual PDF text
    context = "This is an example document content that might have the answer."

    headers = {
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",  # same env variable name
        "HTTP-Referer": "http://localhost:8000",  # or your deployed domain
        "Content-Type": "application/json"
    }

    data = {
        "model": "openai/gpt-3.5-turbo",  # or any other model supported by OpenRouter
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"}
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)

    try:
        result = response.json()
        answer = result['choices'][0]['message']['content']
    except Exception as e:
        return {"error": str(e)}

    return JSONResponse(content={
        "question": question,
        "answer": answer
    })

