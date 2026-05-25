from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from proppulse_os.core.database import Base

class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(Integer, primary_key=True, index=True)
    brokerage_name = Column(String, unique=True, index=True)
    api_key = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    brokerage_id = Column(Integer, ForeignKey("tenants.id"))
    name = Column(String, index=True)
    micro_market = Column(String, index=True)
    base_price_sqft = Column(Float)
    possession_year = Column(Integer)
    amenities = Column(Text)
    amenities_embeddings = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    leads = relationship("Lead", back_populates="project")

class Lead(Base):
    __tablename__ = "leads"
    id = Column(Integer, primary_key=True, index=True)
    brokerage_id = Column(Integer, ForeignKey("tenants.id"))
    name = Column(String, index=True)
    phone_number = Column(String, index=True)
    email = Column(String, index=True, nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    assigned_agent_id = Column(Integer, nullable=True)
    source = Column(String, default="Meta Ads")
    status = Column(String, default="New")
    conversation_summary = Column(String, nullable=True)
    qualification_score = Column(Integer, default=0)
    chat_history = Column(Text, nullable=True)

    # AI Lead Brain profiling
    location_pref = Column(String, nullable=True)
    purchase_urgency = Column(String, nullable=True) # e.g., 30 days, 6 months
    intent_type = Column(String, nullable=True) # Investment vs Self-use
    readiness_score = Column(Integer, default=0)
    budget_range = Column(String, nullable=True)
    response_time_seconds = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="leads")

class AdIntelligence(Base):
    __tablename__ = "ad_intelligence"
    id = Column(Integer, primary_key=True, index=True)
    brokerage_id = Column(Integer, ForeignKey("tenants.id"))
    builder = Column(String, index=True)
    project_name = Column(String)
    micro_market = Column(String, index=True)
    offer = Column(Text)
    hook = Column(Text)
    creative_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    brokerage_id = Column(Integer, ForeignKey("tenants.id"))
    event_type = Column(String) # e.g., LEAD_QUALIFIED, PROJECT_CREATED
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
