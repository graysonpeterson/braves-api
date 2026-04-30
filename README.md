# Did the Braves Win Today? — API

A REST API built with FastAPI that pulls live game data from the MLB Stats API 
and returns Atlanta Braves game results in a clean, simple format.

## Live URL
https://did-the-braves-win-today-production.up.railway.app

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /today` | Returns today's game result — win, loss, in progress, or no game |
| `GET /last10` | Returns results from the last 10 games |
| `GET /next` | Returns the next scheduled game and opponent |

## Example Response

`GET /today`
```json
{
  "result": "win",
  "display": "Braves win! 7-3 over the New York Mets.",
  "braves_score": 7,
  "opponent_score": 3,
  "opponent": "New York Mets"
}
```

## Tech Stack
- Python
- FastAPI
- httpx
- Deployed on Railway

## Run Locally

```bash
git clone https://github.com/graysonpeterson/braves-api.git
cd braves-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

API will be running at `http://localhost:8000`

## Data Source
[MLB Stats API](https://statsapi.mlb.com) — unofficial, free, no key required.
