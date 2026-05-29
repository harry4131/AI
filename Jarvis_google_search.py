import os
import logging
from datetime import datetime

from dotenv import load_dotenv
from livekit.agents import function_tool
from openai import AsyncOpenAI

# Load environment variables
load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenAI client (API key must be in OPENAI_API_KEY env var)
client = AsyncOpenAI()


@function_tool
async def openai_search(query: str) -> str:
    """
    Web search using OpenAI. Returns a short, speech-friendly summary.
    """

    if not os.getenv("OPENAI_API_KEY"):
        return "Missing environment variable: OPENAI_API_KEY"

    try:
        response = await client.responses.create(
            model="gpt-4.1-mini",
            tools=[{"type": "web_search"}],
            input=query,
        )
    except Exception as e:
        logger.error(e)
        return "OpenAI search failed."

    text = []
    for item in response.output:
        if item["type"] == "output_text":
            text.append(item["text"])

    return "".join(text).strip() or "No results found."


@function_tool
async def get_current_datetime() -> str:
    """
    Returns the current date and time.
    """
    now = datetime.now()
    return now.strftime("%d %B %Y, %I:%M %p")
