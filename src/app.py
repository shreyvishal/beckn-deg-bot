from fastapi import FastAPI
from dotenv import load_dotenv
from routes.index import router as main_router
from fastapi.middleware.cors import CORSMiddleware
from config.database import db_manager

load_dotenv()

app = FastAPI(
    title="Beckn DEG Bot",
    description="AI Agent for Beckn Digital Enablement Gateway with Authentication",
    version="1.0.0"
)

# Initialize database connection on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database connection on app startup"""
    db_manager.connect()
    print("Application started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on app shutdown"""
    db_manager.close_connection()
    print("Application shutdown completed")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include AI routes
app.include_router(prefix="/api", router = main_router)

@app.get("/ping")
def read_root():
    return {"message": "PONG!! Hello, World!"}