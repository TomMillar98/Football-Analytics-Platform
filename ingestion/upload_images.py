import os
import requests
from azure.storage.blob import BlobServiceClient
from sqlalchemy import text
from ingestion.utils import engine

def download_bytes(url):
    """Download image bytes from URL."""
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.content
    except Exception:
        return None
    return None


def upload_blob(blob_client, container, blob_name, data):
    """Upload byte data to blob storage."""
    container_client = blob_client.get_container_client(container)
    blob = container_client.get_blob_client(blob_name)
    blob.upload_blob(data, overwrite=True)
    return blob.url


def run():
    print("Starting image upload pipeline...")

    blob_conn = os.getenv("AZURE_BLOB_CXN")
    if not blob_conn:
        raise RuntimeError("AZURE_BLOB_CXN missing from environment variables")

    blob_client = BlobServiceClient.from_connection_string(blob_conn)

    with engine().begin() as conn:

        # Teams
        print("Uploading team logos...")

        teams = conn.execute(text("""
            SELECT team_id, logo_url
            FROM dbo.dim_team
            WHERE logo_url IS NOT NULL
        """)).fetchall()

        for team_id, url in teams:
            data = download_bytes(url)
            if data:
                blob_url = upload_blob(
                    blob_client,
                    "team-logos",
                    f"{team_id}.png",
                    data
                )
                conn.execute(text("""
                    UPDATE dbo.dim_team
                    SET logo_url = :url
                    WHERE team_id = :id
                """), {"url": blob_url, "id": team_id})

        # Players
        print("Uploading player images...")

        players = conn.execute(text("""
            SELECT player_id, photo_url
            FROM dbo.dim_player
            WHERE photo_url IS NOT NULL
        """)).fetchall()

        for player_id, url in players:
            data = download_bytes(url)
            if data:
                blob_url = upload_blob(
                    blob_client,
                    "player-photos",
                    f"{player_id}.png",
                    data
                )
                conn.execute(text("""
                    UPDATE dbo.dim_player
                    SET photo_url = :url
                    WHERE player_id = :id
                """), {"url": blob_url, "id": player_id})

        # Leagues
        print("Uploading league images...")

        leagues = conn.execute(text("""
            SELECT comp_id, logo_url
            FROM dbo.dim_competition
            WHERE logo_url IS NOT NULL
        """)).fetchall()

        for comp_id, url in leagues:
            data = download_bytes(url)
            if data:
                blob_url = upload_blob(
                    blob_client,
                    "league-logos",
                    f"{comp_id}.png",
                    data
                )
                conn.execute(text("""
                    UPDATE dbo.dim_competition
                    SET logo_url = :url
                    WHERE comp_id = :id
                """), {"url": blob_url, "id": comp_id})

    print("Image upload pipeline completed!")