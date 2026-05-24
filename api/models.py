from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    micro_market = Column(String, index=True)
    base_price_sqft = Column(Float)
    possession_year = Column(Integer)
    amenities = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    leads = relationship("Lead", back_populates="project")

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    phone_number = Column(String, index=True)
    email = Column(String, index=True, nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    status = Column(String, default="New") # New, Contacted, Qualified, Site Visit Scheduled, Lost
    qualification_score = Column(Integer, default=0)
    chat_history = Column(Text, nullable=True)
    budget_range = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="leads")
