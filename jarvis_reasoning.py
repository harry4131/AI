from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from Jarvis_google_search import google_search, get_current_datetime
from livekit.agents import function_tool
from livekit import agents
from Jarvis_prompts import load_prompts
load_dotenv()

@function_tool(
    name="thinking_capability",
    description=(
        "Use this tool whenever the user asks to generate or write something new. "
        "If the user does not specify where to write, open Notepad automatically using open_app and start writing. "
        "This tool can also handle tasks like Google search, checking the weather, "
        "opening/closing apps, accessing files, controlling mouse/keyboard, "
        "and system utilities."
    ),
)
async def thinking_capability(query: str) -> dict:
    """
    LangChain-powered reasoning and action tool.
    Takes a natural language query and executes the appropriate workflow.
    """

    # LLM (Google Gemini via langchain_google_genai)
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

    # Define tools list once to avoid duplication
    tools = [
        google_search,
        get_current_datetime,
    ]

    # For simplicity, use the model directly with a prompt
    prompt = load_prompts() + f"\n\nUser query: {query}\n\nAvailable tools: {tools}\n\nRespond with reasoning and action."
    
    try:
        # Call the model directly
        response = await model.ainvoke(prompt)
        # Normalize response
        if hasattr(response, "content"):
            return {"output": response.content}
        return {"output": str(response)}
    except Exception as e:
        return {"error": f"Model execution failed: {str(e)}"}
