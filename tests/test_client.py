import os
import pytest
from dotenv import load_dotenv
import httpx
from frisquet_api.client import FrisquetClient

# Load environment variables from .env file
load_dotenv()


@pytest.fixture
def client() -> FrisquetClient:
    email = os.getenv("FRISQUET_EMAIL")
    password = os.getenv("FRISQUET_PASSWORD")

    if not email or not password:
        pytest.skip(
            "FRISQUET_EMAIL and FRISQUET_PASSWORD environment variables are required"
        )

    return FrisquetClient(email=email, password=password)


async def test_get_token_fake_credentials(client: FrisquetClient):
    client = FrisquetClient(email="test@test.com", password="test")
    with pytest.raises(httpx.HTTPStatusError):
        await client.get_authentication()


async def test_get_token_valid_credentials(client: FrisquetClient):
    token = await client.token
    assert token is not None


async def test_get_site_data(client: FrisquetClient):
    site_data = await client.get_site_data("23425231180423")
    assert site_data is not None
