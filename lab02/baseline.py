
import os
from pathlib import Path

from dotenv import load_dotenv
from litellm import completion

from questions import QUESTIONS

load_dotenv()
MODEL = os.getenv("LLM_MODEL", "groq/openai/gpt-oss-20b")
OUT = Path(__file__).resolve().parent / "evidence" / "baseline_raw.txt"

if __name__ == "__main__":
    lines = [f"Model: {MODEL} (no tools)\n"]
    for name, q in QUESTIONS:
        r = completion(model=MODEL, temperature=0, messages=[{"role": "user", "content": q}])
        answer = (r.choices[0].message.content or "").strip()
        block = f"[{name}] Q: {q}\nA: {answer}\n"
        print(block)
        lines.append(block)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print("Saved", OUT)
