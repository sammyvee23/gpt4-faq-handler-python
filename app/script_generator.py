# app/script_generator.py

import os
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_call_script(prompt):
    try:
        print("📡 Sending prompt to OpenAI:", prompt)

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # ✅ switched from gpt-4 to gpt-3.5-turbo
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI voice assistant calling on behalf of a nonprofit. Be warm, clear, and friendly."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=300,
            temperature=0.7
        )

        message = response['choices'][0]['message']['content']
        print("✅ Generated script:", message)
        return message

    except Exception as e:
        print(f"❌ OpenAI API Error: {e}")
        return f"Sorry, we were unable to generate the call script. ({e})"


