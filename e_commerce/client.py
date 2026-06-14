"""
Simple Gradio Chat Client for SimpleShopAgent A2A Server
---------------------------------------------------------
Run server first : python server.py
Then run client  : python client.py
"""

import asyncio
import uuid
import httpx
import gradio as gr

from a2a.client import A2AClient
from a2a.types import (
    AgentCard,
    SendMessageRequest,
    MessageSendParams,
    Message,
    TextPart,
    Role,
)

from dotenv import load_dotenv
load_dotenv()

SERVER_URL = "http://localhost:8001"


# ──────────────────────────────
# 📡  Send message to A2A server
# ──────────────────────────────

async def ask_shop_agent(question: str) -> str:
    async with httpx.AsyncClient() as http:

        # Fetch agent card
        card = AgentCard(**( await http.get(f"{SERVER_URL}/.well-known/agent.json")).json())

        # Build client & send message
        client = A2AClient(httpx_client=http, agent_card=card)

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

        # Extract text from response
        try:
            task = response.root.result

            # Shape A — artifacts
            for artifact in task.artifacts or []:
                for part in artifact.parts or []:
                    p = getattr(part, "root", part)
                    if getattr(p, "text", None):
                        return p.text

            # Shape B — status message
            for part in task.status.message.parts or []:
                p = getattr(part, "root", part)
                if getattr(p, "text", None):
                    return p.text

        except Exception:
            pass

        return "No response received from shop agent."


# ──────────────────────────────
# 🎨  Gradio Chat Handler
# ──────────────────────────────

def chat(message, history):
    try:
        reply = asyncio.run(ask_shop_agent(message))
    except Exception as e:
        reply = f"❌ Error: {str(e)}\n\nMake sure the server is running at {SERVER_URL}"
    return reply


# ──────────────────────────────
# 🚀  Launch UI
# ──────────────────────────────

with gr.Blocks(title="🛒 Shop Agent") as demo:
    gr.Markdown("## 🛒 Simple Shop Agent")
    gr.Markdown(
        "Ask me about **order status** or **product inventory**.\n\n"
        "Try: *What is the status of ORD-101?* or *Is SHOE-RUN in stock?*"
    )

    gr.ChatInterface(
        fn=chat,
        examples=[
            "What is the status of order ORD-101?",
            "What is the status of order ORD-102?",
            "What is the status of order ORD-103?",
            "Is TSHIRT-BLU in stock?",
            "Is SHOE-RUN in stock?",
            "Check inventory for BAG-LTH",
        ],
    )

if __name__ == "__main__":
    print(f"🔗 Connecting to shop agent at {SERVER_URL}")
    demo.launch()