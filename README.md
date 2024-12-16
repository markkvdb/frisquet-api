# Frisquet API

Python client for the Frisquet API that features:

- Complete control of your Frisquet Connect boiler
- Async/await support for modern Python applications
- Type hints for better IDE integration
- Comprehensive error handling

## Usage

```python
from frisquet_api.client import FrisquetClient, Zone, Mode, ModeChange

client = FrisquetClient(email="your@email.com", password="your-password")
```

### Get site data

```python
site_data = await client.get_site_data("your-site-id")
```

### Set mode

```python
await client.set_mode("your-site-id", Zone.ZONE_1, Mode.COMFORT, ModeChange.PERMANENT)
```

### Set temperature

```python
await client.set_temperature("your-site-id", Zone.ZONE_1, HeatingMode.FROST_PROTECTION, 8.0)
```

### Set water mode

```python
await client.set_water_mode("your-site-id", WaterMode.ECO_TIMER)
```

## Development

Install [uv](https://astral.sh/uv/) and setup your python environment with the following commands:

```bash
uv sync
```

Setup the pre-commit hooks:

```bash
uvx pre-commit install
```

Run the tests:

```bash
uv run pytest .
```

## Inspiration

This project is inspired by the [Frisquet-connect-for-home-assistant](https://github.com/TheGui01/Frisquet-connect-for-home-assistant) project.
