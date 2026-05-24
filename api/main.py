from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from core.database import get_db, engine
from api import models
from automation.whatsapp_bot import trigger_whatsapp_qualification

app = FastAPI(title="PropPulse AI Lead Engine")

class LeadCreate(BaseModel):
    name: str
    phone_number: str
    email: Optional[str] = None
    project_name: str

class ProjectCreate(BaseModel):
    name: str
    micro_market: str
    base_price_sqft: float
    possession_year: int
    amenities: str

@app.post("/v1/projects")
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
async def capture_lead(lead: LeadCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # Match lead with project
    project = db.query(models.Project).filter(models.Project.name == lead.project_name).first()
    if not project:
        # For MVP, if project not found, just assign to the first one or create a dummy
        project = db.query(models.Project).first()
        if not project:
             raise HTTPException(status_code=404, detail="No projects found to assign lead")

    db_lead = models.Lead(
        name=lead.name,
        phone_number=lead.phone_number,
        email=lead.email,
        project_id=project.id,
        status="New"
    )
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)

    # Trigger WhatsApp qualification asynchronously
    background_tasks.add_task(trigger_whatsapp_qualification, db_lead.id)

    return {"message": "Lead captured successfully", "lead_id": db_lead.id}

@app.get("/v1/leads")
def list_leads(db: Session = Depends(get_db)):
    return db.query(models.Lead).all()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
