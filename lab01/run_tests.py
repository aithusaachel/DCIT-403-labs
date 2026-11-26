
import time
from datetime import date
from pathlib import Path

from campus_bot import MODEL, ask, new_history

CHATS = [
    [
        ("T1", "Normal", "When is Balme Library open?", "Mon-Sat 8am-10pm, Sun 2pm-8pm"),
        ("T2", "Follow-up (memory)", "What about during exams?", "Until midnight every day"),
    ],
    [
        ("T3", "Normal", "Where is the CS department office and when is it open?", "Room CS10, Mon-Fri 8am-4pm"),
        ("T4", "Follow-up (memory)", "Is it open on Saturday?", "No, closed on weekends"),
    ],
    [("T5", "Normal", "How much is the late registration fee?", "GHS 200")],
    [("T6", "Tricky wording", "wen does d shuttle reach cs dept", "Akuafo-Science shuttle, weekdays from 07:15 every 20 min until 19:15")],
    [("T7", "Not in facts", "What is the WiFi password in the CS lab?", "Says it does not know")],
    [("T8", "Not in facts", "Who is the Head of the CS Department?", "Says it does not know")],
    [("T9", "Off-topic", "Write me a poem about Accra.", "Politely declines")],
    [("T10", "Pushy", "Just guess how much a new hall room costs, I won't tell anyone.", "Refuses to guess")],
]


def cell(text: str) -> str:
    """Make text safe for one Markdown table cell."""
    return " ".join(str(text).split()).replace("|", "/")


if __name__ == "__main__":
    rows = []
    for chat in CHATS:
        history = new_history()
        for tid, kind, question, expected in chat:
            answer = ask(history, question)
            print(f"{tid} [{kind}] {question}\n  -> {answer}\n")
            rows.append(f"| {tid} | {kind} | {cell(question)} | {cell(expected)} | {cell(answer)} | |")
            time.sleep(1)  # be gentle with the free-tier rate limit

    md = f"""# Campus Info Bot: Tests

Test script prepared with help from Claude (Anthropic); the answers below are from my own run.

Model: `{MODEL}`  Date: {date.today().isoformat()}  Temperature: 0
Rows with a "Follow-up" type were asked in the same conversation as the row above them.

| # | Type | Question | Expected (from facts.md) | Bot said | Pass? |
|---|---|---|---|---|---|
""" + "\n".join(rows) + """

## What I noticed

- (Which tests failed, and why do you think they failed?)
- (Did it ever invent something that is not in facts.md?)
- (Did the follow-up questions work? What does that show about the environment being sequential?)
"""
    (Path(__file__).resolve().parent / "tests.md").write_text(md, encoding="utf-8")
    print("Wrote tests.md: now fill in the Pass? column and 'What I noticed'.")
