from fastapi import FastAPI
from dotenv import load_dotenv
from routes import ai_router
from fastapi.middleware.cors import CORSMiddleware
load_dotenv()

app = FastAPI(
    title="Beckn DEG Bot",
    description="AI Agent for Beckn Digital Enablement Gateway",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include AI routes
app.include_router(ai_router)

@app.get("/ping")
def read_root():
    return {"message": "PONG!! Hello, World!"}