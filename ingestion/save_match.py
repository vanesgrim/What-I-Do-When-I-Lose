import os
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from riot_client import get_puuid, get_match_ids, get_match


# =========================
# Load environment variables
# =========================
load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")


# =========================
# PostgreSQL Connection
# =========================
engine = create_engine(
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)


# =========================
# Save Match into Database
# =========================
def save_match(match_data: dict):

    match_id = match_data["metadata"]["matchId"]
    info = match_data["info"]

    duration = info["gameDuration"]
    mode = info["gameMode"]

    start_time = datetime.fromtimestamp(info["gameStartTimestamp"] / 1000)

    query = text("""
        INSERT INTO matches (match_id, game_duration, game_mode, game_start)
        VALUES (:match_id, :duration, :mode, :start_time)
        ON CONFLICT (match_id) DO NOTHING;
    """)

    with engine.connect() as conn:
        conn.execute(query, {
            "match_id": match_id,
            "duration": duration,
            "mode": mode,
            "start_time": start_time
        })
        conn.commit()

    print("Match saved successfully:", match_id)


# =========================
# Ingestion Pipeline
# =========================
def ingest_player_matches(game_name: str, tag_line: str, count: int = 5):

    print(f"\nSearching player: {game_name}#{tag_line}")

    # Step 1: Riot ID → PUUID
    puuid = get_puuid(game_name, tag_line)
    print("PUUID found")

    # Step 2: PUUID → Match IDs
    match_ids = get_match_ids(puuid, count=count)
    print(f"Found {len(match_ids)} matches")

    # Step 3: Match IDs → Download + Save
    for match_id in match_ids:
        print(f"➡ Downloading match: {match_id}")

        match_data = get_match(match_id)
        save_match(match_data)

    print("\nIngestion completed successfully!\n")


# =========================
# Run Script
# =========================
if __name__ == "__main__":

    riot_id = input("Enter Riot ID (name#tag): ")

    game_name, tag_line = riot_id.split("#")

    ingest_player_matches(game_name, tag_line, count=5)
