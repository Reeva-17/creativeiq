# CreativeIQ

CreativeIQ is a FastAPI-based, four-agent marketing campaign system. It runs in one backend process; LangGraph is embedded in that process. This checkout has **no browser frontend and no database**. Generated Person 2 briefs are saved to `outputs/`; generated Person 3 images/posters are saved to `creative_generation/generated/`.

## Agent workflow

`POST /api/v1/workflow/run` is the integrated path:

1. Person 1 creates a versioned Brand Intelligence Report.
2. Person 2 converts that exact report into campaign strategy and a creative brief through its LangGraph graph.
3. Person 3 uses the brief and strategy context to generate real Gemini marketing copy; Cloudflare image generation is optional.
4. Person 4 evaluates the creative, returning AI evaluation when Gemini is available or the existing local rule-based evaluation if it is not.
5. If revision is required, Person 3 receives the actual Person 4 instructions, produces one revised asset, and Person 4 evaluates it again. The loop is capped at one revision.

No substitute campaign copy is generated if Person 3's Gemini key is missing.

## Windows / VS Code setup

Open this exact folder in VS Code:

```powershell
cd C:\Users\psing\Downloads\creativeiq\creativeiq
code .
```

Use Python 3.11 or later (tested here with Python 3.14). Create the virtual environment only if `.venv` does not already exist:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Set these values in `.env`; never commit it:

```env
GROQ_API_KEY=your_groq_key
GEMINI_API_KEY=your_gemini_key
GEMINI_MODEL=gemini-3.8-flash
# Optional: public competitor research
TAVILY_API_KEY=your_tavily_key
# Optional: images when generate_image is true
CLOUDFLARE_ACCOUNT_ID=your_account_id
CLOUDFLARE_API_TOKEN=your_workers_ai_token
CLOUDFLARE_IMAGE_MODEL=@cf/black-forest-labs/flux-1-schnell
```

Start the API in one VS Code terminal:

```powershell
cd C:\Users\psing\Downloads\creativeiq\creativeiq
.\.venv\Scripts\Activate.ps1
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000 for the built-in one-prompt browser interface, http://127.0.0.1:8000/docs for Swagger, and http://127.0.0.1:8000/health for the health check. No additional agent process, LangGraph service, database, or frontend process is needed.

## Test commands

The standard suite is offline/deterministic and excludes tests that call paid external LLM APIs:

```powershell
python -m pytest -q
```

Run only the four-agent contract tests:

```powershell
python -m pytest tests\test_four_agent_workflow.py -q
```

Run live-provider tests only after configuring valid keys and confirming your network permits Gemini/Groq access:

```powershell
python -m pytest -m integration -q
```

The integration marker is intentional: those tests make real paid/networked provider requests and should not make an otherwise offline test suite flaky.

## Manual complete-workflow test

For the normal user journey, open http://127.0.0.1:8000, enter one brand/campaign prompt, leave **Generate an image and final poster** selected, and click **Generate complete campaign**. The page calls `POST /api/v1/workflow/run-from-prompt`, displays every agent's completed status, and renders returned images/posters directly from `/generated/...`.

The browser experience requires working Groq/Gemini credentials to extract the brand brief and Cloudflare Workers AI credentials for the required visual and poster. If either provider fails, the page displays the API error instead of treating a partial campaign as successful.

### Swagger alternative

In Swagger, open `POST /api/v1/workflow/run`, click **Try it out**, and use:

```json
{
  "brand": {
    "brand_name": "Glowify",
    "industry": "Clean skincare",
    "business_description": "Barrier-repair skincare for people overwhelmed by harsh routines.",
    "products_services": ["Ceramide repair serum"],
    "target_audience": "Urban adults aged 20-32 with sensitive skin",
    "brand_values": ["Transparency", "Skin kindness"]
  },
  "competitor_names": ["The Ordinary", "CeraVe"],
  "product_name": "Barrier Balance Serum",
  "product_description": "A gentle ceramide serum for restoring the skin barrier.",
  "campaign_objective": "Build awareness and drive product discovery.",
  "max_revisions": 1,
  "generate_image": true,
  "generate_poster": true
}
```

A successful response contains `brand_intelligence`, `campaign_handoff`, `creative_assets`, `evaluations`, and—only when a revision was necessary—`revision_feedback` plus a second creative/evaluation. Set `generate_image: true` to return an `image_url`; set `generate_poster: true` to return both an `image_url` and a composed `poster_url`. Both require working Cloudflare Workers AI credentials.

## Troubleshooting

- **`Activate.ps1` is not found:** you are one folder too high. Run `cd C:\Users\psing\Downloads\creativeiq\creativeiq` first.
- **`file or directory not found`:** use `tests\test_four_agent_workflow.py`, without a backslash before `.py`.
- **503 from workflow:** configure the required Gemini key; Person 3 cannot generate copy without it.
- **502 from workflow:** inspect the server log; normally this indicates a rejected/failed Groq, Gemini, Tavily, or Cloudflare request.
- **Port 8000 is occupied:** use `--port 8001` and open that port in Swagger.
- **Images fail:** leave `generate_image` false until both Cloudflare variables are correct.
- **Cloudflare image request returns 400:** restart Uvicorn after this update, then retry. CreativeIQ now sends FLUX a compact visual prompt (the full campaign brief is too long for FLUX.1 Schnell). If it still fails, the returned Person 3 message includes Cloudflare's exact reason. Create a Cloudflare **Workers AI** API token for the same account ID with Workers AI Read/Edit permissions and confirm Workers AI access/credits. The model ID above is the supported FLUX.1 Schnell REST model; do not use an AI Gateway-only token.
