import os
from dotenv import load_dotenv
import openai
import requests

# Load API keys from .env file
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
SENDER = f"Sovereignty Score <mailgun@{MAILGUN_DOMAIN}>"
RECIPIENT = "dmh4681@gmail.com"

# Example user + path
username = "DigitalNomad"
selected_path = "physical_optimization"

# Prompt to generate email body
prompt = f"""
You are a motivational coach aligned with the Sovereign Path philosophy. 
Write a welcome email for a new user named {username}, who has selected the "{selected_path.replace("_", " ").title()}" path. 
Make it inspirational and styled like the voice of its associated expert:
- Physical Optimization = Jeff Cavaliere
- Financial Path = Mark Hyman
- Mental Resilience = Andrew Huberman
- Spiritual Growth = Michael Pollan
- Planetary Stewardship = Dylan's sovereign tone

The email should be direct, powerful, and personalized — suitable for sending as a welcome onboarding message.
"""

# Generate with OpenAI
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}]
)
body = response['choices'][0]['message']['content']

# Send via Mailgun
res = requests.post(
    f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
    auth=("api", MAILGUN_API_KEY),
    data={
        "from": SENDER,
        "to": RECIPIENT,
        "subject": f"Welcome to the Sovereignty Score, {username}!",
        "text": body
    }
)

print(f"✅ Email sent! Status: {res.status_code}")
print(res.text)
