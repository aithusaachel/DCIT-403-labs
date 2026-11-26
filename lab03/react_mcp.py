import asyncio
import json
import os
import re
import sys
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
SERVER = StdioServerParameters(command=sys.executable, args=[str(HERE / "server.py")])
MAX_STEPS = 6

DEFAULT_QUESTIONS = [
    "Which items expire within 30 days?",
    "Can I sell 3 Amlodipine 10mg?",
    "Sell 2 Paracetamol 500mg and tell me the total price.",
]


def make_prompt(tools) -> str:
    lines = []
    for t in tools:
        inputs = list(t.inputSchema.get("properties", {}))
        desc = " ".join((t.description or "").split())
        lines.append(f"{t.name}: {desc} Inputs: {inputs}")
    return ("Answer the question about pharmacy stock. You can use these tools:\n"
            + "\n".join(lines) + """

Use EXACTLY this format:
Question: the question
Thought: think about what to do next
Action: one tool name
Action Input: a JSON object with the tool's inputs, e.g. {"item": "Paracetamol", "strength": "500mg"}
Observation: the tool result (this will be given to you)
... (Thought / Action / Action Input / Observation can repeat)
Thought: I now know the final answer
Final Answer: the answer

Never write the Observation yourself. Never guess stock numbers, prices or dates: use a tool.""")


def native_call_to_text(error_text: str) -> str | None:
    """gpt-oss sometimes answers with a NATIVE tool call even though we gave it no tools;
    Groq rejects it ('tool_use_failed') and returns the attempted call as 'failed_generation'.
    Convert it back into the text protocol so the loop can continue."""
    m = re.search(r'"failed_generation":"((?:[^"\\]|\\.)*)"', error_text)
    if not m:
        return None
    try:
        call = json.loads(json.loads(f'"{m.group(1)}"'))
    except (json.JSONDecodeError, TypeError):
        return None
    args = call.get("arguments") or {}
    return ("Thought: (the model asked for a tool in its native function-calling format; "
            "converted to the text protocol)\n"
            f"Action: {call.get('name', '')}\nAction Input: {json.dumps(args)}")


async def call_model(prompt: str, trace: str) -> str:
    for attempt in range(4):
        try:
            resp = completion(model=MODEL, temperature=0, stop=["Observation:"],
                              messages=[{"role": "system", "content": prompt},
                                        {"role": "user", "content": trace}])
            return resp.choices[0].message.content or ""
        except litellm.RateLimitError:
            wait = 20 * (attempt + 1)
            print(f"  (rate limit reached, waiting {wait}s)")
            await asyncio.sleep(wait)
        except litellm.BadRequestError as e:
            text = native_call_to_text(str(e))
            if text is None:
                raise
            return text
    raise RuntimeError("Still rate-limited after several retries. Try again in a minute.")


async def run(session: ClientSession, prompt: str, question: str) -> str:
    trace = f"Question: {question}\n"
    for _ in range(MAX_STEPS):
        text = (await call_model(prompt, trace)).strip()
        text = re.sub(r"^Question:.*\n?", "", text).strip()
        trace += text + "\n"
        if re.search(r"Final Answer:", text):
            return trace
        action = re.search(r"Action:\s*(.+)", text)
        arg = re.search(r"Action Input:\s*(\{.*\})", text, re.DOTALL)
        if not action:
            obs = "Error: write an Action or a Final Answer in the required format."
        else:
            try:
                args = json.loads(arg.group(1)) if arg else {}
                res = await session.call_tool(action.group(1).strip().strip("`*"), args)  # the MCP call
                obs = "\n".join(c.text for c in res.content if hasattr(c, "text"))
            except Exception as e: 
                obs = f"Error: {e}"
        trace += f"Observation: {obs}\n"
    return trace + "Stopped: too many steps without a final answer.\n"


async def main() -> None:
    questions = sys.argv[1:] or DEFAULT_QUESTIONS
    out = [f"Model: {MODEL}\nAgent: Lab 2 text ReAct loop, tools from the Lab 3 MCP server\n\n"]
    async with stdio_client(SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            prompt = make_prompt((await session.list_tools()).tools)
            for q in questions:
                t = await run(session, prompt, q)
                print(t)
                out.append(t + "\n" + "=" * 60 + "\n\n")
                await asyncio.sleep(2)  
    path = HERE / "evidence" / "react_via_mcp.txt"
    path.parent.mkdir(exist_ok=True)
    path.write_text("".join(out), encoding="utf-8")
    print("Saved", path)


if __name__ == "__main__":
    asyncio.run(main())
