# agent.py
from dotenv import load_dotenv
from livekit import agents
from livekit.agents import (
    AgentSession,
    Agent,
    RoomInputOptions,
    ChatContext,
    ChatMessage,
)
from livekit.plugins import google

# your modules
from Jarvis_prompts import instructions_prompt, Reply_prompts
from memory_loop import MemoryExtractor
from jarvis_reasoning import thinking_capability

import inspect

load_dotenv()


class Assistant(Agent):
    def __init__(self, chat_ctx: ChatContext) -> None:
        # call parent with the correct runtime objects
        super().__init__(
            chat_ctx=chat_ctx,
            instructions=instructions_prompt,
            llm=google.beta.realtime.RealtimeModel(model="gemini-2.0-flash-exp", voice="Charon"),
            tools=[thinking_capability],
        )


async def entrypoint(ctx):
    """
    Entry point invoked by livekit.agents Worker.
    `ctx` is provided by the runtime and should contain ctx.room etc.
    """
    # create a session with backward/forward-compatible handling of the
    # preemptive_generation kwarg (some livekit versions accept it)
    session_kwargs = {}
    init_params = inspect.signature(AgentSession.__init__).parameters
    if "preemptive_generation" in init_params:
        session_kwargs["preemptive_generation"] = True

    # add other session args if needed (e.g., stt plugin) in session_kwargs
    session = AgentSession(**session_kwargs)

    # create an empty chat context or build from incoming ctx if required
    # Many runtimes accept a ChatContext() or similar; adjust if your runtime differs.
    chat_ctx = ChatContext()

    # Start the session (async)
    await session.start(
        room=ctx.room,
        agent=Assistant(chat_ctx=chat_ctx),
        room_input_options=RoomInputOptions(
            # noise_cancellation=silero_vad.VoiceActivityDetector()
        ),
    )

    # After the session starts you can read the history (if any)
    current_ctx = getattr(session, "history", None)
    current_items = getattr(current_ctx, "items", None)

    # Generate a reply using the assistant
    await session.generate_reply(instructions=Reply_prompts)

    # Run your memory extractor on the conversation context (if it expects items)
    conv_ctx = MemoryExtractor()
    # If MemoryExtractor.run is async, await it; otherwise call it synchronously
    run_func = getattr(conv_ctx, "run")
    if inspect.iscoroutinefunction(run_func):
        await conv_ctx.run(current_items)
    else:
        conv_ctx.run(current_items)

    # Optionally stop the session (depends on your desired lifecycle)
    # await session.stop()


if __name__ == "__main__":
    # Run the livekit worker with the entrypoint function
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
