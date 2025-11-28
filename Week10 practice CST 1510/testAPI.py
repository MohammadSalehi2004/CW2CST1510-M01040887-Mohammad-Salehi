from openai import OpenAI
import os

# Load API key
client = OpenAI(
    api_key="REMOVED"
)

# Context-aware prompt
messages = [
    {"role": "system", "content": "You are a helpful Python assistant."},
    {"role": "user", "content": "Write an explanation of API for beginners."}
]

# Call OpenAI API
response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=messages
)

print(response)
#print(response.choices[0].message["content"])
print(response.choices[0].message.content)