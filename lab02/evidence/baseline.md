# Baseline vs ReAct agent

Template prepared with help from Claude (Anthropic); the answers below come from my own runs.

Model: `groq/openai/gpt-oss-20b`  Date of runs: (fill in)

- Plain model: `python baseline.py` (raw output in `baseline_raw.txt`)
- ReAct agent: `python make_traces.py` (traces in `trace_01_*.txt` to `trace_06_*.txt`)

| # | Question | Plain model (no tools) | ReAct agent | Correct answer | Who was right? |
|---|---|---|---|---|---|
| 1 | What is 17.5% of 3480, plus 129? | | | 738 | |
| 2 | When is the library open? | | | from lab01/facts.md | |
| 3 | What day is it today, and is the CS office open that day? | | | (day of the run) + facts.md | |
| 4 | What does PEAS stand for? | | | Performance, Environment, Actuators, Sensors | |
| 5 | What is 250 divided by 0? | | | Undefined (cannot divide by zero) | |
| 6 | What is the WiFi password in the CS lab? | | | Not known: should say so | |

## Steps and tokens (agent)

| # | Steps | Prompt tokens | Completion tokens |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |
| 6 | | | |

## What I learned

- (Where did tools help? Where did the plain model guess?)
- (What did the agent cost in extra steps and tokens?)
- (Any trace where the agent broke the format or failed, and why?)
