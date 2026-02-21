import asyncio
import httpx
from a2a.client import A2AClient
from a2a.types import SendMessageRequest, MessageSendParams, Message, TextPart, Role
import uuid

from dotenv import load_dotenv
load_dotenv()

import asyncio
import httpx
from a2a.client import A2AClient
from a2a.types import SendMessageRequest, MessageSendParams, Message, TextPart, Role
import uuid

async def main():
    async with httpx.AsyncClient(timeout=60.0) as httpx_client:
        # 1️⃣ Fetch Agent Card
        agent_card_response = await httpx_client.get(
            "http://localhost:8001/.well-known/agent.json"
        )
        agent_card_data = agent_card_response.json()
        print("Agent card fetched:", agent_card_data.get("name"))

        # 2️⃣ Create Client
        client = A2AClient(httpx_client=httpx_client, url="http://localhost:8001")

        # 3️⃣ Build Request
        request = SendMessageRequest(
            id=str(uuid.uuid4()),
            params=MessageSendParams(
                message=Message(
                    role=Role.user,
                    parts=[TextPart(text="Please greet Sunny")],
                    messageId=str(uuid.uuid4()),
                )
            ),
        )

        # 4️⃣ Send and Extract Clean Response
        response = await client.send_message(request)
        task = response.root.result

        print(f"\nTask ID : {task.id}")
        print(f"Status  : {task.status.state.value}")

        print("\n--- Agent Response ---")
        if task.artifacts:
            for artifact in task.artifacts:
                for part in artifact.parts:
                    print(part.root.text)
        else:
            print("No artifacts returned.")

if __name__ == "__main__":
    asyncio.run(main())