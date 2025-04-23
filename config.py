"""
Configuration and environment variables for BrickNPlateBot
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

# OpenAI API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# LangChain Model Configuration
llm = ChatOpenAI(
    model="gpt-4-turbo-preview",
    temperature=0.7,
    api_key=OPENAI_API_KEY
)

# Rebrickable API Configuration
REBRICKABLE_API_KEY = os.getenv("REBRICKABLE_API_KEY")
REBRICKABLE_BASE_URL = "https://rebrickable.com/api/v3"

# Twitch Configuration
TWITCH_BOT_USERNAME = os.getenv("TWITCH_BOT_USERNAME")
TWITCH_OAUTH_TOKEN = os.getenv("TWITCH_OAUTH_TOKEN")
TWITCH_CHANNEL = os.getenv("TWITCH_CHANNEL")
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")

# Stream Information Configuration
STREAM_INFO_FILE = os.getenv("STREAM_INFO_FILE", "stream_info.yaml")

# Track recent subscribers and raiders for context
recent_events = {
    "subscribers": [],
    "raiders": []
}

# Add a subscriber to recent events
def add_subscriber(username, tier=None, months=None, message=None):
    recent_events["subscribers"].append({
        "username": username,
        "tier": tier,
        "months": months,
        "message": message,
        "timestamp": datetime.now()
    })
    
    # Trim the list to keep only recent events
    if len(recent_events["subscribers"]) > 10:
        recent_events["subscribers"].pop(0)

# Add a raider to recent events
def add_raider(username, viewers=0):
    recent_events["raiders"].append({
        "username": username,
        "viewers": viewers,
        "timestamp": datetime.now()
    })
    
    # Trim the list to keep only recent events
    if len(recent_events["raiders"]) > 10:
        recent_events["raiders"].pop(0)
