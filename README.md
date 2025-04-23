# BrickNPlateBot

A Twitch chat bot for Lego streamers, built using LangChain and TwitchIO.

## Features

- Responds to chat messages that mention "bricknplatebot"
- Provides information about Lego sets from Rebrickable
- Looks up Twitch user information
- Shares stream details like schedule and current build
- Sends custom thank-you messages for subscriptions and raids

## Project Structure

The project consists of four main files:

- **bot.py** - TwitchIO bot implementation
- **config.py** - Configuration and environment variables
- **tools.py** - LangChain tools for Lego, Twitch, and stream information
- **agents.py** - LangChain agents for handling chat and events

## LangChain Components Used

This implementation uses several LangChain components:

- **StructuredTool** - For defining tools with Pydantic schemas
- **AgentExecutor** - For executing the agent with tools
- **create_openai_functions_agent** - For creating an agent with OpenAI function calling
- **ConversationBufferMemory** - For storing conversation history
- **ChatPromptTemplate** - For creating prompts with system messages

## Installation

1. Clone the repository
2. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your API keys and configuration:
   ```
   OPENAI_API_KEY=your_openai_api_key
   REBRICKABLE_API_KEY=your_rebrickable_api_key
   TWITCH_BOT_USERNAME=bricknplatebot
   TWITCH_OAUTH_TOKEN=oauth:your_twitch_oauth_token
   TWITCH_CHANNEL=your_channel_name
   TWITCH_CLIENT_ID=your_twitch_client_id
   TWITCH_CLIENT_SECRET=your_twitch_client_secret
   STREAM_INFO_FILE=stream_info.yaml
   ```

## Usage

1. Run the bot:
   ```bash
   python bot.py
   ```

2. The bot will connect to Twitch and respond to messages mentioning "bricknplatebot"

3. Customize your stream information by editing `stream_info.yaml`

## Stream Information

The bot reads from a YAML file to get information about your stream. The structure of this file is:

```yaml
current_build:
  set_number: "42115-1"
  name: "Lamborghini Sián FKP 37"
  progress: "50% complete"
  started_on: "2025-04-01"

schedule:
  monday: "No stream"
  tuesday: "7pm-10pm EST"
  # ...

upcoming_builds:
  - set_number: "75192-1"
    name: "Millennium Falcon"
    planned_start: "April 15, 2025"
  # ...

channel_info:
  description: "Building Lego sets brick by brick!"
  rules:
    - "Be kind and respectful"
    # ...

faq:
  - question: "What camera do you use?"
    answer: "I use a Sony a6400..."
  # ...
```

## Extending the Bot

To add new functionality:

1. Add a new tool function in `tools.py`
2. Add the tool to the `get_bot_tools()` function
3. Update the system message in `agents.py` if needed
