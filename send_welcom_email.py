import os
from dotenv import load_dotenv
import openai
import requests

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
SENDER = f"Sovereignty Score <mailgun@{MAILGUN_DOMAIN}>"
RECIPIENT = "dmh4681@gmail.com"

# Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# User input
username = "DigitalNomad"
selected_path = "physical_optimization"

# Build message dynamically
system_prompt = "You are a motivational coach aligned with the Sovereign Path philosophy."
user_prompt = f"""
Write a welcome email for a new user named {username}, who has selected the "{selected_path.replace("_", " ").title()}" path. 
Make it inspirational and styled entirely in Dylan’s sovereign tone — powerful, direct, and designed to ignite momentum.
"""

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_prompt}
]

# Call OpenAI
response = client.chat.completions.create(
    model="gpt-4",
    messages=messages
)

email_body = response.choices[0].message.content

# Send email via Mailgun
res = requests.post(
    f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
    auth=("api", MAILGUN_API_KEY),
    data={
        "from": SENDER,
        "to": RECIPIENT,
        "subject": f"Welcome to the Sovereignty Score, {username}!",
        "text": email_body
    }
)

print(f"✅ Email sent! Status: {res.status_code}")
print(res.text)
print(email_body)
