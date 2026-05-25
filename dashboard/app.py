import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy.orm import Session, joinedload
from core.database import SessionLocal
from core.config import settings
from api import models
import requests
import time

st.set_page_config(page_title=f"{settings.PROJECT_NAME} B2B Enterprise", layout="wide")

# Custom CSS for Premium Look
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: white; padding: 20px; border-radius: 10px; border: 1px solid #eee; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #f1f3f5; padding: 10px 20px; border-radius: 5px; font-weight: 600; }
    .stTabs [aria-selected="true"] { background-color: #007bff; color: white !important; }
    .lead-card { background-color: white; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #007bff; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# Sidebar - Simulated Authentication
st.sidebar.title("🔐 PropPulse OS")
auth_key = st.sidebar.text_input("Enter API Key", type="password", value=settings.API_KEY)

@st.cache_data(ttl=10)
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

st.title(f"🚀 {tenant.brokerage_name} Command Center")

# --- DEMO TOOL IN SIDEBAR ---
with st.sidebar.expander("⚡ Instant Demo: Lead Injection"):
    demo_name = st.text_input("Buyer Name", "Anish Kumar")
    demo_phone = st.text_input("WhatsApp Number", "+919888877777")
    if projects:
        demo_proj = st.selectbox("Select Project", [p.name for p in projects])
        if st.button("🚀 Simulate Ad Response"):
            try:
                # Use docker service name if available, fallback to localhost
                api_url = "http://api:8000/v1/leads" if settings.DATABASE_URL.startswith("postgresql") else "http://localhost:8000/v1/leads"
                resp = requests.post(
                    api_url,
                    headers={"X-API-Key": auth_key},
                    json={"name": demo_name, "phone_number": demo_phone, "project_name": demo_proj}
                )
                if resp.status_code == 200:
                    st.success("Lead Captured & Bot Triggered!")
                    time.sleep(1)
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(f"Error: {resp.text}")
            except Exception as e:
                st.error(f"API unreachable: {e}")
    else:
        st.warning("Create a project first.")

tab1, tab2, tab3, tab4 = st.tabs(["📊 Performance Dashboard", "🔥 High-Intent Leads", "🌍 Market Intelligence", "🏢 Asset Knowledge"])

with tab1:
    st.header("PropPulse Growth Analytics")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Leads Ingested", len(leads))
    qualified_count = len([l for l in leads if l.status == "Qualified"])
    c2.metric("Qualified (MQL)", qualified_count, delta=f"{int(qualified_count/len(leads)*100) if leads else 0}% Rate")

    avg_score = int(sum([l.qualification_score for l in leads])/len(leads)) if leads else 0
    c3.metric("Avg. Quality Score", f"{avg_score}%")
    c4.metric("Ad Spend Efficiency", "+24%", delta="Optimized")

    if leads:
        df_leads = pd.DataFrame([{
            "ID": l.id,
            "Name": l.name,
            "Project": l.project.name if l.project else "N/A",
            "Status": l.status,
            "Score": l.qualification_score,
            "Created At": l.created_at
        } for l in leads])

        col_left, col_right = st.columns(2)

        with col_left:
            status_counts = df_leads['Status'].value_counts().reset_index()
            fig_pie = px.pie(status_counts, values='count', names='Status', title='Lead Lifecycle Stage',
                             hole=.4, color_discrete_sequence=px.colors.qualitative.Bold)
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_right:
            # Score Gauge
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = avg_score,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Aggregate Portfolio Quality"},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#007bff"},
                    'steps' : [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "gray"}],
                    'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 90}}))
            st.plotly_chart(fig_gauge, use_container_width=True)

        st.subheader("Real-Time Ingestion Feed")
        st.dataframe(df_leads.sort_values(by="Created At", ascending=False), use_container_width=True, hide_index=True)
    else:
        st.info("No leads captured. Use the 'Lead Injection' tool in the sidebar to populate.")

with tab2:
    st.header("🔥 Hot Leads (Ready for Sales)")
    hot_leads = [l for l in leads if l.qualification_score >= 70]
    if hot_leads:
        for l in hot_leads:
            st.markdown(f"""
                <div class="lead-card">
                    <div style="display: flex; justify-content: space-between;">
                        <div>
                            <span style="font-size: 1.2em; font-weight: bold;">👤 {l.name}</span><br/>
                            <span style="color: #666;">Interested in: {l.project.name if l.project else 'N/A'}</span>
                        </div>
                        <div style="text-align: right;">
                            <span style="font-size: 1.5em; font-weight: bold; color: #007bff;">{l.qualification_score}%</span><br/>
                            <span style="font-size: 0.8em; color: #888;">AI SCORE</span>
                        </div>
                    </div>
                    <div style="margin-top: 10px; font-style: italic; color: #444; border-top: 1px solid #eee; padding-top: 5px;">
                        "AI Summary: {l.conversation_summary or 'Qualification in progress...'}"
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"Handover to Sales Agent", key=f"hand_{l.id}"):
                st.toast(f"Lead {l.name} pushed to Sales CRM!")
    else:
        st.info("No high-intent leads detected yet.")

with tab3:
    st.header("🌍 Micro-Market Intelligence")
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Competitor Ad Monitoring")
        if ads:
            for a in ads:
                with st.container(border=True):
                    st.write(f"**Builder:** {a.builder}")
                    st.write(f"**Project:** {a.project_name}")
                    st.info(f"Offer: {a.offer}")
        else:
            st.info("Scanning local Meta/TikTok ads...")

    with col2:
        st.subheader("Micro-Market Pricing Heatmap (Mock)")
        # Mock data for micro-market heat map
        market_data = pd.DataFrame({
            'Market': ['Sarjapur', 'Whitefield', 'Indiranagar', 'Electronic City', 'Hebbal'],
            'Avg Price': [9500, 10500, 16000, 7500, 11000],
            'Lead Volume': [150, 200, 80, 250, 120]
        })
        fig_market = px.bar(market_data, x='Market', y='Avg Price', color='Lead Volume',
                           title='Price vs Demand Velocity', labels={'Avg Price': 'Price (per sqft)'})
        st.plotly_chart(fig_market, use_container_width=True)

with tab4:
    st.header("🏢 Asset Knowledge Base")
    if projects:
        for p in projects:
            with st.expander(f"🏢 {p.name} - {p.micro_market}"):
                col1, col2 = st.columns(2)
                col1.write(f"**Base Price:** ₹{p.base_price_sqft}/sqft")
                col1.write(f"**Possession:** {p.possession_year}")
                col2.write(f"**Amenities:** {p.amenities}")
                st.button(f"Update Brochure Parsing for {p.name}", key=f"sync_{p.id}")
    else: st.info("No project assets ingested.")

# Hidden log section for admin
if st.sidebar.checkbox("Show System Logs"):
    st.divider()
    st.header("📜 System Logs")
    db = SessionLocal()
    logs = db.query(models.AuditLog).filter(models.AuditLog.brokerage_id == tenant.id).order_by(models.AuditLog.created_at.desc()).all()
    db.close()
    if logs:
        st.table(pd.DataFrame([{"Time": l.created_at.strftime("%H:%M:%S"), "Event": l.event_type, "Details": l.details} for l in logs]))
