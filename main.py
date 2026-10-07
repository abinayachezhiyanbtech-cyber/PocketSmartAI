import base64
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from gemini_utils import generate_recommendations

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="PocketSmart AI")

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static"
)

templates = Jinja2Templates(
    directory=BASE_DIR / "templates"
)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


@app.post("/generate-home")
async def generate_home(request: Request):
    data = await request.json()

    budget = float(data.get("budget", 0))

    if budget <= 0:
        return {"error": "Please enter a valid budget."}

    result = await generate_recommendations(
        category="home",
        data=data
    )

    return {
        "category": "Home Interior",
        "result": result
    }


@app.post("/generate-party")
async def generate_party(request: Request):
    data = await request.json()

    budget = float(data.get("budget", 0))

    if budget <= 0:
        return {"error": "Please enter a valid budget."}

    result = await generate_recommendations(
        category="party",
        data=data
    )

    return {
        "category": "Party Planner",
        "result": result
    }


@app.post("/generate-jewelry")
async def generate_jewelry(
    budget: float = Form(...),
    preferences: str = Form(...),
    extra: str = Form(""),
    outfit_image: UploadFile | None = File(default=None)
):
    if budget <= 0:
        return {"error": "Please enter a valid budget."}

    image_data = None
    mime_type = None

    if outfit_image and outfit_image.filename:
        allowed_types = {
            "image/jpeg",
            "image/png",
            "image/webp"
        }

        if outfit_image.content_type not in allowed_types:
            return {
                "error": "Upload a JPG, PNG, or WEBP image."
            }

        content = await outfit_image.read()

        if len(content) > 5 * 1024 * 1024:
            return {
                "error": "Image must be smaller than 5 MB."
            }

        image_data = base64.b64encode(
            content
        ).decode("utf-8")

        mime_type = outfit_image.content_type

    data = {
        "budget": budget,
        "preferences": preferences,
        "extra": extra
    }

    result = await generate_recommendations(
        category="jewelry",
        data=data,
        image_data=image_data,
        mime_type=mime_type
    )

    return {
        "category": "Jewelry Planner",
        "result": result
    }


@app.get("/health")
async def health():
    return {
        "status": "running",
        "project": "PocketSmart AI"
    }