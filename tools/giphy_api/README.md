# Giphy CLI Wrapper

Thin Python CLI wrapper around the official [`giphy-python-client`](https://github.com/Giphy/giphy-python-client).

The main workflow is searching GIFs by query, with a few extra convenience commands included.

## Requirements

- Python 3.10+
- A Giphy API key

## Installation

Create and activate a virtual environment if you want:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the project in editable mode:

```bash
pip install -e .
```

## Configuration

Create a `.env` file in the project root:

```bash
GIPHY_API_KEY=your_api_key_here
```

A ready-to-copy example is available in `.env.example`.

## Commands

### Search by query

```bash
giphy search "cats" --limit 5
```

JSON output:

```bash
giphy search "cats" --limit 5 --json
```

Example payload:

```json
[
  {
    "id": "wLjduF4f4bHOxxMM6X",
    "title": "",
    "gif_url": "https://i.giphy.com/wLjduF4f4bHOxxMM6X.gif",
    "webp_url": "https://i.giphy.com/wLjduF4f4bHOxxMM6X.webp",
    "username": "Lunchtre",
    "rating": "g",
    "source": ""
  }
]
```

### Trending

```bash
giphy trending --limit 5
```

### Translate

```bash
giphy translate "mind blown"
```

### Random

```bash
giphy random --tag "excited"
```

## Run without installing the script entry point

You can also run the module directly:

```bash
python -m giphy_cli.cli search "cats" --limit 5
```

## Common flags

- `--limit` number of results
- `--offset` pagination offset
- `--rating` content rating filter
- `--lang` language hint for `search`
- `--json` machine-friendly output

## Behavior

- Loads environment variables from `.env`
- Fails fast if `GIPHY_API_KEY` is missing
- Uses the official Python client under a thin wrapper
- Prints useful fields by default: `id`, `title`, `gif_url`, `webp_url`, `username`, `rating`, `source`
- `gif_url` and `webp_url` are emitted as direct asset URLs like `https://i.giphy.com/<id>.gif` and `https://i.giphy.com/<id>.webp`

## Development smoke checks

Show help:

```bash
python -m giphy_cli.cli --help
```

Check missing config handling:

```bash
python -m giphy_cli.cli search "cats"
```
