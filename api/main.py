from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Security, Request, Header
from fastapi.security.api_key import APIKeyHeader
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
import time
from core.database import get_db, engine
from core.config import settings
from core.logger import logger
from api import models
from core.routing import route_lead
from automation.whatsapp_bot import trigger_whatsapp_qualification

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

# Production Middleware: Request Tracking
@app.middleware("http")
async def add_request_id_and_timer(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.id = request_id
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(process_time)
    return response

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

async def get_tenant_id(x_brokerage_id: str = Header(default="default")):
    """Dependency to extract brokerage_id for multi-tenancy."""
    return x_brokerage_id

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    req_id = getattr(request.state, "id", "N/A")
    logger.error(f"Request {req_id} failed: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error", "request_id": req_id},
    )

@app.get("/v1/health")
def health_check():
    return {"status": "healthy", "timestamp": time.time()}

class LeadCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    phone_number: str = Field(..., pattern=r"^\+?[1-9]\d{1,14}$") # E.164 format
    email: Optional[EmailStr] = None
    project_name: str
    source: Optional[str] = "Meta Ads"

class ProjectCreate(BaseModel):
    name: str
    micro_market: str
    base_price_sqft: float
    possession_year: int
    amenities: str

@app.post("/v1/projects", dependencies=[Depends(get_api_key)])
def create_project(project: ProjectCreate, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    db_project = models.Project(**project.model_dump(), brokerage_id=tenant_id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@app.get("/v1/projects")
def list_projects(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return db.query(models.Project).filter(models.Project.brokerage_id == tenant_id).all()

@app.post("/v1/leads")
async def capture_lead(
    lead: LeadCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
    tenant_id: str = Depends(get_tenant_id)
):
    # Match lead with project within tenant scope
    project = db.query(models.Project).filter(
        models.Project.name == lead.project_name,
        models.Project.brokerage_id == tenant_id
    ).first()

    if not project:
        project = db.query(models.Project).filter(models.Project.brokerage_id == tenant_id).first()
        if not project:
             raise HTTPException(status_code=404, detail="Project not found for this tenant")

    db_lead = models.Lead(
        name=lead.name,
        phone_number=lead.phone_number,
        email=lead.email,
        project_id=project.id,
        brokerage_id=tenant_id,
        source=lead.source,
        status="New"
    )
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)

    background_tasks.add_task(route_lead, db_lead.id)
    background_tasks.add_task(trigger_whatsapp_qualification, db_lead.id)

    return {"message": "Lead captured successfully", "lead_id": db_lead.id}

@app.get("/v1/leads")
def list_leads(db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)):
    return db.query(models.Lead).filter(models.Lead.brokerage_id == tenant_id).all()
