import pytest
from pydantic import ValidationError
from app.schemas.brand_input import BrandInput
from app.schemas.brand_report import BrandIntelligenceReport


def test_minimal_brand_input_is_valid():
    assert BrandInput(brand_name="Glowify", industry="Skincare").brand_name == "Glowify"


def test_blank_name_is_invalid():
    with pytest.raises(ValidationError): BrandInput(brand_name="", industry="Skincare")


def test_report_contract_validates():
    report = BrandIntelligenceReport(brand_name="Glowify", industry="Skincare", brand_dna={}, competitor_analysis={}, swot_analysis={}, visual_identity={})
    assert report.schema_version == "1.0.0"
