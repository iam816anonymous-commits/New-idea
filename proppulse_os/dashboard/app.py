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
from proppulse_os.analytics.recommendations import GrowthAdvisor
from proppulse_os.market_intel.engine import MarketIntelEngine
import requests
import time

st.set_page_config(page_title=f"{settings.PROJECT_NAME} OS", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for Premium Look
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: white; padding: 15px; border-radius: 12px; border: 1px solid #eee; box-shadow: 0 4px 6px rgba(0,0,0,0.02); }
    .kpi-card { background: linear-gradient(135deg, #007bff 0%, #0056b3 100%); color: white; padding: 20px; border-radius: 15px; margin-bottom: 20px; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #f1f3f5; padding: 10px 20px; border-radius: 8px; font-weight: 600; border: none; }
    .stTabs [aria-selected="true"] { background-color: #007bff; color: white !important; }
    .lead-card { background-color: white; padding: 15px; border-radius: 12px; margin-bottom: 12px; border-left: 6px solid #007bff; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .market-badge { background-color: #e3f2fd; color: #0d47a1; padding: 4px 10px; border-radius: 20px; font-size: 0.75em; font-weight: 700; text-transform: uppercase; }
    .priority-high { color: #d32f2f; font-weight: bold; }
    .priority-medium { color: #f57c00; font-weight: bold; }
    .advisor-card { background-color: #fff; border-left: 4px solid #4caf50; padding: 10px 15px; margin-bottom: 10px; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

# Sidebar - Simulated Authentication
st.sidebar.title("🚀 PropPulse OS")
auth_key = st.sidebar.text_input("Enter API Key", type="password", value=settings.API_KEY)

@st.cache_data(ttl=5)
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

# --- TOP BAR KPI (Mobile First View) ---
st.markdown(f"### ⚡ Executive Pulse: {tenant.brokerage_name}")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.markdown('<div class="stMetric"><b>Revenue Pipeline</b><br/><span style="font-size: 1.8em; color: #007bff;">₹4.2 Cr</span></div>', unsafe_allow_html=True)
with kpi2:
    hot_count = len([l for l in leads if l.qualification_score >= 75])
    st.markdown(f'<div class="stMetric"><b>Hot Leads</b><br/><span style="font-size: 1.8em; color: #d32f2f;">{hot_count}</span></div>', unsafe_allow_html=True)
with kpi3:
    st.markdown('<div class="stMetric"><b>Market Sentiment</b><br/><span style="font-size: 1.8em; color: #4caf50;">Bullish</span></div>', unsafe_allow_html=True)
with kpi4:
    conversion = get_conversion_rate(tenant.id)
    st.markdown(f'<div class="stMetric"><b>Conversion Rate</b><br/><span style="font-size: 1.8em; color: #007bff;">{int(conversion)}%</span></div>', unsafe_allow_html=True)

st.divider()

# Sidebar Search & Demo
st.sidebar.divider()
st.sidebar.subheader("🔍 Project Discovery")
search_query = st.sidebar.text_input("Semantic Search", placeholder="e.g. Sarjapur Luxury Villas")
if search_query:
    db = SessionLocal()
    search_service = SemanticSearchService(db)
    results = search_service.search_projects(search_query, tenant.id)
    db.close()
    if results:
        for r in results: st.sidebar.caption(f"🏢 {r['name']} ({r['micro_market']})")
    else: st.sidebar.caption("No results.")

with st.sidebar.expander("⚡ Growth Tools"):
    if st.button("🚀 Inject Test Lead"):
        try:
            api_url = "http://api:8000/v1/leads" if settings.DATABASE_URL.startswith("postgresql") else "http://localhost:8000/v1/leads"
            requests.post(api_url, headers={"X-API-Key": auth_key}, json={"name": "Test User", "phone_number": "+919000000000", "project_name": projects[0].name if projects else "Default"})
            st.success("Lead Injected!")
            st.cache_data.clear()
            st.rerun()
        except: st.error("API Error")

tab1, tab2, tab3, tab4 = st.tabs(["📊 Growth Analytics", "🧠 AI Lead Brain", "🕵️ Market Intelligence", "💡 Advisor"])

with tab1:
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("Lead Ingestion & Lifecycle")
        if leads:
            df_leads = pd.DataFrame([{"Stage": l.status, "Count": 1} for l in leads])
            fig_funnel = px.funnel(df_leads.groupby("Stage").count().reset_index(), x='Count', y='Stage', title="Sales Funnel Efficiency")
            st.plotly_chart(fig_funnel, use_container_width=True)
        else: st.info("No data yet.")

    with col_right:
        st.subheader("Ingestion Velocity")
        velocity = get_lead_velocity(tenant.id)
        st.metric("Daily Avg", f"{velocity:.1f} leads", delta="+12%")

        # Micro-market share
        if projects:
            markets = [p.micro_market for p in projects]
            fig_market = px.pie(names=markets, title="Asset Portfolio Share", hole=.4)
            st.plotly_chart(fig_market, use_container_width=True)

with tab2:
    st.header("🧠 Deep Lead Profiling")
    hot_leads = sorted([l for l in leads if l.qualification_score >= 60], key=lambda x: x.qualification_score, reverse=True)
    if hot_leads:
        for l in hot_leads:
            with st.container():
                st.markdown(f"""
                <div class="lead-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-size: 1.3em; font-weight: 800; color: #212529;">{l.name}</span>
                            <span class="market-badge">{l.intent_type or 'MQL'}</span>
                        </div>
                        <div style="text-align: right;">
                            <span style="font-size: 1.6em; font-weight: 900; color: #007bff;">{l.qualification_score}%</span><br/>
                            <span style="font-size: 0.7em; font-weight: bold; color: #adb5bd;">AI CONFIDENCE: {l.ai_confidence or '92'}%</span>
                        </div>
                    </div>
                    <div style="margin-top: 12px; display: grid; grid-template-columns: 1.5fr 1fr 1fr; gap: 15px; background: #f8f9fa; padding: 10px; border-radius: 8px; border: 1px solid #eee;">
                        <div>🏢 <b>Project:</b> {l.project.name if l.project else 'N/A'}</div>
                        <div>💰 <b>Budget:</b> {l.budget_range or 'N/A'}</div>
                        <div>⏱️ <b>Urgency:</b> {l.purchase_urgency or 'N/A'}</div>
                    </div>
                    <div style="margin-top: 10px; font-size: 0.9em; color: #495057;">
                        <b>AI Reasoning:</b> {l.conversation_summary}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                col_btn1, col_btn2 = st.columns([1, 4])
                col_btn1.button("CRM Sync", key=f"s_{l.id}")
                col_btn2.button("View Full Chat Transcript", key=f"t_{l.id}", type="secondary")
    else: st.info("No high-intent profiles detected.")

with tab3:
    st.header("🕵️ Real-Time Market Intelligence")
    st.markdown('<div style="background: #e8f5e9; padding: 5px 15px; border-radius: 20px; color: #2e7d32; font-weight: 600; font-size: 0.8em; display: inline-block;">● AGENTS SCANNING LIVE</div>', unsafe_allow_html=True)

    db = SessionLocal()
    intel = MarketIntelEngine(db)
    pulse = intel.analyze_market_momentum("Sarjapur")
    db.close()

    m1, m2, m3 = st.columns(3)
    m1.metric("Ad Spend Velocity", pulse['ad_velocity'], delta="+15% (Competitor avg)")
    m2.metric("Market Sentiment", pulse['sentiment'], delta=pulse['price_trend'])
    m3.metric("Inventory Pulse", "Critical", delta="-5% Supply")

    st.subheader("Competitor Ad Hooks & Offers")
    if ads:
        for a in ads:
            with st.container(border=True):
                st.subheader(f"{a.builder}: {a.project_name}")
                st.write(f"🪝 **Hook:** {a.hook}")
                st.success(f"🎁 Offer: {a.offer}")
    else: st.info("Indexing local campaigns...")

with tab4:
    st.header("💡 PropPulse Growth Advisor")
    st.caption("Actionable insights powered by Lead Brain & Market Intel")

    db = SessionLocal()
    advisor = GrowthAdvisor(db)
    recs = advisor.get_recommendations(tenant.id)
    db.close()

    for r in recs:
        priority_class = f"priority-{r['priority'].lower()}"
        st.markdown(f"""
            <div class="advisor-card">
                <div style="display: flex; justify-content: space-between;">
                    <span style="font-weight: 800; font-size: 1.1em; color: #2c3e50;">{r['title']}</span>
                    <span class="{priority_class}">{r['priority']} Priority</span>
                </div>
                <div style="color: #666; font-size: 0.9em; margin-top: 5px;">
                    <b>{r['category']}:</b> {r['body']}
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.button("Execute Recommendation", key=f"rec_{r['title']}")

if st.sidebar.checkbox("Show Infrastructure Logs"):
    st.divider()
    db = SessionLocal()
    logs = db.query(models.AuditLog).filter(models.AuditLog.brokerage_id == tenant.id).order_by(models.AuditLog.created_at.desc()).all()
    db.close()
    if logs:
        st.table(pd.DataFrame([{"Time": l.created_at.strftime("%H:%M:%S"), "Event": l.event_type} for l in logs]))
