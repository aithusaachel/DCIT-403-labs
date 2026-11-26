
import os
from pathlib import Path

from dotenv import load_dotenv
from litellm import completion

load_dotenv()
MODEL = os.getenv("LLM_MODEL", "groq/openai/gpt-oss-20b")
HERE = Path(__file__).resolve().parent

FACTS = (HERE / "facts.md").read_text(encoding="utf-8")

DONT_KNOW = "I don't know that. Please ask at the Computer Science Department office."

SYSTEM_PROMPT = f"""You are the Campus Info Bot. You answer students' questions about campus.

Rules:
- Answer ONLY using the FACTS below. Do not use outside knowledge about the university.
- If the facts do not contain the answer, reply exactly: "{DONT_KNOW}"
- Never guess times, fees, rooms or passwords.
- Use the conversation so far to understand follow-up questions such as "What about Sunday?".
- Politely decline requests that are not about campus information.
- Keep answers to at most 3 sentences.

FACTS:
{FACTS}
"""


def new_history() -> list[dict]:
    """Start a conversation: only the system prompt."""
    return [{"role": "system", "content": SYSTEM_PROMPT}]


def ask(history: list[dict], question: str) -> str:
    """Send one user message with the whole history; record the reply in the history."""
    history.append({"role": "user", "content": question})
    try:
        response = completion(model=MODEL, messages=history, temperature=0)
        answer = (response.choices[0].message.content or "").strip()
    except Exception as e: 
        history.pop() 
        return f"(Error talking to the model: {e})"
    history.append({"role": "assistant", "content": answer})
    return answer


if __name__ == "__main__":
    history = new_history()
    print(f"Campus Info Bot ({MODEL}). Type 'quit' to stop.")
    while True:
        question = input("\nYou: ").strip()
        if question.lower() in ("quit", "exit"):
            break
        if not question:
            continue
        print("Bot:", ask(history, question))
