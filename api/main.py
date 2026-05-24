from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Security
from fastapi.security.api_key import APIKeyHeader
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from core.database import get_db, engine
from core.config import settings
from core.logger import logger
from api import models
from core.routing import route_lead
from automation.whatsapp_bot import trigger_whatsapp_qualification

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error"},
    )

class LeadCreate(BaseModel):
    name: str
    phone_number: str
    email: Optional[str] = None
    project_name: str
    source: Optional[str] = "Meta Ads"

class ProjectCreate(BaseModel):
    name: str
    micro_market: str
    base_price_sqft: float
    possession_year: int
    amenities: str

@app.post("/v1/projects", dependencies=[Depends(get_api_key)])
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    db_project = models.Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@app.get("/v1/projects")
def list_projects(db: Session = Depends(get_db)):
    return db.query(models.Project).all()

@app.post("/v1/leads")
async def capture_lead(lead: LeadCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    logger.info(f"Capturing lead: {lead.name} from {lead.source}")

    # Match lead with project
    project = db.query(models.Project).filter(models.Project.name == lead.project_name).first()
    if not project:
        project = db.query(models.Project).first()
        if not project:
             raise HTTPException(status_code=404, detail="No projects found")

    db_lead = models.Lead(
        name=lead.name,
        phone_number=lead.phone_number,
        email=lead.email,
        project_id=project.id,
        source=lead.source,
        status="New"
    )
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)

    # Routing and Automation
    background_tasks.add_task(route_lead, db_lead.id)
    background_tasks.add_task(trigger_whatsapp_qualification, db_lead.id)

    return {"message": "Lead captured successfully", "lead_id": db_lead.id}

@app.get("/v1/leads")
def list_leads(db: Session = Depends(get_db)):
    return db.query(models.Lead).all()
