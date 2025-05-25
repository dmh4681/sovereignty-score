import os
import time
from dotenv import load_dotenv
from openai import OpenAI

# Load API key from .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# Assistant ID
ASSISTANT_ID = "asst_x36oxhsulPDwZPYOD2Ohi0O3"  # Replace with yours if different

# User inputs
username = "DigitalNomad"
selected_path = "planetary_stewardship"

# Create a thread
thread = client.beta.threads.create()

# Add a message to the thread
client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=f"My username is {username}, and I selected the {selected_path} path. Please send me the welcome email."
)

# Run the assistant
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=ASSISTANT_ID,
)

# Wait for completion
while True:
    run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
    if run.status == "completed":
        break
    time.sleep(1)

# Get the assistant's response
messages = client.beta.threads.messages.list(thread_id=thread.id)
latest = messages.data[0].content[0].text.value

print("=== Assistant Response ===\n")
print(latest)
