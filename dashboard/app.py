import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session, joinedload
from core.database import SessionLocal
from core.config import settings
from api import models

st.set_page_config(page_title=f"{settings.PROJECT_NAME} B2B Enterprise", layout="wide")

# Sidebar - Simulated Authentication
st.sidebar.title("🔐 Tenant Access")
auth_key = st.sidebar.text_input("Enter API Key", type="password", value=settings.API_KEY)

@st.cache_data(ttl=30)
def get_enterprise_data(api_key: str):
    db = SessionLocal()
    try:
        tenant = db.query(models.Tenant).filter(models.Tenant.api_key == api_key).first()
        if not tenant:
            return None, [], [], []

        leads = db.query(models.Lead).filter(models.Lead.brokerage_id == tenant.id).options(joinedload(models.Lead.project)).all()
        projects = db.query(models.Project).filter(models.Project.brokerage_id == tenant.id).all()
        ads = db.query(models.AdIntelligence).filter(models.AdIntelligence.brokerage_id == tenant.id).all()
        return tenant, leads, projects, ads
    finally:
        db.close()

tenant, leads, projects, ads = get_enterprise_data(auth_key)

if not tenant:
    st.error("Access Denied: Invalid API Key")
    st.stop()

st.title(f"🚀 {tenant.brokerage_name} - Command Center")

tab1, tab2, tab3, tab4 = st.tabs(["📊 Revenue Pipeline", "🕵️ Market Intel", "🏢 Project Knowledge", "📜 Audit Logs"])

with tab1:
    st.header("Pipeline Intelligence")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Ingestion", len(leads))
    c2.metric("Qualified Assets", len([l for l in leads if l.status == "Qualified"]))

    avg_score = f"{int(sum([l.qualification_score for l in leads])/len(leads)) if leads else 0}%"
    c3.metric("AI Quality Score", avg_score)

    if leads:
        df_leads = pd.DataFrame([{
            "ID": l.id,
            "Name": l.name,
            "Project": l.project.name if l.project else "N/A",
            "Status": l.status,
            "Score": f"{l.qualification_score}%",
            "Created At": l.created_at.strftime("%Y-%m-%d")
        } for l in leads])
        st.dataframe(df_leads, use_container_width=True, hide_index=True)

        # Export
        csv = df_leads.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export Lead Data (CSV)", data=csv, file_name="leads_export.csv", mime="text/csv")
    else:
        st.info("No leads captured.")

with tab2:
    st.header("Market Intelligence Engine")
    if ads:
        for a in ads:
            with st.container(border=True):
                st.subheader(f"{a.builder}: {a.project_name}")
                st.write(f"**Hook:** {a.hook}")
                st.write(f"**Offer:** {a.offer}")
    else: st.info("No competitor data indexed.")

with tab3:
    st.header("Project Knowledge Base")
    if projects:
        for p in projects:
            with st.expander(f"🏢 {p.name} Assets"):
                st.write(f"**Specs:** {p.amenities}")
                st.button(f"Approve Data for {p.name}", key=f"app_{p.id}")
    else: st.info("No project assets ingested.")

with tab4:
    st.header("B2B Audit Trail")
    db = SessionLocal()
    logs = db.query(models.AuditLog).filter(models.AuditLog.brokerage_id == tenant.id).order_by(models.AuditLog.created_at.desc()).all()
    db.close()

    if logs:
        df_logs = pd.DataFrame([{
            "Time": l.created_at.strftime("%H:%M:%S"),
            "Event": l.event_type,
            "Details": l.details
        } for l in logs])
        st.table(df_logs)
    else:
        st.info("No audit logs available.")
