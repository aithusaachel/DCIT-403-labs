# AI-Use Log

Add one row every time you use an AI tool for lab work (see Lab Manual Section 4).
Copy the rows for each lab into that lab's report.

| Date | Lab | Tool | What I asked | What I used | What I changed or checked |
|---|---|---|---|---|---|
| 2026-11-25 | 1-3 | Claude (Anthropic) | Explain what Labs 1, 2 and 3 require, step by step | The explanations as a study guide | Checked against the lab README files; the Lab Manual is the authority |
| 2026-11-25 | 1 | Claude (Anthropic) | Write lab01/facts.md for the Campus Info Bot | The 14 facts: real UG place names with fictional times, rooms and fees | Checked each line before use; I will replace any detail I can confirm on campus |
| 2026-11-25 | 1 | Claude (Anthropic) | Write the rest of Lab 1: hello_llm.py, campus_bot.py, peas.md and run_tests.py (which generates tests.md) | All of that code and the PEAS description, as written by Claude | Claude also ran run_tests.py on my PC to generate tests.md. I judged every test result (Pass? column), took the screenshots and wrote concept_check.md in my own words |
| 2026-11-25 | 2 | Claude (Anthropic) | Write the Lab 2 code: tools.py, react_agent.py, baseline.py, questions.py, make_traces.py, and the baseline.md template | All of that code, as written by Claude | Claude also ran make_traces.py and baseline.py on my PC, and fixed the loop when gpt-oss replied with native tool calls. I read and checked every trace, filled in baseline.md, and wrote concept_check.md in my own words |
| 2026-11-25 | 3 | Claude (Anthropic) | Write the Lab 3 code: server.py (MCP server, 4 tools + 1 resource), client_agent.py, react_mcp.py | All of that code, as written by Claude | Claude also tested the server tools and ran both agents on my PC to produce tool_calls.jsonl and react_via_mcp.txt. I tested every tool in the MCP Inspector, checked the outputs, and wrote concept_check.md in my own words |
| 2026-11-26 | 1-2 | Claude (Anthropic) | Fill in the result tables in lab01/tests.md (Pass? column) and lab02/evidence/baseline.md | Claude copied answers, steps and token counts from my runs and drafted the Pass? and "Who was right?" verdicts | I checked each verdict against facts.md and the traces. The "What I noticed / learned" notes and all concept checks are my own |
| 2026-11-26 | 3 | Claude (Anthropic) | Check that Lab 3 works | Claude tested all 4 server tools and the resource, ran both agents, and fixed a crash on Windows (the terminal could not print some characters in the model's replies, so both agents now print in UTF-8) | I reran the agents to confirm |
