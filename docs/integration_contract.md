# Brand Intelligence Contract v1.0.0

Person 2 consumes the JSON returned by `POST /api/v1/brand/analyze`; no Python import is required. `schema_version` is mandatory and semantic-versioned. Additive fields may arrive in a minor version; breaking changes require a new major version.

Every analytical claim is a `Finding`: `statement`, `evidence_type`, optional `rationale`, and `source_urls`. Evidence types are `verified_information`, `user_provided_information`, `ai_generated_interpretation`, `recommendation`, and `unavailable`. Consumers must not treat non-verified entries as facts.

Top-level fields: `brand_name`, `industry`, `brand_overview`, `brand_dna`, `competitor_analysis`, `swot_analysis`, `visual_identity`, `strategic_recommendations`, `sources`, and `assumptions`. Empty arrays mean evidence was unavailable, not a negative conclusion. `assumptions` and `competitor_analysis.limitations` must be surfaced to a human reviewer.

For the full machine-readable contract use the endpoint OpenAPI schema (`/openapi.json`, component `BrandIntelligenceReport`). A sample payload is in `examples/sample_brand_output.json`; its statements are fictional.
