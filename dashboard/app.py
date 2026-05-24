import streamlit as st
import pandas as pd
import requests
from sqlalchemy.orm import Session
from core.database import SessionLocal
from api import models

st.set_page_config(page_title="PropPulse AI - Command Center", layout="wide")

st.title("🚀 PropPulse AI - Real Estate Growth OS")
st.subheader("Lead Intelligence & Automation Dashboard")

def get_data():
    db = SessionLocal()
    from sqlalchemy.orm import joinedload
    leads = db.query(models.Lead).options(joinedload(models.Lead.project)).all()
    projects = db.query(models.Project).all()
    db.close()
    return leads, projects

leads, projects = get_data()

# Sidebar Metrics
st.sidebar.header("Pipeline Metrics")
st.sidebar.metric("Total Leads", len(leads))
st.sidebar.metric("Qualified Leads", len([l for l in leads if l.status == "Qualified"]))
st.sidebar.metric("Active Projects", len(projects))

# Main Dashboard
col1, col2 = st.columns(2)

with col1:
    st.write("### Active Leads")
    if leads:
        lead_data = []
        for l in leads:
            lead_data.append({
                "ID": l.id,
                "Name": l.name,
                "Project": l.project.name if l.project else "N/A",
                "Status": l.status,
                "Score": l.qualification_score,
                "Created At": l.created_at
            })
        df_leads = pd.DataFrame(lead_data)
        st.dataframe(df_leads, use_container_width=True)
    else:
        st.info("No leads captured yet.")

with col2:
    st.write("### Qualification Distribution")
    if leads:
        df_leads = pd.DataFrame([{"Status": l.status} for l in leads])
        status_counts = df_leads["Status"].value_counts()
        st.bar_chart(status_counts)
    else:
        st.info("No data for charts.")

st.write("### Lead Details & Chat History")
if leads:
    selected_lead_id = st.selectbox("Select a lead to view details", [l.id for l in leads], format_func=lambda x: next(l.name for l in leads if l.id == x))
    selected_lead = next(l for l in leads if l.id == selected_lead_id)

    c1, c2 = st.columns(2)
    with c1:
        st.write(f"**Name:** {selected_lead.name}")
        st.write(f"**Phone:** {selected_lead.phone_number}")
        st.write(f"**Email:** {selected_lead.email}")
        st.write(f"**Budget:** {selected_lead.budget_range or 'N/A'}")

    with c2:
        st.write("**WhatsApp Chat History:**")
        st.text_area("History", selected_lead.chat_history or "No history yet", height=200)
else:
    st.info("Capture leads to see details.")

if st.button("Refresh Data"):
    st.rerun()
