
import argparse
import json
import os
import re
import time
from datetime import datetime
from pathlib import Path

import litellm
from dotenv import load_dotenv
from litellm import completion

from tools import TOOL_DESCRIPTIONS, TOOLS

load_dotenv()
MODEL = os.getenv("LLM_MODEL", "groq/openai/gpt-oss-20b")
MAX_STEPS = 6
EVIDENCE = Path(__file__).resolve().parent / "evidence"

PROMPT = f"""Answer the question. You can use these tools:

{TOOL_DESCRIPTIONS}

Use EXACTLY this format:

Question: the question you must answer
Thought: think about what to do next
Action: one tool name from [{", ".join(TOOLS)}]
Action Input: the input for the tool
Observation: the tool result (this will be given to you)
... (Thought / Action / Action Input / Observation can repeat)
Thought: I now know the final answer
Final Answer: the answer to the question

Rules:
- Never write the Observation yourself.
- Never guess facts, dates or arithmetic: use a tool.
- If the tools cannot give the answer, say so in the Final Answer instead of inventing one.
- If you can answer without a tool, go straight to Thought and Final Answer.
- Your last line must always start with "Final Answer:".
"""


def native_call_to_text(error_text: str) -> str | None:
    """gpt-oss sometimes answers with a NATIVE tool call even though we gave it no tools.
    Groq then rejects the reply with 'tool_use_failed' and includes the attempted call as
    'failed_generation'. Turn that call back into our text protocol so the loop can go on."""
    m = re.search(r'"failed_generation":"((?:[^"\\]|\\.)*)"', error_text)
    if not m:
        return None
    try:
        call = json.loads(json.loads(f'"{m.group(1)}"'))
    except (json.JSONDecodeError, TypeError):
        return None
    args = call.get("arguments") or {}
    arg = next(iter(args.values()), "") if isinstance(args, dict) else str(args)
    return ("Thought: (the model asked for a tool in its native function-calling format; "
            "converted to the text protocol)\n"
            f"Action: {call.get('name', '')}\nAction Input: {arg}")


def call_model(trace: str):
    """One model call with stop=["Observation:"]. Retries on rate limits.
    Returns (response or None, text)."""
    for attempt in range(4):
        try:
            resp = completion(
                model=MODEL,
                messages=[{"role": "system", "content": PROMPT},
                          {"role": "user", "content": trace}],
                temperature=0,
                stop=["Observation:"],  # stop before the model invents a tool result
            )
            return resp, (resp.choices[0].message.content or "")
        except litellm.RateLimitError:
            wait = 20 * (attempt + 1)
            print(f"  (rate limit reached, waiting {wait}s)")
            time.sleep(wait)
        except litellm.BadRequestError as e:
            text = native_call_to_text(str(e))
            if text is None:
                raise
            return None, text
    raise RuntimeError("Still rate-limited after several retries. Try again in a minute.")


def run(question: str) -> dict:
    """Run the agent on one question. Returns answer, trace, steps and token counts."""
    trace = f"Question: {question}\n"
    tokens = {"prompt": 0, "completion": 0}

    for step in range(1, MAX_STEPS + 1):
        resp, text = call_model(trace)
        if resp is not None and getattr(resp, "usage", None):
            tokens["prompt"] += resp.usage.prompt_tokens or 0
            tokens["completion"] += resp.usage.completion_tokens or 0
        text = text.strip()

        text = re.sub(r"^Question:.*\n?", "", text).strip()
        trace += text + "\n"

        # 1) Finished?
        final = re.search(r"Final Answer:\s*(.*)", text, re.DOTALL)
        if final:
            return {"answer": final.group(1).strip(), "trace": trace, "steps": step, "tokens": tokens}

        # 2) Which tool, with what input?
        action = re.search(r"Action:\s*(.+)", text)
        action_input = re.search(r"Action Input:\s*(.*)", text)
        if not action and text and "Observation:" in trace:
            # The model has already seen a tool result and replied with plain text but no
            # "Final Answer:" label (gpt-oss often writes "**Answer:**"). Accept it as the answer.
            answer = re.sub(r"^(Thought:.*\n)?\s*(\*\*)?Answer:?(\*\*)?:?\s*", "", text).strip()
            trace += "(no 'Final Answer:' label; the reply above was accepted as the final answer)\n"
            return {"answer": answer, "trace": trace, "steps": step, "tokens": tokens}
        if not action:
            observation = "Error: write an Action or a Final Answer in the required format."
        else:
            name = action.group(1).strip().strip("`*").lower()
            arg = action_input.group(1).strip() if action_input else ""
            tool = TOOLS.get(name)
            observation = tool(arg) if tool else f"Error: unknown tool '{name}'. Use one of {list(TOOLS)}."

        # 3) Feed the real result back in
        trace += f"Observation: {observation}\n"

    return {"answer": "Stopped: too many steps without a final answer.", "trace": trace,
            "steps": MAX_STEPS, "tokens": tokens}


def save_trace(result: dict, name: str | None = None) -> Path:
    EVIDENCE.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = EVIDENCE / (f"trace_{name}.txt" if name else f"trace_{stamp}.txt")
    path.write_text(
        f"Model: {MODEL}\nRun at: {stamp}\nSteps: {result['steps']}  Tokens: {result['tokens']}\n\n"
        f"{result['trace']}\nANSWER: {result['answer']}\n",
        encoding="utf-8",
    )
    return path


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="ReAct agent (Lab 2)")
    ap.add_argument("question", nargs="*", help="the question to ask")
    ap.add_argument("--name", help="name for the saved trace file, e.g. 01_one_tool")
    args = ap.parse_args()

    q = " ".join(args.question) or input("Question: ")
    result = run(q)
    print(result["trace"])
    print("=" * 40)
    print("ANSWER:", result["answer"])
    print(f"(steps: {result['steps']}, tokens: {result['tokens']})")
    print("Saved", save_trace(result, args.name))
