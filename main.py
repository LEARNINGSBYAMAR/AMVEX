"""
Amvex Technologies — backend API (FastAPI)
============================================================
Serves the same content the website's AMVEX_CONFIG object holds,
as JSON, plus a /api/contact endpoint for the contact form.

Run locally:
    pip install -r requirements.txt
    uvicorn main:app --reload

Then open:
    http://127.0.0.1:8000/docs      (interactive API docs)
    http://127.0.0.1:8000/api/config

To wire the website to this API once both are deployed on real
domains, replace the contact form's client-side handler in
index.html with a fetch() call to POST /api/contact (the file
already has a commented example at the bottom of the <script>).
A published Claude artifact link cannot call a custom domain, so
this only works once you deploy both the site and this API
yourselves — e.g. the site on Vercel/Netlify and this API on
Render/Fly.io/your own server.
============================================================
"""

from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from fastapi.responses import FileResponse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Amvex Technologies API",
    description="Content & contact API for the Amvex Technologies website.",
    version="1.0.0",
)

# ----------------------------------------------------------------
# CORS — add your real deployed website domain(s) here before you
# go live. "*" is fine for local development only.
# ----------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:5500",
        # "https://www.amvex.tech",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ==================================================================
# CONFIGURATION — edit these values to update what the API returns.
# This mirrors the AMVEX_CONFIG object in the website's index.html,
# so the two can be kept in sync, or you can later make the website
# fetch this data directly instead of using its built-in copy.
# ==================================================================

COMPANY = {
    "name": "Amvex Technologies Private Limited",
    "short_name": "Amvex",
    "founded_year": 2026,
    "tagline": "Software and game development, built end to end.",
    "email": "amarjith@amvex.in",
    "phone": "+91 94960 63951",
    "address": "Kozhikode, Kerala, India",
}

SERVICES = [
    {
        "title": "Software Development",
        "description": "Custom internal tools, automation and SaaS products, architected in Python and shipped with typed APIs from day one.",
        "tags": ["FastAPI", "PostgreSQL", "Docker"],
    },
    {
        "title": "Game Development",
        "description": "2D and 3D games and prototypes — gameplay systems, live-ops backends, and matchmaking services that scale with your player base.",
        "tags": ["Unity", "Godot", "WebSocket"],
    },
    {
        "title": "Web Development",
        "description": "Marketing sites and web apps that load fast and animate with intent, not decoration.",
        "tags": ["React", "FastAPI"],
    },
    {
        "title": "Cloud & DevOps",
        "description": "CI/CD, containerized deployments and observability so releases stop being an event.",
        "tags": ["Docker", "CI/CD"],
    },
    {
        "title": "APIs & Integrations",
        "description": "Third-party integrations and internal APIs, documented and versioned from the first commit.",
        "tags": ["FastAPI", "OpenAPI"],
    },
]

PROJECTS = [
    {"title": "Ledgerline", "kind": "Software", "description": "Internal finance automation tool replacing three spreadsheets and a lot of email."},
    {"title": "Driftbound", "kind": "Game", "description": "A low-poly co-op exploration game with a Python-backed matchmaking service."},
    {"title": "Northreach", "kind": "Website", "description": "A logistics company's public site and customer portal, rebuilt for speed."},
    {"title": "Signalboard", "kind": "Software", "description": "A real-time ops dashboard streaming metrics over WebSockets from a FastAPI core."},
    {"title": "Emberkeep", "kind": "Game", "description": "A mobile idle-strategy game with cloud save and a Python live-ops backend."},
    {"title": "Fieldkit", "kind": "Website", "description": "A booking and scheduling web app for a field-services client."},
]

STACK = ["Python", "FastAPI", "PostgreSQL", "Redis", "Docker", "Unity / Godot"]

PROCESS = [
    {"step": "Discover", "description": "We start with your users and constraints, not a feature list."},
    {"step": "Design", "description": "System design plus wireframes and motion studies, reviewed together."},
    {"step": "Build", "description": "Python services and interfaces built in weekly, demoable increments."},
    {"step": "Playtest & QA", "description": "Automated tests plus manual playtesting or user testing on every release."},
    {"step": "Launch & Support", "description": "Monitoring, on-call support and the next round of features after launch."},
]

# In-memory store for contact submissions (swap for a real database
# such as PostgreSQL before going to production).
CONTACT_MESSAGES: List[dict] = []


# ==================================================================
# MODELS
# ==================================================================

class Service(BaseModel):
    title: str
    description: str
    tags: List[str]


class Project(BaseModel):
    title: str
    kind: str
    description: str


class ProcessStep(BaseModel):
    step: str
    description: str


class CompanyInfo(BaseModel):
    name: str
    short_name: str
    founded_year: int
    tagline: str
    email: EmailStr
    phone: str
    address: str


class ContactMessageIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    email: EmailStr
    project_type: Optional[str] = Field(default="Something else", max_length=60)
    message: str = Field(..., min_length=1, max_length=4000)


class ContactMessageOut(BaseModel):
    status: str
    received_at: datetime


# ==================================================================
# ROUTES
# ==================================================================

@app.get("/api/health")
def health():
    return {"status": "ok", "time": datetime.utcnow()}


@app.get("/api/config", response_model=CompanyInfo)
def get_company_info():
    return CompanyInfo(
        name=COMPANY["name"],
        short_name=COMPANY["short_name"],
        founded_year=COMPANY["founded_year"],
        tagline=COMPANY["tagline"],
        email=COMPANY["email"],
        phone=COMPANY["phone"],
        address=COMPANY["address"],
    )


@app.get("/api/services", response_model=List[Service])
def get_services():
    return SERVICES


@app.get("/api/projects", response_model=List[Project])
def get_projects(kind: Optional[str] = None):
    """Optionally filter projects by kind, e.g. /api/projects?kind=Game"""
    if kind:
        filtered = [p for p in PROJECTS if p["kind"].lower() == kind.lower()]
        if not filtered:
            raise HTTPException(status_code=404, detail=f"No projects of kind '{kind}'")
        return filtered
    return PROJECTS


@app.get("/api/stack", response_model=List[str])
def get_stack():
    return STACK


@app.get("/api/process", response_model=List[ProcessStep])
def get_process():
    return PROCESS


@app.post("/api/contact", response_model=ContactMessageOut)
def submit_contact(payload: ContactMessageIn):
    record = payload.dict()
    record["received_at"] = datetime.utcnow()
    CONTACT_MESSAGES.append(record)
    # TODO: send an email / Slack notification / save to a real database here.
    return ContactMessageOut(status="received", received_at=record["received_at"])

"""
@app.get("/")
def root():
    return {
        "message": "Amvex Technologies API is running.",
        "docs": "/docs",
        "endpoints": [
            "/api/config", "/api/services", "/api/projects",
            "/api/stack", "/api/process", "/api/contact (POST)",
        ],
    }
"""
@app.get("/")
def home():
    return FileResponse(BASE_DIR / "index.html")
