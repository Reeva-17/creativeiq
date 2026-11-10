# CREATIVEIQ · Multi-Agent Marketing Operating System

**Module 01: Brand Intelligence Agent (Person 1)**  
**Module 02: Autonomous Creative Director Agent (Person 2)**

---

## Architecture Overview

CREATIVEIQ is designed as a pipeline of specialized autonomous agents:
- **Person 1 (Brand Intelligence Agent)**: Analyzes Brand DNA, competitor research, market gaps, and SWOT analysis. Exposes verified findings via FastAPI contract `BrandIntelligenceReport` v1.0.0.
- **Person 2 (Autonomous Creative Director Agent)**: Consumes Person 1's report, frames strategic goals, ideates 3 distinct creative concepts, evaluates them across a weighted 4-pillar rubric, autonomously selects the winning concept with comparative trade-off rationales, and generates a master campaign strategy, visual direction blueprint (hex palette, typography), and Instagram platform execution engine.
- **Person 3 (Production Agent)**: Receives Person 2's structured JSON Campaign Blueprint (`CreativeDirectorHandoff` v2.0.0) and renders final advertising assets and copy.

---

## Quickstart in VS Code

### 1. Run Interactive Creative Director CLI
```powershell
.\venv\Scripts\Activate.ps1
python run_creative_director.py
```

### 2. Run All 3 Test Brands (Glowify, EcoGlow, Horizon AI)
```powershell
python run_all_brands.py
```

### 3. Run FastAPI Server & Interactive Swagger UI
```powershell
uvicorn app.main:app --reload
```
Visit `http://127.0.0.1:8000/docs` to test:
- `POST /api/v1/brand/analyze` — Person 1 Report
- `POST /api/v1/campaign/generate` — Person 2 Campaign Blueprint
- `POST /api/v1/campaign/generate-from-report` — Person 1 to Person 2 Automated Handoff
- `GET /api/v1/campaign/outputs` — List generated blueprints

### 4. Run Pytest Test Suite
```powershell
pytest -v tests
```

---

## Outputs Generated in `outputs/`
- `glowify_campaign_blueprint.json` & `glowify_creative_brief.md`
- `ecoglow_campaign_blueprint.json` & `ecoglow_creative_brief.md`
- `horizon_ai_campaign_blueprint.json` & `horizon_ai_creative_brief.md`
