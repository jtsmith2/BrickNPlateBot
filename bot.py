"""
TwitchIO bot implementation for BrickNPlateBot using LangChain
"""

from twitchio.ext import commands

from config import (
    TWITCH_BOT_USERNAME, 
    TWITCH_OAUTH_TOKEN, 
    TWITCH_CHANNEL,
    add_subscriber,
    add_raider
)
from agents import process_chat_message, process_event

class BrickNPlateBot(commands.Bot):
    """Main Twitch bot class for BrickNPlateBot"""
    
    def __init__(self):
        """Initialize the bot with no command prefix"""
        super().__init__(
            token=TWITCH_OAUTH_TOKEN,
            prefix="",  # No command prefix, we'll use natural language
            initial_channels=[TWITCH_CHANNEL]
        )
        # Store channels for reference
        self._connected_channels = [TWITCH_CHANNEL]
    
    async def event_ready(self):
        """Called once when the bot goes online."""
        print(f"{TWITCH_BOT_USERNAME} is online!")
        print(f"Joined channels: {', '.join(self._connected_channels)}")
    
    async def event_message(self, message):
        """Called when a message is sent to the channel."""
        # Ignore messages from the bot itself
        if message.echo:
            return
        
        # Check if the message is addressed to the bot
        content = message.content.lower()
        if "bricknplatebot" in content:
            # Process the message with our agent
            response = await process_chat_message(message.author.name, message.content)
            
            # Truncate response to fit Twitch's character limit
            if len(response) > 500:
                response = response[:497] + "..."
                
            await message.channel.send(response)
    
    async def event_subscribe(self, event):
        """Called when a user subscribes to the channel."""
        # Add to recent events
        add_subscriber(event.user.name, event.sub_plan)
        
        # Generate and send message
        message = await process_event(
            event_type="subscription",
            username=event.user.name,
            details={"tier": event.sub_plan}
        )
        
        # Truncate message to fit Twitch's character limit
        if len(message) > 500:
            message = message[:497] + "..."
            
        await event.channel.send(message)
    
    async def event_resub(self, event):
        """Called when a user resubscribes to the channel."""
        # Add to recent events
        add_subscriber(
            event.user.name,
            event.sub_plan,
            event.cumulative_months,
            event.message.content if event.message else ""
        )
        
        # Generate and send message
        message = await process_event(
            event_type="resub",
            username=event.user.name,
            details={
                "months": event.cumulative_months,
                "tier": event.sub_plan,
                "message": event.message.content if event.message else ""
            }
        )
        
        # Truncate message to fit Twitch's character limit
        if len(message) > 500:
            message = message[:497] + "..."
            
        await event.channel.send(message)
    
    async def event_raid(self, event):
        """Called when the channel is raided."""
        # Add to recent events
        add_raider(event.raider.name, event.viewers)
        
        # Generate and send message
        message = await process_event(
            event_type="raid",
            username=event.raider.name,
            details={"viewers": event.viewers}
        )
        
        # Truncate message to fit Twitch's character limit
        if len(message) > 500:
            message = message[:497] + "..."
            
        await event.channel.send(message)

def main():
    """Start the Twitch bot"""
    bot = BrickNPlateBot()
    bot.run()

if __name__ == "__main__":
    main()
