# PEAS: Campus Info Bot

Drafted with help from Claude (Anthropic); logged in AI_USE_LOG.md.

The Campus Info Bot answers students' everyday questions about campus (offices, opening hours,
shuttles, registration) in a text chat, using only the facts in `facts.md`.

## Performance measure (how we judge it)

- **Correctness:** every answer agrees with `facts.md`.
- **Honesty:** when `facts.md` has no answer, it says "I don't know" instead of guessing (no invented times, fees or rooms).
- **Context:** follow-up questions ("What about Sunday?") are answered correctly using the earlier turns.
- **Brevity:** answers are at most 3 sentences.
- **Staying in scope:** off-topic requests are politely declined.
- **Speed and cost:** a reply within a few seconds, using as few tokens as possible.

## Environment (where it works)

- A text chat in the terminal.
- Users: students and visitors writing in English, sometimes informally, with typos or vague follow-ups.
- The knowledge source `facts.md`, which can become out of date.
- The model provider (Groq free tier), which can be slow, rate-limited or unavailable.

## Actuators (how it acts)

- Printing a text reply to the user.

## Sensors (how it perceives)

- The text the user types (one percept per message).
- The `facts.md` file, read when the bot starts.
- The conversation history (`history`), which is the percept sequence sent to the model on every turn.

## Environment type

| Property | Classification | Why |
|---|---|---|
| Observable | Partially observable | The bot cannot see the user's intent or the real state of the campus, only the text and `facts.md` |
| Deterministic | Stochastic | Users can ask anything; model output can vary |
| Episodic | Sequential | Follow-up questions depend on earlier turns |
| Static | Static | The facts do not change while the bot is answering |
| Discrete | Discrete | The conversation is a sequence of separate turns |
| Agents | Single-agent | Only the bot acts; the user is part of the environment |
