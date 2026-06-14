from google.adk import Agent
from google.adk.tools import FunctionTool
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from a2a.types import AgentCard
import uvicorn
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────
#  Fake "Database"
# ─────────────────────────────

ORDERS = {
    "ORD-101": {"status": "shipped",    "item": "Blue T-Shirt",  "total": 29.99, "tracking": "TRK-001"},
    "ORD-102": {"status": "processing", "item": "Running Shoes", "total": 89.99, "tracking": None},
    "ORD-103": {"status": "delivered",  "item": "Leather Bag",   "total": 149.00,"tracking": "TRK-002"},
}

INVENTORY = {
    "TSHIRT-BLU": {"name": "Blue T-Shirt",   "stock": 10, "price": 29.99},
    "SHOE-RUN":   {"name": "Running Shoes",   "stock": 0,  "price": 89.99},
    "BAG-LTH":    {"name": "Leather Bag",     "stock": 4,  "price": 149.00},
}


# ─────────────────────────────
#  Tool 1 — get_order_status
# ─────────────────────────────

def get_order_status(order_id: str) -> dict:
    """
    Get the current status of an order by its ID.

    Args:
        order_id: Order ID like 'ORD-101'.

    Returns:
        Order details or an error message.
    """
    order = ORDERS.get(order_id.upper())
    if not order:
        return {"error": f"Order '{order_id}' not found."}

    return {
        "order_id": order_id.upper(),
        "item":     order["item"],
        "status":   order["status"],
        "total":    f"${order['total']}",
        "tracking": order["tracking"] or "Not yet assigned",
    }


# ─────────────────────────────
# Tool 2 — check_inventory
# ─────────────────────────────

def check_inventory(sku: str) -> dict:
    """
    Check stock availability for a product SKU.

    Args:
        sku: Product SKU like 'TSHIRT-BLU'.

    Returns:
        Stock info or an error message.
    """
    item = INVENTORY.get(sku.upper())
    if not item:
        return {"error": f"SKU '{sku}' not found."}

    in_stock = item["stock"] > 0
    return {
        "sku":        sku.upper(),
        "name":       item["name"],
        "price":      f"${item['price']}",
        "stock":      item["stock"],
        "available":  "✅ In stock" if in_stock else "❌ Out of stock",
    }

# Agent

root_agent = Agent(
    name="SimpleShopAgent",
    description="A simple e-commerce agent that checks orders and inventory.",
    model="gemini-2.5-flash-lite",
    tools=[
        FunctionTool(func=get_order_status),
        FunctionTool(func=check_inventory),
    ],
)

# ─────────────────────────────
# AgentCard tells other agents who you are, where you are located, what you do, what formats you accept, 
# and what capabilities you expos
# ─────────────────────────────

my_agent_card = AgentCard(
    name="simple_shop_agent",
    url="http://localhost:8001",
    description="Checks order status and product inventory.",
    version="1.0.0",
    capabilities={},
    skills=[
        {
            "id": "order_tracking",           # ✅ required unique ID
            "name": "order_tracking",
            "description": "Track customer orders",
            "tags": ["orders", "tracking", "ecommerce"],  # ✅ required list
        },
        {
            "id": "inventory_lookup",          # ✅ required unique ID
            "name": "inventory_lookup",
            "description": "Check product availability",
            "tags": ["inventory", "stock", "ecommerce"],  # ✅ required list
        },
    ],
    defaultInputModes=["text/plain"],
    defaultOutputModes=["text/plain"],
    supportsAuthenticatedExtendedCard=False,
)

# ─────────────────────────────
# 🚀  Run
# ─────────────────────────────

a2a_app = to_a2a(root_agent, port=8001, agent_card=my_agent_card) # Exposes the ADK agent as an A2A server

if __name__ == "__main__":
    print(" Simple Shop A2A Server running on http://localhost:8001")
    uvicorn.run(a2a_app, host="0.0.0.0", port=8001)