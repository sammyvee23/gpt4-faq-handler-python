# app/script_generator.py

import os
import openai
from openai import OpenAI

# Initialize the OpenAI client with your API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_call_script(prompt):
    try:
        print("🧠 Generating call script with prompt:", prompt)
        
        # Create a chat completion with the OpenAI API
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Use gpt-4 if your account supports it
            messages=[
                {"role": "system", "content": "You are a friendly AI call agent helping nonprofits communicate with supporters."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        message = completion.choices[0].message.content.strip()
        print("✅ Script generated successfully:", message)
        return message

    except openai.OpenAIError as oe:
        print(f"❌ OpenAI API Error: {oe.__class__.__name__} - {oe}")
        return f"Sorry, we were unable to generate the call script. (OpenAI Error: {oe})"

    except Exception as e:
        print(f"❌ Unexpected Error: {e.__class__.__name__} - {e}")
        return f"Sorry, an unexpected error occurred while generating the script. ({e})"



