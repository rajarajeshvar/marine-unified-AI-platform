import asyncio
import websockets
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

AISSTREAM_API_KEY = "972ea8678eb2082db98b2fdbb4643c1cbe171ce7"
AISSTREAM_URL = "wss://stream.aisstream.io/v0/stream"

# In-memory cache for live ships
# Key: MMSI (str), Value: Dict with lat, lng, timestamp, name, etc.
live_ships_cache: Dict[str, Dict[str, Any]] = {}

async def ais_stream_client():
    subscription_message = {
        "APIKey": AISSTREAM_API_KEY,
        # Bounding box covering a broad region (e.g., North Atlantic)
        # format: [[min_lat, min_lon], [max_lat, max_lon]]
        "BoundingBoxes": [[[15, -80], [50, -10]]], 
        "FilterMessageTypes": ["PositionReport"]
    }
    
    while True:
        try:
            async with websockets.connect(AISSTREAM_URL) as websocket:
                await websocket.send(json.dumps(subscription_message))
                logger.info("Connected to AISStream and subscribed.")
                
                async for message_str in websocket:
                    try:
                        message = json.loads(message_str)
                        if message["MessageType"] == "PositionReport":
                            msg_data = message.get("Message", {}).get("PositionReport", {})
                            mmsi = str(message.get("MetaData", {}).get("MMSI"))
                            ship_name = message.get("MetaData", {}).get("ShipName", "Unknown")
                            lat = msg_data.get("Latitude")
                            lng = msg_data.get("Longitude")
                            speed = msg_data.get("Sog", 0)
                            
                            # Valid coordinates check
                            if lat is not None and lng is not None and lat != 91 and lng != 181:
                                live_ships_cache[mmsi] = {
                                    "mmsi": mmsi,
                                    "name": ship_name.strip(),
                                    "lat": lat,
                                    "lng": lng,
                                    "speed_knots": speed,
                                    "last_updated": message.get("MetaData", {}).get("time_utc")
                                }
                    except json.JSONDecodeError:
                        continue
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
        
        except Exception as e:
            logger.error(f"AISStream connection error: {e}. Reconnecting in 5 seconds...")
            await asyncio.sleep(5)
