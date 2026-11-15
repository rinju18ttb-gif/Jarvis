import os
import requests
from fastapi import FastAPI
from pydantic import BaseModel
from google import genai

app = FastAPI()

GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_KEY)
CHECKLIST_CSV_URL = os.environ.get("CHECKLIST_CSV_URL", "")

class Command(BaseModel):
    prompt: str

def get_my_checklist():
    if not CHECKLIST_CSV_URL:
        return "No checklist connected yet."
    try:
        return requests.get(CHECKLIST_CSV_URL, timeout=10).text
    except Exception:
        return "Could not fetch checklist."

@app.get("/")
def home():
    return {"status": "Jarvis Online"}

@app.get("/morning-briefing")
def get_briefing():
    checklist_data = get_my_checklist()
    prompt = (
        "You are Jarvis giving a daily morning briefing. Analyze the checklist and updates below, "
        "tell the user what to prioritize first, and keep it under 100 words so it sounds great spoken aloud.\n\n"
        f"{checklist_data}"
    )
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return {"briefing": response.text.strip()}

@app.post("/ask")
def ask_jarvis(cmd: Command):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"You are Jarvis. Answer concisely in 2 sentences: {cmd.prompt}"
    )
    return {"reply": response.text.strip()}
