"""
Fixed A2A Client — Way 2 (Plain HTTP)
"""

import requests
import json
import uuid

def way2_plain_http():
    print("\n=== WAY 2: Plain HTTP POST ===")

    url = "http://localhost:8001"

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "message/send",
        "params": {
            "message": {
                "role": "user",
                "messageId": str(uuid.uuid4()),
                "parts": [
                    {"kind": "text", "text": "Is SHOE-RUN in stock?"}
                ]
            }
        }
    }

    response = requests.post(url, json=payload)

    # ── Step 1: print raw so we know the real shape ──
    print("Status Code :", response.status_code)
    print("Raw JSON    :", json.dumps(response.json(), indent=2))

    data = response.json()

    # ── Step 2: safely walk the response ──
    # A2A servers can return the reply nested differently depending on version.
    # We try the most common shapes in order.

    reply = None

    # Shape A  →  data["result"]["parts"][0]["text"]
    if "result" in data:
        result = data["result"]
        parts  = result.get("parts") or []
        if parts:
            reply = parts[0].get("text")

    # Shape B  →  data["result"]["artifacts"][0]["parts"][0]["text"]
    if not reply and "result" in data:
        artifacts = data["result"].get("artifacts") or []
        if artifacts:
            parts = artifacts[0].get("parts") or []
            if parts:
                reply = parts[0].get("text")

    # Shape C  →  data["result"]["messages"][-1]["parts"][0]["text"]
    if not reply and "result" in data:
        messages = data["result"].get("messages") or []
        if messages:
            parts = messages[-1].get("parts") or []
            if parts:
                reply = parts[0].get("text")

    # Shape D  →  JSON-RPC error
    if not reply and "error" in data:
        reply = f"Server returned error: {data['error']}"

    print("\nAgent says:", reply or "Could not parse reply — see Raw JSON above")


if __name__ == "__main__":
    print("Make sure server is running")
    way2_plain_http()