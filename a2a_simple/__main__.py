import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import GreetingAgentExecutor


def main():
    skill = AgentSkill(
        id="hello_world",
        name="Greet",
        description="Return a greeting",
        tags=["greeting", "hello", "world"],
        examples=["Hey", "Hello", "Hi"],
    )

    agent_card = AgentCard(
        name="Greeting Agent",
        description="A simple agent that returns a greeting",
        url="http://localhost:9999/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    request_handler = DefaultRequestHandler(
        agent_executor=GreetingAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    # A2AStarletteApplication is a Starlette-based ASGI wrapper that turns your agent into a fully functional A2A-compliant HTTP server.

    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )
    
    # It makes your agent accessible over HTTP following the A2A protocol, allowing it to interact with other agents and services in a standardized way.
    uvicorn.run(server.build(), host="0.0.0.0", port=9999)

if __name__ == "__main__":
    main()
