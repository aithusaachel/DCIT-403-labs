# Baseline vs ReAct agent

Template prepared with help from Claude (Anthropic). Claude copied the answers and numbers below from my runs and drafted the "Who was right?" column; I checked them.

Model: `groq/openai/gpt-oss-20b`  Date of runs: 2026-11-25

- Plain model: `python baseline.py` (raw output in `baseline_raw.txt`)
- ReAct agent: `python make_traces.py` (traces in `trace_01_*.txt` to `trace_06_*.txt`)

| # | Question | Plain model (no tools) | ReAct agent | Correct answer | Who was right? |
|---|---|---|---|---|---|
| 1 | What is 17.5% of 3480, plus 129? | 738 (worked it out step by step) | 738 (via calculator; first call failed on `17.5% of 3480`, retried with `0.175*3480+129`) | 738 | Both |
| 2 | When is the library open? | Asked which library; gave no hours | Balme: Mon-Sat 8am-10pm, Sun 2pm-8pm, midnight in exams (via campus_fact) | from lab01/facts.md | Agent |
| 3 | What day is it today, and is the CS office open that day? | Wednesday; open (assumed "standard" Mon-Fri hours, not from facts) | Wednesday; open (via today + campus_fact) | Wednesday 2026-11-25; open 8am-4pm | Agent (plain model right only by guessing) |
| 4 | What does PEAS stand for? | Performance measure, Environment, Actuators, Sensors (long answer) | Performance measure, Environment, Actuators, Sensors (no tool) | Performance, Environment, Actuators, Sensors | Both |
| 5 | What is 250 divided by 0? | Undefined | Undefined (answered without calling the calculator) | Undefined (cannot divide by zero) | Both |
| 6 | What is the WiFi password in the CS lab? | "I can't help with that" (refused) | "I couldn't find the WiFi password" (after checking campus_fact) | Not known: should say so | Agent (plain model refused rather than saying it is not known) |

## Steps and tokens (agent)

| # | Steps | Prompt tokens | Completion tokens |
|---|---|---|---|
| 1 | 3 | 421 | 170 |
| 2 | 2 | 410 | 135 |
| 3 | 3 | 530 | 87 |
| 4 | 1 | 313 | 106 |
| 5 | 1 | 311 | 130 |
| 6 | 2 | 377 | 157 |

Failed earlier runs (kept as evidence): Q2 took 6 steps, 2393 prompt + 1557 completion tokens (`trace_02b`); Q3 took 6 steps, 1708 + 3009 tokens (`trace_03b`). Both stopped without a Final Answer.

## What I learned

- (Where did tools help? Where did the plain model guess?)
- (What did the agent cost in extra steps and tokens?)
- (Any trace where the agent broke the format or failed, and why?)
