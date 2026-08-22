from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import engine, Base, get_db, init_db
from app import models

settings = get_settings()

# Initialize database
init_db()

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers after app creation to avoid circular imports
from app.routers import companies, clusters, news, reports, importer

app.include_router(importer.router, prefix="/api/import", tags=["import"])
app.include_router(companies.router, prefix="/api/companies", tags=["companies"])
app.include_router(clusters.router, prefix="/api/clusters", tags=["clusters"])
app.include_router(news.router, prefix="/api/news", tags=["news"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])


@app.get("/")
def read_root():
    return {
        "name": settings.app_name,
        "version": settings.version,
        "status": "running",
    }


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    return {"status": "healthy"}
