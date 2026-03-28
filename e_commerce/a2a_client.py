"""
Agent-to-Agent (A2A) Client — Full & Clean
--------------------------------------------
Run server first : python simple_ecommerce_a2a.py
Then run client  : python a2a_agent_client.py
"""

import asyncio
import uuid
import httpx

from a2a.client import A2AClient
from a2a.types import (
    AgentCard,
    SendMessageRequest,
    MessageSendParams,
    Message,
    TextPart,
    Role,
)

from google.adk import Agent
from google.adk.tools import FunctionTool
from google.adk.runners import InMemoryRunner
from google.genai.types import UserContent, Part

from dotenv import load_dotenv
load_dotenv()

SERVER_URL = "http://localhost:8001"


# ══════════════════════════════════════════════
# 🛠️  Tool — wraps the remote A2A server
# ══════════════════════════════════════════════

async def ask_shop_agent(question: str) -> str:
    """
    Forward a question to the remote SimpleShopAgent running on localhost:8001.

    Args:
        question: A question about an order status or product inventory.

    Returns:
        Plain-text reply from the shop agent.
    """
    async with httpx.AsyncClient() as http:

        # Step 1 — fetch agent card
        card_resp = await http.get(f"{SERVER_URL}/.well-known/agent.json")
        card_resp.raise_for_status()
        agent_card = AgentCard(**card_resp.json())

        # Step 2 — build client
        client = A2AClient(httpx_client=http, agent_card=agent_card)

        # Step 3 — send message
        request = SendMessageRequest(
            id=str(uuid.uuid4()),
            params=MessageSendParams(
                message=Message(
                    role=Role.user,
                    messageId=str(uuid.uuid4()),
                    parts=[TextPart(text=question)],
                )
            ),
        )

        response = await client.send_message(request)

        # Step 4 — response is a Task object, walk all possible locations
        result = response.root

        if hasattr(result, "result"):
            task = result.result

            # Shape A — task.artifacts[*].parts[*].text
            if hasattr(task, "artifacts") and task.artifacts:
                for artifact in task.artifacts:
                    for part in artifact.parts or []:
                        p = part.root if hasattr(part, "root") else part
                        if hasattr(p, "text") and p.text:
                            return p.text

            # Shape B — task.status.message.parts[*].text
            if hasattr(task, "status") and task.status:
                msg = getattr(task.status, "message", None)
                if msg and hasattr(msg, "parts"):
                    for part in msg.parts or []:
                        p = part.root if hasattr(part, "root") else part
                        if hasattr(p, "text") and p.text:
                            return p.text

        return "No response received from shop agent."


# ══════════════════════════════════════════════
# 🤖  Caller Agent
# ══════════════════════════════════════════════

caller_agent = Agent(
    name="CallerAgent",
    #model="gemini-2.5-flash",
    model="gemini-2.0-flash-lite",
    description="Routes order and inventory questions to the remote ShopAgent.",
    instruction=(
        "You are a helpful shopping assistant. "
        "Whenever a user asks about an order or product availability, "
        "call the ask_shop_agent tool and relay the answer clearly."
    ),
    tools=[FunctionTool(func=ask_shop_agent)],
)


# ══════════════════════════════════════════════
# 🚀  Main
# ══════════════════════════════════════════════

async def main():
    runner  = InMemoryRunner(agent=caller_agent)
    session = await runner.session_service.create_session(
        app_name=runner.app_name,
        user_id="user_1",
    )

    questions = [
        "What is the status of order ORD-101?",
        "Is SHOE-RUN in stock?",
    ]

    for question in questions:
        print(f"\n🧑 User        : {question}")

        async for event in runner.run_async(
            user_id="user_1",
            session_id=session.id,
            new_message=UserContent(parts=[Part(text=question)]),
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        print(f"🤖 CallerAgent : {part.text}")


if __name__ == "__main__":
    print("🔗 Agent-to-Agent Communication Demo")
    print(f"   Connecting to shop server at {SERVER_URL}\n")
    asyncio.run(main())
