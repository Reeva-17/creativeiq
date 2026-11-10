# CreativeIQ — Brand Intelligence Agent (Person 1)

Standalone FastAPI service for evidence-labelled Brand DNA, transparent competitor research, SWOT, and a versioned handoff report. It deliberately does **not** create campaigns, ads, captions, or creative assets.

## Architecture

Routes validate requests and return only schema contracts. Services own Brand DNA, competitor, SWOT, and report composition. `ai/` contains an interchangeable `LLMProvider`; `GroqProvider` uses Groq's official asynchronous SDK, JSON mode, timeout and retry handling. Missing/failed AI calls do not block the API: the report contains only sourceable user data plus an explicit limitation. This prevents fake analysis.

## Setup and run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`. Set `GROQ_API_KEY` in `.env` to enable enrichment. Optional: `GROQ_MODEL` (default: `llama-3.3-70b-versatile`), `GROQ_TIMEOUT_SECONDS`, `GROQ_MAX_RETRIES`. Add `TAVILY_API_KEY` to enable optional public-web competitor leads through Tavily; without it, competitor claims remain explicitly unavailable.

## API

- `GET /health`
- `POST /api/v1/brand/analyze` — complete stable report
- `POST /api/v1/brand/analyze-dna` — DNA and visual direction only
- `POST /api/v1/brand/competitors` — supplied competitors, clearly source-limited

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/v1/brand/analyze -ContentType application/json -InFile examples/sample_brand_input.json
pytest -q
```

## Person 2 integration

Call `/api/v1/brand/analyze`, persist the JSON unchanged, and branch on each `Finding.evidence_type`. Check `schema_version` starts with `1.`. Read `docs/integration_contract.md` and never turn an `unavailable` item into a claim. `examples/` uses fictional Glowify data only.
