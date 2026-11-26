
import os
import sys

from dotenv import load_dotenv   
from litellm import completion   

load_dotenv()
MODEL = os.getenv("LLM_MODEL", "groq/openai/gpt-oss-20b")

question = " ".join(sys.argv[1:]) or "What is an intelligent agent?"

messages = [
    {"role": "system", "content": "You are a helpful assistant. Answer in one or two sentences."},
    {"role": "user", "content": question},
]

response = completion(model=MODEL, messages=messages, temperature=0)

print("Model:   ", MODEL)
print("Question:", question)
print("Answer:  ", response.choices[0].message.content)
print("Tokens:  ", response.usage.prompt_tokens, "in +", response.usage.completion_tokens, "out =",
      response.usage.total_tokens)
