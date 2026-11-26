
import time

from questions import QUESTIONS
from react_agent import run, save_trace

if __name__ == "__main__":
    for name, q in QUESTIONS:
        print(f"\n### {name}: {q}")
        try:
            result = run(q)
        except Exception as e:  
            print(f"  FAILED: {e}")
            continue
        print(result["trace"])
        print("ANSWER:", result["answer"])
        print("Saved", save_trace(result, name))
        time.sleep(2)  
