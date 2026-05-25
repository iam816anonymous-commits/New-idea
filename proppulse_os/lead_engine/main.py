from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Security, Request
from fastapi.security.api_key import APIKeyHeader
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
import time
from proppulse_os.core.database import get_db, engine
from proppulse_os.core.config import settings
from proppulse_os.core.logger import logger
from proppulse_os.lead_engine import models
from proppulse_os.core.routing import route_lead
from proppulse_os.core.audit import log_event
from proppulse_os.agents.whatsapp_bot import trigger_whatsapp_qualification

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

async def get_current_tenant(api_key: str = Security(api_key_header), db: Session = Depends(get_db)) -> models.Tenant:
    tenant = db.query(models.Tenant).filter(models.Tenant.api_key == api_key, models.Tenant.is_active == True).first()
    if not tenant:
        # For development/MVP allow the default key
        if api_key == settings.API_KEY:
            # Create a default tenant if not exists
            default_tenant = db.query(models.Tenant).filter(models.Tenant.brokerage_name == "Default Brokerage").first()
            if not default_tenant:
                default_tenant = models.Tenant(brokerage_name="Default Brokerage", api_key=settings.API_KEY)
                db.add(default_tenant)
                db.commit()
                db.refresh(default_tenant)
            return default_tenant
        raise HTTPException(status_code=403, detail="Unauthorized: Invalid API Key")
    return tenant

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    req_id = getattr(request.state, "id", "N/A")
    logger.error(f"Request {req_id} failed: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"message": "Internal Server Error", "request_id": req_id})

@app.get("/v1/health")
def health_check():
    return {"status": "healthy", "timestamp": time.time()}

class LeadCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    phone_number: str = Field(..., pattern=r"^\+?[1-9]\d{1,14}$")
    email: Optional[EmailStr] = None
    project_name: str
    source: Optional[str] = "Meta Ads"

class ProjectCreate(BaseModel):
    name: str
    micro_market: str
    base_price_sqft: float
    possession_year: int
    amenities: str

@app.post("/v1/projects")
def create_project(project: ProjectCreate, db: Session = Depends(get_db), tenant: models.Tenant = Depends(get_current_tenant)):
    db_project = models.Project(**project.model_dump(), brokerage_id=tenant.id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@app.get("/v1/projects")
def list_projects(db: Session = Depends(get_db), tenant: models.Tenant = Depends(get_current_tenant)):
    return db.query(models.Project).filter(models.Project.brokerage_id == tenant.id).all()

@app.post("/v1/leads")
async def capture_lead(
    lead: LeadCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    tenant: models.Tenant = Depends(get_current_tenant)
):
    project = db.query(models.Project).filter(
        models.Project.name == lead.project_name,
        models.Project.brokerage_id == tenant.id
    ).first()

    if not project:
        project = db.query(models.Project).filter(models.Project.brokerage_id == tenant.id).first()
        if not project:
             raise HTTPException(status_code=404, detail="No projects found for tenant")

    db_lead = models.Lead(
        name=lead.name,
        phone_number=lead.phone_number,
        email=lead.email,
        project_id=project.id,
        brokerage_id=tenant.id,
        source=lead.source,
        status="New"
    )
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)

    background_tasks.add_task(route_lead, db_lead.id)
    background_tasks.add_task(trigger_whatsapp_qualification, db_lead.id)
    background_tasks.add_task(log_event, tenant.id, "LEAD_CAPTURED", f"Lead {db_lead.id} created from {lead.source}")

    return {"message": "Lead captured successfully", "lead_id": db_lead.id, "tenant": tenant.brokerage_name}

@app.get("/v1/leads")
def list_leads(db: Session = Depends(get_db), tenant: models.Tenant = Depends(get_current_tenant)):
    return db.query(models.Lead).filter(models.Lead.brokerage_id == tenant.id).all()
