
import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import litellm
from dotenv import load_dotenv
from litellm import completion
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()
# Windows terminals default to cp1252 and crash on characters the model uses (e.g.  )
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
MODEL = os.getenv("LLM_MODEL", "groq/openai/gpt-oss-20b")
HERE = Path(__file__).resolve().parent
LOG = HERE / "evidence" / "tool_calls.jsonl"
MAX_STEPS = 6

SYSTEM = """You are a pharmacy stock assistant for pharmacy staff.
- Use the tools for every fact about stock, prices and expiry. Never guess numbers.
- If an item comes in several strengths and the user did not say which, ask (or list them) before selling.
- Never oversell and never sell expired stock.
- Keep answers short and give prices in GHS."""

DEMO = [
    "Which items expire in the next 60 days?",
    "How many Amoxicillin do we have?",
    "Sell 2 packs of Paracetamol 500mg.",
    "Sell 3 Amlodipine 10mg.",
    "Sell 500 packs of Ibuprofen 400mg.",
    "What is the price of Panadol Extra?",
]

SERVER = StdioServerParameters(command=sys.executable, args=[str(HERE / "server.py")])


def to_schema(tool) -> dict:
    """Turn an MCP tool into the function-calling format the model expects."""
    return {"type": "function", "function": {
        "name": tool.name, "description": tool.description or "", "parameters": tool.inputSchema}}


def log(question: str, name: str, args: dict, result: str) -> None:
    LOG.parent.mkdir(exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(), "model": MODEL,
                            "question": question, "tool": name, "args": args, "result": result},
                           ensure_ascii=False) + "\n")


async def call_model(messages: list, schemas: list):
    """One function-calling request; waits and retries on the free-tier rate limit."""
    for attempt in range(4):
        try:
            return completion(model=MODEL, messages=messages, tools=schemas, temperature=0)
        except litellm.RateLimitError:
            wait = 20 * (attempt + 1)
            print(f"  (rate limit reached, waiting {wait}s)")
            await asyncio.sleep(wait)
    raise RuntimeError("Still rate-limited after several retries. Try again in a minute.")


async def ask(session: ClientSession, schemas: list, messages: list, question: str) -> str:
    messages.append({"role": "user", "content": question})
    for _ in range(MAX_STEPS):
        resp = await call_model(messages, schemas)
        msg = resp.choices[0].message
        if not msg.tool_calls:  # a plain answer: done
            answer = msg.content or ""
            messages.append({"role": "assistant", "content": answer})
            return answer
        messages.append(msg.model_dump())  # keep the model's tool request BEFORE the results
        for tc in msg.tool_calls:
            name = tc.function.name
            try:
                args = json.loads(tc.function.arguments or "{}")
                res = await session.call_tool(name, args)  # runs on the MCP server
                text = "\n".join(c.text for c in res.content if hasattr(c, "text"))
            except Exception as e:  # noqa: BLE001
                args, text = {}, f"Tool error: {e}"
            print(f"  [tool] {name}({args}) -> {text[:150]}")
            log(question, name, args, text)
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": text})
    return "Sorry, I could not finish that. Please check the stock manually."


async def main() -> None:
    async with stdio_client(SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = (await session.list_tools()).tools
            schemas = [to_schema(t) for t in tools]
            print(f"Connected ({MODEL}). Tools:", [t.name for t in tools])
            messages = [{"role": "system", "content": SYSTEM}]

            if "--demo" in sys.argv:
                # each demo question is an independent test: fresh conversation each time
                # (also keeps the token count under the free-tier per-minute limit)
                for q in DEMO:
                    print(f"\nYou: {q}")
                    fresh = [{"role": "system", "content": SYSTEM}]
                    print("Agent:", await ask(session, schemas, fresh, q))
                    await asyncio.sleep(5)  # free-tier rate limit
                return

            print("Type 'quit' to exit.")
            while True:
                q = (await asyncio.to_thread(input, "\nYou: ")).strip()
                if q.lower() in ("quit", "exit"):
                    break
                if q:
                    print("Agent:", await ask(session, schemas, messages, q))


if __name__ == "__main__":
    asyncio.run(main())
