from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import engine, Base, get_db
from app import models
from app.routers import customers, data_quality, services, opportunities

settings = get_settings()

Base.metadata.create_all(bind=engine)

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

app.include_router(customers.router, prefix="/api/customers", tags=["customers"])
app.include_router(data_quality.router, prefix="/api/data-quality", tags=["data_quality"])
app.include_router(services.router, prefix="/api/services", tags=["services"])
app.include_router(opportunities.router, prefix="/api/opportunities", tags=["opportunities"])


@app.get("/")
def read_root():
    return {
        "name": settings.app_name,
        "version": settings.version,
        "status": "running"
    }


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    return {"status": "healthy"}
