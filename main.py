from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.authenticate import router as authenticate_router
from routes.organization import router as organization_router
from routes.rfp import router as rfp_router
from routes.supplier import router as supplier_router
from routes.google import router as google
from dotenv import load_dotenv
import os
import uvicorn


load_dotenv()

BASE_URL = os.getenv("BASE_URL")
if not BASE_URL:
    raise ValueError("BASE_URL is not set in the environment variables.")
import logging

app = FastAPI()
if __name__ == "__main__":
    # Use the PORT environment variable, default to 8000 for local development
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
    
origins = [BASE_URL]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows specific origins
    allow_credentials=True,  # Allows cookies to be included
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

logging.basicConfig(level=logging.DEBUG)

@app.get("/")
async def read_root():
    return {"API Working"}

app.include_router(authenticate_router, prefix="/api", tags=["authenticate"])
app.include_router(organization_router, prefix="/api", tags=["organization"])
app.include_router(rfp_router, prefix="/api", tags=["rfp"])
app.include_router(supplier_router, prefix="/api", tags=["supplier"])

app.include_router(google, prefix="/api", tags=["google"])

