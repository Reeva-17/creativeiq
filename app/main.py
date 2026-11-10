from fastapi import FastAPI
from app.api.routes import brand, competitors

app = FastAPI(title="CreativeIQ Brand Intelligence Agent", version="1.0.0", description="Person 1: evidence-labelled brand intelligence; no advertising or campaign generation.")
app.include_router(brand.router)
app.include_router(competitors.router)


@app.get("/health", tags=["System"])
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "creativeiq-brand-intelligence", "schema_version": "1.0.0"}
