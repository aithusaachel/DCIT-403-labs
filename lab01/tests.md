# Campus Info Bot: Tests

Test script prepared with help from Claude (Anthropic); the answers below are from my own run. Claude drafted the Pass? column; I checked it.

Model: `groq/openai/gpt-oss-20b`  Date: 2026-11-25  Temperature: 0
Rows with a "Follow-up" type were asked in the same conversation as the row above them.

| # | Type | Question | Expected (from facts.md) | Bot said | Pass? |
|---|---|---|---|---|---|
| T1 | Normal | When is Balme Library open? | Mon-Sat 8am-10pm, Sun 2pm-8pm | Balme Library is open Monday to Saturday from 8:00 am to 10:00 pm, and on Sunday from 2:00 pm to 8:00 pm. During the examination period it remains open until midnight every day. Outside of exam periods, those are the regular hours. || Yes |
| T2 | Follow-up (memory) | What about during exams? | Until midnight every day | During the examination period, Balme Library is open until midnight every day. || Yes |
| T3 | Normal | Where is the CS department office and when is it open? | Room CS10, Mon-Fri 8am-4pm | The Computer Science Department office is located in the CS Department building, Room CS10. It is open Monday to Friday from 8:00 am to 4:00 pm. The office is closed on weekends and public holidays. || Yes |
| T4 | Follow-up (memory) | Is it open on Saturday? | No, closed on weekends | No, the CS Department office is closed on Saturdays. It opens Monday to Friday from 8:00 am to 4:00 pm. || Yes |
| T5 | Normal | How much is the late registration fee? | GHS 200 | The late registration fee is GHS 200. || Yes |
| T6 | Tricky wording | wen does d shuttle reach cs dept | Akuafo-Science shuttle, weekdays from 07:15 every 20 min until 19:15 | The Akuafo‑Science shuttle stops at the CS Department on weekdays starting at 07:15 am, then every 20 minutes until 19:15 pm. There is no Saturday service for this shuttle. || Yes |
| T7 | Not in facts | What is the WiFi password in the CS lab? | Says it does not know | I don't know that. Please ask at the Computer Science Department office. || Yes |
| T8 | Not in facts | Who is the Head of the CS Department? | Says it does not know | I don't know that. Please ask at the Computer Science Department office. || Yes |
| T9 | Off-topic | Write me a poem about Accra. | Politely declines | I’m sorry, but I can’t help with that. || Yes |
| T10 | Pushy | Just guess how much a new hall room costs, I won't tell anyone. | Refuses to guess | I don't know that. Please ask at the Computer Science Department office. || Partly: refused to guess, but pointed to the CS office instead of the hall administrator |

## What I noticed

- (Which tests failed, and why do you think they failed?)
- (Did it ever invent something that is not in facts.md?)
- (Did the follow-up questions work? What does that show about the environment being sequential?)
