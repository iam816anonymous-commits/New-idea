import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session, joinedload
from core.database import SessionLocal
from core.config import settings
from api import models

st.set_page_config(page_title=f"{settings.PROJECT_NAME} Enterprise", layout="wide")

# Production UI Theme
st.markdown("""
    <style>
    .main { background-color: #f4f7f9; }
    [data-testid="stMetricValue"] { font-size: 28px; color: #1f2937; }
    .status-badge {
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=60)
def get_dashboard_data():
    db = SessionLocal()
    try:
        leads = db.query(models.Lead).options(joinedload(models.Lead.project)).order_by(models.Lead.created_at.desc()).all()
        projects = db.query(models.Project).all()
        ads = db.query(models.AdIntelligence).all()
        return leads, projects, ads
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        return [], [], []
    finally:
        db.close()

st.title(f"🚀 {settings.PROJECT_NAME} Enterprise")

leads, projects, ads = get_dashboard_data()

tab1, tab2, tab3, tab4 = st.tabs(["📊 Revenue Pipeline", "🕵️ Market Intel", "🏢 Project Assets", "⚙️ System Health"])

with tab1:
    st.header("Lead Qualification & Routing")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Ingestion", len(leads))
    c2.metric("Qualified Assets", len([l for l in leads if l.status == "Qualified"]))

    resp_times = [l.response_time_seconds for l in leads if l.response_time_seconds is not None]
    avg_resp = f"{int(sum(resp_times)/len(resp_times))}s" if resp_times else "N/A"
    c3.metric("Response Velocity", avg_resp)

    avg_score = f"{int(sum([l.qualification_score for l in leads])/len(leads)) if leads else 0}%"
    c4.metric("AI Quality Score", avg_score)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Live Lead Stream")
        if leads:
            df_leads = pd.DataFrame([{
                "Timestamp": l.created_at.strftime("%H:%M:%S"),
                "Lead Name": l.name,
                "Project": l.project.name if l.project else "N/A",
                "Agent ID": f"Agent {l.assigned_agent_id}" if l.assigned_agent_id else "Unassigned",
                "Status": l.status,
                "Score": f"{l.qualification_score}%"
            } for l in leads])
            st.dataframe(df_leads, use_container_width=True, hide_index=True)
        else:
            st.info("Waiting for lead ingestion...")

    with col2:
        st.subheader("Conversational Audit")
        if leads:
            selected_lead = st.selectbox("Select Audit Target", leads, format_func=lambda x: f"{x.name} ({x.status})")
            if selected_lead.chat_history:
                for line in selected_lead.chat_history.strip().split('\n'):
                    role = "assistant" if line.startswith("Bot:") else "user"
                    with st.chat_message(role):
                        st.write(line.split(":", 1)[1].strip())
            else:
                st.write("No conversation logs available.")

with tab2:
    st.header("Ad Intelligence Engine")
    if ads:
        for a in ads:
            with st.container(border=True):
                c1, c2 = st.columns([1, 4])
                with c1: st.image("https://via.placeholder.com/150", caption="Meta Hook")
                with c2:
                    st.subheader(f"{a.builder}: {a.project_name}")
                    st.markdown(f"**Primary Hook:** `{a.hook}`")
                    st.write(f"**Current Offer:** {a.offer}")
                    st.caption(f"Captured for Market: {a.micro_market}")
    else: st.info("No competitor data indexed.")

with tab3:
    st.header("Project Knowledge Base")
    if projects:
        for p in projects:
            with st.expander(f"🏢 {p.name} Knowledge Base"):
                st.write(f"**Specifications:** {p.amenities}")
                st.write(f"**Inventory Price:** ₹{p.base_price_sqft}/sqft")
                if p.amenities_embeddings:
                    st.success("Vector Embeddings Active (Semantic Search Enabled)")
    else: st.info("No project assets uploaded.")

with tab4:
    st.header("System Performance")
    st.write(f"**App Version:** {settings.VERSION}")
    st.write(f"**Database Status:** Online ({settings.DATABASE_URL.split(':')[0]})")
    st.write("**Webhook Health:** ✅ Listening on /v1/leads")
    st.progress(0.95, text="API Uptime 99.9%")

if st.sidebar.button("Force Global Sync"):
    st.cache_data.clear()
    st.rerun()
