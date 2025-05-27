import os
import time
import sys
import requests
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
SENDER = f"Sovereignty Score <mailgun@{MAILGUN_DOMAIN}>"

# Get command line arguments
if len(sys.argv) != 4:
    print("Usage: python AI_Assist_Welcome.py <username> <email> <path>")
    sys.exit(1)

username = sys.argv[1]
email = sys.argv[2]
selected_path = sys.argv[3]

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)
ASSISTANT_ID = "asst_x36oxhsulPDwZPYOD2Ohi0O3"

# Step 1: Create a thread and send message to Assistant
thread = client.beta.threads.create()

client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=f"My username is {username}, and I selected the {selected_path} path. Please send me the welcome email."
)

run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=ASSISTANT_ID
)

# Wait for response
while True:
    run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
    if run.status == "completed":
        break
    time.sleep(1)

# Retrieve final message
messages = client.beta.threads.messages.list(thread_id=thread.id)
latest = messages.data[0].content[0].text.value

# Step 2: Send the email via Mailgun
response = requests.post(
    f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
    auth=("api", MAILGUN_API_KEY),
    data={
        "from": SENDER,
        "to": email,
        "subject": f"Welcome to the Sovereignty Score, {username}!",
        "text": latest,
        "h:Reply-To": SENDER,
        "h:List-Unsubscribe": f"<mailto:unsubscribe@{MAILGUN_DOMAIN}>",
        "v:username": username,
        "v:path": selected_path,
        "o:tracking": "yes",
        "o:tracking-clicks": "yes",
        "o:tracking-opens": "yes",
        "o:require-tls": "yes",
        "o:skip-verification": "no"
    }
)

# Return results
print(f"Email sent to {email}")
print(f"Status code: {response.status_code}")
print(f"Preview of email content:\n{latest[:400]}")
