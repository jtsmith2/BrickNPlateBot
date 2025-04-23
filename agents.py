"""
LangChain agents for BrickNPlateBot
"""

from typing import List, Dict, Any
import json

from langchain.agents import create_openai_functions_agent
from langchain.agents import AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from config import llm
from tools import get_bot_tools

def create_chat_agent():
    """Create an agent for handling chat messages"""
    
    # Define tools
    tools = get_bot_tools()
    
    # Define system message
    system_message = """You are BrickNPlateBot, a helpful assistant for a Twitch channel focused on building Lego sets.
    You have knowledge about Lego sets and can retrieve more detailed information using tools.
    
    IMPORTANT: Your responses MUST be brief and concise, less than 400 characters. Twitch has a 500 character limit.
    Be friendly, concise, and enthusiastic about Lego. The channel is currently building Lego sets live on stream.
    
    When users ask about Lego sets:
    - If they mention a specific set number (like '75192' or '42115-1'), use get_lego_set_info to look it up
    - If they ask about sets with a theme or name (like 'Star Wars sets' or 'Millennium Falcon'), use search_lego_sets
    - If they ask about another user's activity or preferences, use get_twitch_user_info
    - If they ask about the stream schedule, current build, etc., use get_stream_info
    
    Keep your responses friendly, brief, and engaging. Feel free to use emojis and show enthusiasm about Lego.
    Remember: MUST be under 400 characters.
    """
    
    # Create the prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    
    # Create memory with specific output key
    memory = ConversationBufferMemory(
        return_messages=True, 
        memory_key="chat_history",
        output_key="output"  # Explicitly specify which key to use for storing the chat history
    )
    
    # Create the agent
    agent = create_openai_functions_agent(llm, tools, prompt)
    
    # Create the agent executor
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        memory=memory,
        verbose=True,
        return_intermediate_steps=True,
        max_iterations=3,
        handle_parsing_errors=True
    )
    
    return agent_executor

def create_event_agent():
    """Create an agent for handling Twitch events"""
    
    # For events, we don't need all tools
    tools = get_bot_tools()[3:]  # Just get the stream info tool
    
    # Define system message specifically for events
    system_message = """You are BrickNPlateBot, a helpful assistant for a Twitch channel focused on building Lego sets.
    Your task is to generate personalized thank-you messages for Twitch events like subscriptions and raids.
    
    IMPORTANT: Your message MUST be under 400 characters due to Twitch's 500-character limit.
    
    Make your messages brief, friendly, enthusiastic, and Lego-themed.
    
    You can use the get_stream_info tool to incorporate relevant details about the current build or stream schedule
    in your thank-you messages.
    
    For subscribers:
    - Thank them for their support
    - Mention that they're helping to "build" the community
    - For resubscribers, acknowledge their continued support
    
    For raiders:
    - Welcome the raiders
    - Mention what's currently being built (use get_stream_info)
    - Invite them to join the building process
    
    Use Lego-themed language like "building together," "connecting pieces," "essential building blocks," etc.
    Remember: MUST be under 400 characters.
    """
    
    # Create the prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    
    # Create the agent
    agent = create_openai_functions_agent(llm, tools, prompt)
    
    # Create the agent executor (no memory needed for one-off events)
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True,
        return_intermediate_steps=True,
        max_iterations=2,
        handle_parsing_errors=True
    )
    
    return agent_executor

async def process_chat_message(username: str, message: str) -> str:
    """Process a chat message and return a response"""
    agent_executor = create_chat_agent()
    formatted_message = f"{username}: {message}"
    
    try:
        result = await agent_executor.ainvoke({"input": formatted_message})
        return result["output"]
    except Exception as e:
        print(f"Error processing message: {str(e)}")
        return f"Sorry, I encountered an error while processing your message! Error: {str(e)}"

async def process_event(event_type: str, username: str, details: Dict = None) -> str:
    """Process a Twitch event and return a customized message"""
    agent_executor = create_event_agent()
    details = details or {}
    
    # Prepare event description
    if event_type == "subscription":
        event_description = f"{username} has subscribed with tier {details.get('tier', '1000')}."
    elif event_type == "resub":
        event_description = f"{username} has resubscribed for {details.get('months', 1)} months with tier {details.get('tier', '1000')}."
    elif event_type == "raid":
        event_description = f"{username} has raided the channel with {details.get('viewers', 0)} viewers."
    else:
        event_description = f"{username} triggered an event of type {event_type}."
    
    # Add instructions
    prompt = f"{event_description} Generate a personalized thank you message for this {event_type} event. Make it brief, enthusiastic, and Lego-themed."
    
    try:
        result = await agent_executor.ainvoke({"input": prompt})
        return result["output"]
    except Exception as e:
        print(f"Error processing event: {str(e)}")
        
        # Fallback messages
        if event_type == "raid":
            return f"Thanks for the amazing raid, {username}, with {details.get('viewers', 0)} viewers! Welcome to our brick-building adventure!"
        elif event_type in ["subscription", "resub"]:
            months = f"{details.get('months', 1)}-month " if event_type == "resub" and details.get('months') else ""
            return f"Thanks for the {months}sub, {username}! You're an essential piece in our community!"
        else:
            return f"Thanks, {username}! You're awesome!"
