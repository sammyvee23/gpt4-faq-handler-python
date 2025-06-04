import openai
import os

openai.api_key = os.environ.get("OPENAI_API_KEY")

def generate_call_script(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful customer service AI that speaks clearly and professionally."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=250
    )
    return response.choices[0].message['content'].strip()
