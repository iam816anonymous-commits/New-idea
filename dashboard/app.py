import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session, joinedload
from core.database import SessionLocal
from api import models

st.set_page_config(page_title="PropPulse OS - Growth Engine", layout="wide")

st.title("🚀 PropPulse OS - Real Estate Growth Engine")

def get_data():
    db = SessionLocal()
    try:
        leads = db.query(models.Lead).options(joinedload(models.Lead.project)).all()
        projects = db.query(models.Project).all()
        ads = db.query(models.AdIntelligence).all()
        return leads, projects, ads
    finally:
        db.close()

leads, projects, ads = get_data()

tab1, tab2, tab3 = st.tabs(["📊 Lead Engine", "🕵️ Ad Intelligence", "🏗️ Project Knowledge"])

with tab1:
    st.header("Lead Qualification Pipeline")

    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Leads", len(leads))
    c2.metric("Qualified", len([l for l in leads if l.status == "Qualified"]))
    c3.metric("Avg Score", f"{int(sum([l.qualification_score for l in leads])/len(leads)) if leads else 0}%")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Active Lead Tracker")
        if leads:
            df_leads = pd.DataFrame([{
                "ID": l.id,
                "Name": l.name,
                "Project": l.project.name if l.project else "N/A",
                "Status": l.status,
                "Score": l.qualification_score,
                "Created At": l.created_at.strftime("%Y-%m-%d %H:%M")
            } for l in leads])
            st.dataframe(df_leads, use_container_width=True)
        else:
            st.info("No leads captured.")

    with col2:
        st.subheader("Chat Review")
        if leads:
            selected_lead_id = st.selectbox("Select Lead", [l.id for l in leads], format_func=lambda x: next(l.name for l in leads if l.id == x))
            selected_lead = next(l for l in leads if l.id == selected_lead_id)
            st.text_area("WhatsApp History", selected_lead.chat_history or "No history", height=300)
        else:
            st.info("No leads.")

with tab2:
    st.header("Competitor Ad Monitoring")
    if ads:
        df_ads = pd.DataFrame([{
            "Builder": a.builder,
            "Project": a.project_name,
            "Micro Market": a.micro_market,
            "Offer": a.offer,
            "Hook": a.hook
        } for a in ads])
        st.table(df_ads)
    else:
        st.info("No ad intelligence gathered yet.")

with tab3:
    st.header("Project Knowledge Base")
    if projects:
        for p in projects:
            with st.expander(f"🏢 {p.name} - {p.micro_market}"):
                st.write(f"**Base Price:** ₹{p.base_price_sqft}/sqft")
                st.write(f"**Possession:** {p.possession_year}")
                st.write(f"**Amenities:** {p.amenities}")
                if p.amenities_embeddings:
                    st.info("✅ Vector Embeddings Generated")
    else:
        st.info("No projects ingested.")

if st.button("🔄 Refresh OS Data"):
    st.rerun()
