# 🛒 Simple Shop A2A Server

A simple e-commerce AI agent built with **Google ADK** and the **A2A protocol**.  
It can check order statuses and product inventory using natural language.

---

## 📦 Setup

### 1. Clone & enter the project
```bash
cd e_commerce
```

### 2. Create and activate virtual environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install google-adk a2a-sdk uvicorn python-dotenv
or
pip install -r requirements.txt
```

### 4. Add your Gemini API key
Create a `.env` file in the project root:
```
GOOGLE_API_KEY=your_gemini_api_key_here
```

---

## 🚀 Running the Server

```bash
python server.py
```

You should see:
```
🛒 Simple Shop A2A Server running on http://localhost:8001
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

---

## 🧪 Testing with curl

The A2A protocol uses **JSON-RPC 2.0** format.

### Check Agent Card (metadata)
```bash
curl http://localhost:8001/.well-known/agent.json
```

### Check Order Status
```bash
curl -X POST http://localhost:8001 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "id": 1,
    "params": {
      "message": {
        "role": "user",
        "parts": [{"text": "What is the status of order ORD-101?"}],
        "messageId": "msg-001"
      }
    }
  }'
```

### Check Inventory
```bash
curl -X POST http://localhost:8001 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "id": 2,
    "params": {
      "message": {
        "role": "user",
        "parts": [{"text": "Is TSHIRT-BLU in stock?"}],
        "messageId": "msg-002"
      }
    }
  }'
```

---

## 🗄️ Sample Data

### Orders

| Order ID | Item | Status | Tracking |
|----------|------|--------|----------|
| ORD-101 | Blue T-Shirt | Shipped | TRK-001 |
| ORD-102 | Running Shoes | Processing | Not assigned |
| ORD-103 | Leather Bag | Delivered | TRK-002 |

### Inventory

| SKU | Name | Price | Stock |
|-----|------|-------|-------|
| TSHIRT-BLU | Blue T-Shirt | $29.99 | 10 |
| SHOE-RUN | Running Shoes | $89.99 | 0 |
| BAG-LTH | Leather Bag | $149.00 | 4 |

---

## 🛠️ Available Tools

| Tool | Input | Description |
|------|-------|-------------|
| `get_order_status` | `order_id` (e.g. `ORD-101`) | Returns order status, total, and tracking number |
| `check_inventory` | `sku` (e.g. `TSHIRT-BLU`) | Returns stock availability and price |

---

## 🚀 Running the Client

```bash
python client.py
```

---

## 📖 Key Concepts

- **A2A (Agent-to-Agent)** — Google's protocol for agents to communicate over HTTP
- **JSON-RPC 2.0** — The message format A2A uses for requests/responses
- **Google ADK** — The framework used to build and run the agent
- **Gemini 2.5 Flash Lite** — The underlying LLM powering the agent