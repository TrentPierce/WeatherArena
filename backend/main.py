from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import data, verification, tiles

app = FastAPI(title="WeatherArena API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(data.router)
app.include_router(verification.router)
app.include_router(tiles.router)

@app.get("/")
async def root():
    return {"message": "WeatherArena Backend Operational"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
