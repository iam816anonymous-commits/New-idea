from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    brokerage_id = Column(String, index=True, default="default")
    name = Column(String, index=True)
    micro_market = Column(String, index=True)
    base_price_sqft = Column(Float)
    possession_year = Column(Integer)
    amenities = Column(Text)
    # Simulated vector column for embeddings (storing as Text for SQLite)
    amenities_embeddings = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    leads = relationship("Lead", back_populates="project")

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    brokerage_id = Column(String, index=True, default="default")
    name = Column(String, index=True)
    phone_number = Column(String, index=True)
    email = Column(String, index=True, nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    source = Column(String, default="Meta Ads") # Meta Ads, Google Ads, Organic, Manual
    status = Column(String, default="New") # New, Contacted, Qualified, Site Visit Scheduled, Lost
    qualification_score = Column(Integer, default=0)
    chat_history = Column(Text, nullable=True)
    budget_range = Column(String, nullable=True)
    response_time_seconds = Column(Integer, nullable=True) # To track lead velocity
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="leads")

class AdIntelligence(Base):
    __tablename__ = "ad_intelligence"

    id = Column(Integer, primary_key=True, index=True)
    brokerage_id = Column(String, index=True, default="default")
    builder = Column(String, index=True)
    project_name = Column(String)
    micro_market = Column(String, index=True)
    offer = Column(Text)
    hook = Column(Text)
    creative_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
