from google.adk import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from a2a.types import AgentCard
import uvicorn
from google.adk import Agent
from google.adk.tools import FunctionTool
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from a2a.types import AgentCard
import uvicorn

from dotenv import load_dotenv
load_dotenv()

# 1️⃣ Define normal Python function
def greet(name: str) -> str:
    return f"Hello {name}! This is Server responding via A2A."

# 2️⃣ Wrap function as ADK Tool
greet_tool = FunctionTool(func=greet)

# 3️⃣ Create Agent and attach tool
root_agent = Agent(
    name="HelloServer",
    description="Simple A2A server agent",
    model="gemini-2.5-flash",
    tools=[greet_tool],  # 👈 attach tools here
)

# 4️⃣ Agent Card
my_agent_card = AgentCard(
    name="hello_server",
    url="http://localhost:8001",
    description="Test A2A Hello Agent",
    version="1.0.0",
    capabilities={},
    skills=[],
    defaultInputModes=["text/plain"],
    defaultOutputModes=["text/plain"],
    supportsAuthenticatedExtendedCard=False,
)

# 5️⃣ Convert to A2A
a2a_app = to_a2a(root_agent, port=8001, agent_card=my_agent_card)

if __name__ == "__main__":
    uvicorn.run(a2a_app, host="0.0.0.0", port=8001)