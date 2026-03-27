from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential
import os

app = FastAPI()

# Template setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Managed Identity setup
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

credential = DefaultAzureCredential()

token_provider = get_bearer_token_provider(
    credential,
    "https://cognitiveservices.azure.com/.default"
)

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version="2024-02-15-preview",
    azure_ad_token_provider=token_provider
)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {})

@app.post("/chat")
async def chat(req: Request):
    body = await req.json()
    user_query = body["message"]

    return {"response": f"You said: {user_query}"}

@app.get("/test-openai")
async def test_openai():
    try:
        print("Endpoint:", os.getenv("AZURE_OPENAI_ENDPOINT"))
        print("Deployment:", os.getenv("AZURE_OPENAI_DEPLOYMENT"))

        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages=[
                {"role": "user", "content": "Say hello"}
            ]
        )

        return {"response": response.choices[0].message.content}

    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "trace": traceback.format_exc()
        }
