"""
LangChain tools for BrickNPlateBot
"""

import yaml
import os
import requests
from typing import Dict, List, Optional, Union, Any

from langchain.tools import BaseTool, StructuredTool
from pydantic import BaseModel, Field

from config import (
    REBRICKABLE_API_KEY, 
    REBRICKABLE_BASE_URL,
    TWITCH_CLIENT_ID,
    TWITCH_CLIENT_SECRET,
    TWITCH_CHANNEL,
    STREAM_INFO_FILE
)

# Input/Output schemas for tools
class LegoSetInput(BaseModel):
    set_num: str = Field(description="The Lego set number (e.g., '42115-1' or '75192')")

class LegoSearchInput(BaseModel):
    query: str = Field(description="Search query for finding Lego sets")

class TwitchUserInput(BaseModel):
    username: str = Field(description="Twitch username to get information about")

class StreamInfoInput(BaseModel):
    category: Optional[str] = Field(
        None, 
        description="The category of information to retrieve (e.g., 'current_build', 'schedule', 'upcoming_builds', 'channel_info', 'faq'). If not specified, returns all information."
    )

# Tool functions
def get_lego_set_info(set_num: str) -> Dict:
    """Get detailed information about a specific Lego set."""
    try:
        headers = {
            "Authorization": f"key {REBRICKABLE_API_KEY}"
        }
        response = requests.get(f"{REBRICKABLE_BASE_URL}/lego/sets/{set_num}/", headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching Lego set {set_num}: {str(e)}")
        return {"error": f"Could not find information for set {set_num}"}

def search_lego_sets(query: str) -> List[Dict]:
    """Search for Lego sets by name or theme."""
    try:
        headers = {
            "Authorization": f"key {REBRICKABLE_API_KEY}"
        }
        params = {
            "search": query
        }
        response = requests.get(f"{REBRICKABLE_BASE_URL}/lego/sets/", headers=headers, params=params)
        response.raise_for_status()
        results = response.json().get("results", [])
        return results[:5]  # Return top 5 results
    except Exception as e:
        print(f"Error searching for Lego sets with query '{query}': {str(e)}")
        return {"error": f"Could not find any sets matching '{query}'"}

def get_twitch_user_info(username: str) -> Dict:
    """Get information about a Twitch user using Twitch API."""
    try:
        # Step 1: Get an app access token
        auth_url = "https://id.twitch.tv/oauth2/token"
        auth_params = {
            "client_id": TWITCH_CLIENT_ID,
            "client_secret": TWITCH_CLIENT_SECRET,
            "grant_type": "client_credentials"
        }
        auth_response = requests.post(auth_url, params=auth_params)
        auth_response.raise_for_status()
        access_token = auth_response.json()["access_token"]
        
        # Step 2: Get user ID from username
        headers = {
            "Client-ID": TWITCH_CLIENT_ID,
            "Authorization": f"Bearer {access_token}"
        }
        
        # Get user data
        users_url = "https://api.twitch.tv/helix/users"
        users_params = {"login": username.lower()}
        users_response = requests.get(users_url, headers=headers, params=users_params)
        users_response.raise_for_status()
        
        user_data = users_response.json()
        if not user_data["data"]:
            return {"error": f"User '{username}' not found on Twitch"}
        
        user_id = user_data["data"][0]["id"]
        user_info = user_data["data"][0]
        
        # Step 3: Get channel information
        channel_url = f"https://api.twitch.tv/helix/channels?broadcaster_id={user_id}"
        channel_response = requests.get(channel_url, headers=headers)
        channel_response.raise_for_status()
        channel_data = channel_response.json()["data"][0] if channel_response.json()["data"] else {}
        
        # Step 4: Check if user follows this channel
        channel_name = TWITCH_CHANNEL.lower().lstrip('#')
        broadcaster_id = None
        
        # Get broadcaster ID
        broadcaster_params = {"login": channel_name}
        broadcaster_response = requests.get(users_url, headers=headers, params=broadcaster_params)
        broadcaster_response.raise_for_status()
        broadcaster_data = broadcaster_response.json()
        
        if broadcaster_data["data"]:
            broadcaster_id = broadcaster_data["data"][0]["id"]
            
            # Check follow status
            follows_url = "https://api.twitch.tv/helix/channels/followers"
            follows_params = {
                "broadcaster_id": broadcaster_id,
                "user_id": user_id
            }
            follows_response = requests.get(follows_url, headers=headers, params=follows_params)
            follows_response.raise_for_status()
            
            follow_data = follows_response.json()
            following_since = None
            
            if "data" in follow_data and follow_data["data"]:
                following_since = follow_data["data"][0]["followed_at"]
        
        # Compile user information
        result = {
            "username": user_info["display_name"],
            "id": user_id,
            "profile_image": user_info["profile_image_url"],
            "account_created": user_info["created_at"],
            "description": user_info["description"],
            "broadcaster_type": user_info["broadcaster_type"],
            "channel": channel_data,
            "following_since": following_since if 'following_since' in locals() else None,
            "is_following": 'following_since' in locals() and following_since is not None
        }
        
        return result
        
    except Exception as e:
        print(f"Error fetching Twitch user info for {username}: {str(e)}")
        return {"error": f"Could not fetch information for user {username}: {str(e)}"}

def get_stream_info(category: Optional[str] = None) -> Dict:
    """Get information about the stream based on the specified category."""
    try:
        # Load the stream info file
        if os.path.exists(STREAM_INFO_FILE):
            with open(STREAM_INFO_FILE, 'r', encoding='utf-8') as file:
                stream_info = yaml.safe_load(file)
        else:
            # Create a default stream info file if it doesn't exist
            stream_info = create_default_stream_info()
            
            with open(STREAM_INFO_FILE, 'w', encoding='utf-8') as file:
                yaml.dump(stream_info, file, default_flow_style=False)
            
            print(f"Created default stream info file at {STREAM_INFO_FILE}")
        
        if not category:
            # Return everything if no category specified
            return stream_info
        
        if category in stream_info:
            return {category: stream_info[category]}
        else:
            return {"error": f"No information found for category '{category}'"}
    except Exception as e:
        print(f"Error getting stream info for category '{category}': {str(e)}")
        return {"error": f"Could not retrieve stream information: {str(e)}"}

def create_default_stream_info() -> Dict:
    """Create default stream information."""
    return {
        "current_build": {
            "set_number": "42115-1",
            "name": "Lamborghini Sián FKP 37",
            "progress": "50% complete",
            "started_on": "2025-04-01"
        },
        "schedule": {
            "monday": "No stream",
            "tuesday": "7pm-10pm EST",
            "wednesday": "No stream",
            "thursday": "7pm-10pm EST",
            "friday": "8pm-12am EST",
            "saturday": "3pm-7pm EST",
            "sunday": "No stream"
        },
        "upcoming_builds": [
            {"set_number": "75192-1", "name": "Millennium Falcon", "planned_start": "April 15, 2025"},
            {"set_number": "10294-1", "name": "Titanic", "planned_start": "May 1, 2025"}
        ],
        "channel_info": {
            "description": "Building Lego sets brick by brick! Join us for relaxing brick building sessions.",
            "rules": [
                "Be kind and respectful",
                "No spoilers about build techniques unless asked",
                "Have fun and share your love for Lego"
            ]
        },
        "faq": [
            {"question": "What camera do you use?", 
             "answer": "I use a Sony a6400 for the main shot and a Sony a7III for closeups."},
            {"question": "Do you take build requests?", 
             "answer": "Yes! Subscribers can suggest builds for our community poll."},
            {"question": "How long have you been streaming?", 
             "answer": "I started streaming Lego builds in January 2024."}
        ]
    }

# Create LangChain tools
def get_bot_tools():
    """Get all tools for the bot."""
    tools = [
        StructuredTool.from_function(
            func=get_lego_set_info,
            name="get_lego_set_info",
            description="Get detailed information about a specific Lego set by set number",
            args_schema=LegoSetInput,
            return_direct=False
        ),
        StructuredTool.from_function(
            func=search_lego_sets,
            name="search_lego_sets",
            description="Search for Lego sets by name or theme",
            args_schema=LegoSearchInput,
            return_direct=False
        ),
        StructuredTool.from_function(
            func=get_twitch_user_info,
            name="get_twitch_user_info",
            description="Get information about a Twitch user in the context of this channel",
            args_schema=TwitchUserInput,
            return_direct=False
        ),
        StructuredTool.from_function(
            func=get_stream_info,
            name="get_stream_info",
            description="Get information about the stream like schedule, current build, etc.",
            args_schema=StreamInfoInput,
            return_direct=False
        )
    ]
    
    return tools
