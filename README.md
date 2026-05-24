# PropPulse OS - Real Estate Growth Engine

PropPulse OS is a professional, B2B-ready AI operating system for real estate developers and agencies. It automates lead qualification, monitors market trends, and provides deep pipeline intelligence.

## 🏗️ Architecture

- **Lead Engine**: FastAPI-based ingestion with strict E.164 phone validation and multi-tenant isolation.
- **WhatsApp Automation**: Asynchronous qualification loop simulating human-like interaction and scoring.
- **Market Intel**: Ad-spy and brochure parsing layers (Phase 1 mock) integrated into the core schema.
- **Enterprise Dashboard**: Streamlit-based command center for revenue tracking and conversation audit.
- **Persistence**: SQLAlchemy + Alembic, prepared for `pgvector` on PostgreSQL.

## 🚀 Deployment

### Docker Compose
```bash
docker-compose up --build
```

### Manual Setup
1. `pip install -r requirements.txt`
2. `alembic upgrade head`
3. `uvicorn api.main:app --host 0.0.0.0 --port 8000`
4. `streamlit run dashboard/app.py`

## 🔒 Security
All ingestion endpoints are protected by `X-API-Key` authentication. Data is isolated per tenant using the `X-Brokerage-ID` header.

## 📈 Roadmap
- [ ] Native `pgvector` integration for semantic brochure search.
- [ ] Real WhatsApp Business API hooks.
- [ ] CRM sync (Salesforce/HubSpot).
