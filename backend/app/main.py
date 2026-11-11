from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(title=settings.APP_NAME)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.APP_NAME}

from app.api.v1.endpoints import auth, documents, investigations
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Authentication"])
app.include_router(documents.router, prefix=f"{settings.API_V1_PREFIX}/documents", tags=["Documents"])
app.include_router(investigations.router, prefix=f"{settings.API_V1_PREFIX}/investigations", tags=["Investigations"])