import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy.orm import Session, joinedload
from proppulse_os.core.database import SessionLocal
from proppulse_os.core.config import settings
from proppulse_os.lead_engine import models
from proppulse_os.vector_search.search import SemanticSearchService
from proppulse_os.analytics.velocity import get_conversion_rate, get_lead_velocity
from proppulse_os.market_intel.engine import MarketIntelEngine
import requests
import time

st.set_page_config(page_title=f"{settings.PROJECT_NAME} OS Enterprise", layout="wide")

# Custom CSS for Premium Look
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: white; padding: 20px; border-radius: 10px; border: 1px solid #eee; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #f1f3f5; padding: 10px 20px; border-radius: 5px; font-weight: 600; }
    .stTabs [aria-selected="true"] { background-color: #007bff; color: white !important; }
    .lead-card { background-color: white; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #007bff; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    .market-badge { background-color: #e3f2fd; color: #0d47a1; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }
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

st.title(f"🚀 {tenant.brokerage_name} Operating System")

# --- SEMANTIC SEARCH IN SIDEBAR ---
st.sidebar.divider()
st.sidebar.subheader("🔍 Semantic Project Search")
search_query = st.sidebar.text_input("Find projects with...", placeholder="e.g. 3BHK with clubhouse")
if search_query:
    db = SessionLocal()
    search_service = SemanticSearchService(db)
    results = search_service.search_projects(search_query, tenant.id)
    db.close()
    if results:
        for r in results:
            st.sidebar.caption(f"🏢 {r['name']} ({r['micro_market']})")
    else:
        st.sidebar.caption("No matching assets found.")

# --- DEMO TOOL IN SIDEBAR ---
with st.sidebar.expander("⚡ Instant Demo: Lead Injection"):
    demo_name = st.text_input("Buyer Name", "Vikram Singh")
    demo_phone = st.text_input("WhatsApp Number", "+919876543210")
    if projects:
        demo_proj = st.selectbox("Select Project", [p.name for p in projects])
        if st.button("🚀 Simulate Ad Response"):
            try:
                api_url = "http://api:8000/v1/leads" if settings.DATABASE_URL.startswith("postgresql") else "http://localhost:8000/v1/leads"
                resp = requests.post(
                    api_url,
                    headers={"X-API-Key": auth_key},
                    json={"name": demo_name, "phone_number": demo_phone, "project_name": demo_proj}
                )
                if resp.status_code == 200:
                    st.success("Lead Captured & AI Brain Triggered!")
                    time.sleep(1)
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(f"Error: {resp.text}")
            except Exception as e:
                st.error(f"API unreachable: {e}")

tab1, tab2, tab3, tab4 = st.tabs(["📊 Performance Dashboard", "🔥 AI Lead Brain", "🌍 Market Intelligence", "🏢 Asset Knowledge"])

with tab1:
    st.header("PropPulse Analytics Engine")
    c1, c2, c3, c4 = st.columns(4)

    conversion = get_conversion_rate(tenant.id)
    velocity = get_lead_velocity(tenant.id)

    c1.metric("Leads Ingested", len(leads))
    c2.metric("Conversion (MQL)", f"{int(conversion)}%", delta="Enterprise Grade")
    c3.metric("Lead Velocity", f"{velocity:.1f}/day", delta="High Volume")
    c4.metric("Ad Spend ROI", "3.4x", delta="Optimized")

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
            # Conversion Trend Mock
            trend_data = pd.DataFrame({
                'Date': pd.date_range(start='2024-01-01', periods=7),
                'Leads': [10, 15, 8, 22, 18, 25, 30]
            })
            fig_trend = px.line(trend_data, x='Date', y='Leads', title='Daily Ingestion Velocity')
            st.plotly_chart(fig_trend, use_container_width=True)

with tab2:
    st.header("🔥 AI Lead Brain: Intent Extraction")
    hot_leads = [l for l in leads if l.qualification_score >= 60]
    if hot_leads:
        for l in hot_leads:
            st.markdown(f"""
                <div class="lead-card">
                    <div style="display: flex; justify-content: space-between;">
                        <div>
                            <span style="font-size: 1.2em; font-weight: bold;">👤 {l.name}</span> <span class="market-badge">{l.intent_type or 'General'}</span><br/>
                            <span style="color: #666;">Target: {l.project.name if l.project else 'N/A'}</span>
                        </div>
                        <div style="text-align: right;">
                            <span style="font-size: 1.5em; font-weight: bold; color: #007bff;">{l.qualification_score}%</span><br/>
                            <span style="font-size: 0.8em; color: #888;">AI SCORE</span>
                        </div>
                    </div>
                    <div style="margin-top: 10px; display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; font-size: 0.9em; color: #444;">
                        <div>📍 <b>Pref:</b> {l.location_pref or 'N/A'}</div>
                        <div>💰 <b>Budget:</b> {l.budget_range or 'TBD'}</div>
                        <div>⏱️ <b>Urgency:</b> {l.purchase_urgency or 'Unknown'}</div>
                    </div>
                    <div style="margin-top: 10px; font-style: italic; color: #007bff; border-top: 1px solid #eee; padding-top: 5px;">
                        "AI Logic: {l.conversation_summary}"
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"Push to Salesforce", key=f"crm_{l.id}"):
                st.toast(f"Lead {l.name} synced!")
    else:
        st.info("No high-intent profiles detected.")

with tab3:
    st.header("🌍 Market & Competitor Intelligence")
    db = SessionLocal()
    intel_engine = MarketIntelEngine(db)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Micro-Market Pulse")
        markets = ["Sarjapur", "Whitefield", "Indiranagar"]
        for m in markets:
            pulse = intel_engine.analyze_market_momentum(m)
            with st.container(border=True):
                st.write(f"📍 **{m}**")
                st.write(f"Velocity: **{pulse['ad_velocity']}**")
                st.write(f"Price: {pulse['price_trend']}")
                st.progress(min(pulse['momentum_score']/20, 1.0))
        db.close()

    with col2:
        st.subheader("Competitor Ad Strategy Tracking")
        if ads:
            for a in ads:
                with st.container(border=True):
                    st.write(f"**Builder:** {a.builder}")
                    st.write(f"**Offer:** {a.offer}")
                    st.caption(f"Hook: {a.hook}")
        else:
            st.info("Initializing scanning agents...")

with tab4:
    st.header("🏢 Enterprise Asset Knowledge")
    if projects:
        for p in projects:
            with st.expander(f"🏢 {p.name} - {p.micro_market}"):
                col1, col2 = st.columns(2)
                col1.write(f"**Base Price:** ₹{p.base_price_sqft}/sqft")
                col1.write(f"**Possession:** {p.possession_year}")
                col2.write(f"**Amenities:** {p.amenities}")
                st.button(f"Generate AI Brochure for {p.name}", key=f"brochure_{p.id}")
    else: st.info("No project assets ingested.")

if st.sidebar.checkbox("Show System Transparency"):
    st.divider()
    st.header("📜 Traceability Logs")
    db = SessionLocal()
    logs = db.query(models.AuditLog).filter(models.AuditLog.brokerage_id == tenant.id).order_by(models.AuditLog.created_at.desc()).all()
    db.close()
    if logs:
        st.table(pd.DataFrame([{"Time": l.created_at.strftime("%H:%M:%S"), "Event": l.event_type, "Details": l.details} for l in logs]))
