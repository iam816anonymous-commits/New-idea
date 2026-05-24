import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session, joinedload
from core.database import SessionLocal
from api import models

st.set_page_config(page_title="PropPulse OS Professional", layout="wide")

st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 PropPulse OS Professional")

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

tab1, tab2, tab3, tab4 = st.tabs(["📊 Lead Engine", "🕵️ Ad Intelligence", "🏗️ Project Knowledge", "📈 Market Insights"])

with tab1:
    st.header("Lead Qualification Pipeline")

    # Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Leads", len(leads))
    c2.metric("Qualified", len([l for l in leads if l.status == "Qualified"]))

    # Calculate avg response time
    resp_times = [l.response_time_seconds for l in leads if l.response_time_seconds is not None]
    avg_resp = f"{int(sum(resp_times)/len(resp_times))}s" if resp_times else "N/A"
    c3.metric("Avg Response Time", avg_resp)

    c4.metric("Avg Score", f"{int(sum([l.qualification_score for l in leads])/len(leads)) if leads else 0}%")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Active Lead Tracker")
        if leads:
            df_leads = pd.DataFrame([{
                "ID": l.id,
                "Name": l.name,
                "Project": l.project.name if l.project else "N/A",
                "Status": l.status,
                "Score": l.qualification_score,
                "Source": l.source
            } for l in leads])
            st.dataframe(df_leads, use_container_width=True, hide_index=True)
        else:
            st.info("No leads captured.")

    with col2:
        st.subheader("WhatsApp Simulation Review")
        if leads:
            selected_lead_id = st.selectbox("Select Lead", [l.id for l in leads], format_func=lambda x: next(l.name for l in leads if l.id == x))
            selected_lead = next(l for l in leads if l.id == selected_lead_id)

            if selected_lead.chat_history:
                for line in selected_lead.chat_history.strip().split('\n'):
                    if line.startswith("Bot:"):
                        with st.chat_message("assistant"):
                            st.write(line.replace("Bot:", "").strip())
                    elif line.startswith("User:"):
                        with st.chat_message("user"):
                            st.write(line.replace("User:", "").strip())
            else:
                st.write("No chat history.")
        else:
            st.info("No leads.")

with tab2:
    st.header("Competitor Ad Monitoring")
    if ads:
        for a in ads:
            with st.container(border=True):
                c1, c2 = st.columns([1, 3])
                with c1:
                    st.image("https://via.placeholder.com/150", caption="Creative Hook")
                with c2:
                    st.subheader(f"{a.builder} - {a.project_name}")
                    st.info(f"**Hook:** {a.hook}")
                    st.write(f"**Offer:** {a.offer}")
                    st.write(f"**Market:** {a.micro_market}")
    else:
        st.info("No ad intelligence gathered yet.")

with tab3:
    st.header("Project Knowledge Base")
    if projects:
        for p in projects:
            with st.expander(f"🏢 {p.name} - {p.micro_market}"):
                c1, c2 = st.columns(2)
                with c1:
                    st.write(f"**Base Price:** ₹{p.base_price_sqft}/sqft")
                    st.write(f"**Possession:** {p.possession_year}")
                with c2:
                    st.write(f"**Amenities:** {p.amenities}")
                if p.amenities_embeddings:
                    st.success("✅ Semantic Embeddings Loaded (pgvector ready)")
    else:
        st.info("No projects ingested.")

with tab4:
    st.header("Demand Analytics")
    if leads:
        st.subheader("Lead Source Distribution")
        df_source = pd.DataFrame([{"Source": l.source} for l in leads])
        st.bar_chart(df_source["Source"].value_counts())

        st.subheader("Micro-market Demand (Simulated Heatmap)")
        st.map(pd.DataFrame({
            'lat': [12.9716, 12.9279, 12.9668],
            'lon': [77.5946, 77.6271, 77.7499]
        }))
    else:
        st.info("Data insufficient for reports.")

if st.button("🔄 Sync Growth OS"):
    st.rerun()
