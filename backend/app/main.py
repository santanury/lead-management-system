from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import leads, auth
from app.api import settings as settings_router
from app.config import settings
# Removed: from dotenv import load_dotenv

# Removed: load_dotenv()

app = FastAPI(
    title="AI Lead Management System",
    description="A hackathon project to analyze, score, and route sales leads using AI.",
    version="1.0.0"
)

# CORS Configuration
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API router
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(leads.router, prefix="/api/v1", tags=["leads"])
app.include_router(settings_router.router, prefix="/api/v1", tags=["settings"])

@app.get("/", tags=["Root"])
async def read_root():
    """
    Root endpoint for health checks.
    """
    return {"message": "Welcome to the AI Lead Management System API!"}

# A check to ensure the Google API key is loaded.
@app.on_event("startup")
async def startup_event():
    # Initialize the database
    from app.db.init_db import init_db
    init_db()

    # pydantic-settings will raise ValidationError if GOOGLE_API_KEY is missing,
    # so this check is primarily for visual feedback.
    if not settings.google_api_key or "YOUR_GEMINI_API_KEY" in settings.google_api_key:
        print("="*80)
        print("WARNING: Google API key is not configured.")
        print("Please ensure GOOGLE_API_KEY is set in your .env file.")
        print("="*80)
