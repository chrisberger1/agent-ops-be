from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controller import router as auth_router
from app.models import Base
from app.database import engine

# Create tables in the database
Base.metadata.create_all(bind=engine)

# Initialize FastAPI application
app = FastAPI(
    title="AI Opporturniy Holder App",
    description="API for user registration and authentication",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)

@app.get("/")
async def root():
    return {"message": "Opportunity Collector App is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)