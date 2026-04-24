from fastapi import FastAPI
import httpx
from datetime import date, timedelta
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BRAVES_TEAM_ID = 144
MLB_API_BASE = "https://statsapi.mlb.com/api/v1"

async def get_todays_game():
    today = date.today().isoformat()
    url = f"{MLB_API_BASE}/schedule?teamId={BRAVES_TEAM_ID}&date={today}&sportId=1"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()

    if data["totalGames"] == 0:
        return None
    
    return data["dates"][0]["games"][0]

async def get_last10_games():
    today_as_day = date.today().day
    last10_list = []
    for i in range(1,11):
        formatted_date = date.today() - timedelta(days=i)
        url = f"{MLB_API_BASE}/schedule?teamId={BRAVES_TEAM_ID}&date={formatted_date}&sportId=1"

        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()
        
        if data["totalGames"] == 0:
            last10_list.append("IDLE")
        else:
            last10_list.append(data["dates"][0]["games"][0])
    return last10_list

# return the next game whose status is Preview.
async def get_next_game():
    today_as_day = date.today().day
    i = 0
    while i <= 7:
        formatted_date = date.today() + timedelta(days=i)
        url = f"{MLB_API_BASE}/schedule?teamId={BRAVES_TEAM_ID}&date={formatted_date}&sportId=1"

        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()
        
        if data["totalGames"] == 0 and i == 7:
            return "No games in 7 days"
        if data["totalGames"] == 0:
            i+=1
            continue
        if data["dates"][0]["games"][0]["status"]["abstractGameState"] == "Preview":
            return data["dates"][0]["games"][0]
        i+=1
    return None


def parse_game(game):
    status = game["status"]["abstractGameState"] # "Preview", "Live", "Final"
    home = game["teams"]["home"]
    away = game["teams"]["away"]

    braves_are_home = home["team"]["id"] == BRAVES_TEAM_ID

    braves = home if braves_are_home else away
    opponent = away if braves_are_home else home

    braves_score = braves.get("score", 0)
    opponent_score = opponent.get("score",0)
    opponent_name = opponent["team"]["name"]

    return {
        "status": status,
        "braves_score": braves_score,
        "opponent_score": opponent_score,
        "opponent": opponent_name,
        "braves_are_home": braves_are_home,
    }


@app.get("/")
def root():
    return {"message": "Braves API is running! Success!"}


@app.get("/today")
async def today():
    game = await get_todays_game()

    if game is None:
        return {"display": "No Braves game today.", "result": "no_game"}
    
    parsed = parse_game(game)

    if parsed["status"] != "Final":
        return {
            "display": f"Game not final yet. Status: {parsed['status']}",
            "result": "in_progress",
            "opponent": parsed["opponent"],
        }
    
    braves_won = parsed["braves_score"] > parsed["opponent_score"]
    result = "win" if braves_won else "loss"
    display = (
        f"Braves win! {parsed['braves_score']}-{parsed['opponent_score']} over the {parsed['opponent']}."
        if braves_won
        else f"Braves lost. {parsed['braves_score']}-{parsed['opponent_score']} to the {parsed['opponent']}."
    )

    return {
        "result": result,
        "display": display,
        "braves_score": parsed["braves_score"],
        "opponent_score": parsed["opponent_score"],
        "opponent": parsed["opponent"],
    }


@app.get("/last10")
async def last10():
    game_list = await get_last10_games()

    cleaned_last10_list = []
    for i in range(10):
        if game_list[i] == "IDLE":
            cleaned_last10_list.append({"display": "No Braves game today.", "result": "no_game"})
        else:
            parsed = parse_game(game_list[i])
            
            braves_won = parsed["braves_score"] > parsed["opponent_score"]
            result = "win" if braves_won else "loss"
            display = (
                f"W - {parsed['braves_score']}-{parsed['opponent_score']} over the {parsed['opponent']}."
                if braves_won
                else f"L - {parsed['braves_score']}-{parsed['opponent_score']} to the {parsed['opponent']}."
            )

            cleaned_last10_list.append({
            "result": result,
            "display": display,
            "braves_score": parsed["braves_score"],
            "opponent_score": parsed["opponent_score"],
            "opponent": parsed["opponent"],
            })
    return cleaned_last10_list


@app.get("/next")
async def next():
    game = await get_next_game()

    if game is None:
        return {"display": "No Braves game in next 7 days", "result": "no_game"}
    
    parsed = parse_game(game)

    return {
        "opponent": f"Braves will face {parsed['opponent']} next.",
    }