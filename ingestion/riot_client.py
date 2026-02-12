import os
import requests
from dotenv import load_dotenv

# =========================
# Load environment variables
# =========================
load_dotenv()

RIOT_API_KEY = os.getenv("RIOT_API_KEY")
print("DEBUG RIOT_API_KEY:", RIOT_API_KEY[:10])


RIOT_PLATFORM_ROUTING = os.getenv("RIOT_PLATFORM_ROUTING")  # la1
RIOT_REGIONAL_ROUTING = os.getenv("RIOT_REGIONAL_ROUTING")  # americas


# =========================
# Base Riot Request
# =========================
def riot_get(url: str):
    """
    Makes a GET request to Riot API with the API key.
    """
    headers = {"X-Riot-Token": RIOT_API_KEY}

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(
            f"Riot API Error {response.status_code}: {response.text}"
        )

    return response.json()


# =========================
# Get PUUID from Summoner Name
# =========================
def get_puuid(game_name: str, tag_line: str):

    url = (
        f"https://americas.api.riotgames.com/"
        f"riot/account/v1/accounts/by-riot-id/"
        f"{game_name}/{tag_line}"
    )

    data = riot_get(url)
    return data["puuid"]



# =========================
# Get Match IDs
# =========================
def get_match_ids(puuid: str, count: int = 5):
    """
    Returns a list of recent match IDs from a player PUUID.
    """

    url = (
        f"https://{RIOT_REGIONAL_ROUTING}.api.riotgames.com"
        f"/lol/match/v5/matches/by-puuid/{puuid}/ids?count={count}"
    )

    return riot_get(url)


# =========================
# Get Match Details
# =========================
def get_match(match_id: str):
    """
    Returns full match JSON data from a match ID.
    """

    url = (
        f"https://{RIOT_REGIONAL_ROUTING}.api.riotgames.com"
        f"/lol/match/v5/matches/{match_id}"
    )

    return riot_get(url)
