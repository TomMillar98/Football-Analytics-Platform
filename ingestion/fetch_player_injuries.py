import logging
from datetime import datetime, UTC

logger = logging.getLogger(__name__)

def safe_get(d, *keys):
    """Safely get nested dictionary values"""
    for key in keys:
        if not isinstance(d, dict):
            return None
        d = d.get(key)
    return d


def run(api_response):
    records = []

    for i, item in enumerate(api_response):

        try:
            player = item.get("player", {})

            record = {
                "player_id": safe_get(player, "id"),
                "name": safe_get(player, "name"),
                "injury_date": safe_get(player, "injury", "date"),
                "injury_type": safe_get(player, "injury", "type"),
                "injury_reason": safe_get(player, "injury", "reason"),
                "last_updated": datetime.now(UTC)
            }

            records.append(record)

        except Exception as e:
            logger.error(f"Error processing record {i}: {e}", exc_info=True)
            continue  # 🔥 NEVER crash, just skip bad row

    return records