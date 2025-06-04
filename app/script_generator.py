import openai
import os

# Load OpenAI API key from environment variable
openai.api_key = os.environ.get("OPENAI_API_KEY")

def generate_call_script(prompt):
    """
    Generates a professional and friendly AI phone call script based on the given prompt.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a polite and helpful AI assistant speaking to a customer over the phone."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=250
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"Sorry, we were unable to generate the call script. ({e})"

