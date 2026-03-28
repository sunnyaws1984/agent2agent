async for event in runner.run_async(...):
    if event.content and event.content.parts:
        for part in event.content.parts:
            if hasattr(part, "text") and part.text:
                print(f"🤖 CallerAgent : {part.text}")
```

`run_async` returns a **stream of events**, not a single response. Each event can be:
```
Event 1 → LLM decides to call ask_shop_agent  (no text yet)
Event 2 → tool executes, result comes back    (no text yet)
Event 3 → LLM generates final answer          (✅ has text)
```

That's why we check `if part.text` — we only want to print the final text events.

---

## 🔗 How It All Ties Together
```
User types: "What is the status of order ORD-101?"
     │
     ▼
runner.run_async() feeds it to CallerAgent
     │
     ▼
Gemini sees the question + available tools
Gemini decides: "I should call ask_shop_agent"
     │
     ▼
FunctionTool calls ask_shop_agent("What is the status of order ORD-101?")
     │
     ▼
ask_shop_agent() makes HTTP POST to localhost:8001
     │
     ▼
SimpleShopAgent (server) receives it
Gemini (server-side) calls get_order_status("ORD-101")
Returns: { status: "shipped", tracking: "TRK-001", ... }
     │
     ▼
Response travels back as a Task object
ask_shop_agent() parses it → returns plain string to CallerAgent
     │
     ▼
CallerAgent (Gemini) gets the string, formats a nice reply
     │
     ▼
Event stream emits the final text
main() prints: "🤖 CallerAgent : Order ORD-101 is shipped..."