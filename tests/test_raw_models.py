from pathlib import Path
import json
from frisquet_api.raw_models import SiteData


def test_site_data_from_json():
    with open(Path(__file__).parent / "assets" / "response_site_data.json", "r") as f:
        data = json.load(f)
        site_data = SiteData.model_validate(data)
        assert site_data is not None
