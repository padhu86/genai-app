from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
import requests

app = FastAPI()

# Template setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# APIM details
APIM_ENDPOINT = "https://apim-dev-southindia-01.azure-api.net/dev/openai/deployments/gpt-4o-mini/chat/completions?api-version=2024-02-15-preview"
APIM_KEY = os.getenv("APIM_SUBSCRIPTION_KEY")

# 🚨 Safety check (fail fast if key missing)
if not APIM_KEY:
    raise ValueError("APIM_SUBSCRIPTION_KEY is not set in environment variables")

# Home page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {})

# Chat endpoint
@app.post("/chat")
async def chat(req: Request):
    body = await req.json()
    user_query = body["message"]

    response = requests.post(
        APIM_ENDPOINT,
        headers={
            "Content-Type": "application/json",
            "Ocp-Apim-Subscription-Key": APIM_KEY
        },
        json={
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_query}
            ]
        }
    )

    data = response.json()

    # 🔍 Debug handling
    if "choices" not in data:
        return {
            "error": "APIM response issue",
            "full_response": data
        }

    return {
        "response": data["choices"][0]["message"]["content"]
    }

# Test APIM endpoint
@app.get("/test-apim")
async def test_apim():
    try:
        response = requests.post(
            APIM_ENDPOINT,
            headers={
                "Content-Type": "application/json",
                "Ocp-Apim-Subscription-Key": APIM_KEY
            },
            json={
                "messages": [
                    {"role": "user", "content": "Say hello"}
                ]
            }
        )

        return response.json()

    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "trace": traceback.format_exc()
        }
