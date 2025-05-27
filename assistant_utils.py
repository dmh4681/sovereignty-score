# assistant_utils.py or inline
import time
from openai import OpenAI

def call_openai_assistant(api_key, assistant_id, user_input):
    client = OpenAI(api_key=api_key)
    thread = client.beta.threads.create()
    
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_input
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id
    )

    while True:
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        if run.status == "completed":
            break
        time.sleep(1)

    messages = client.beta.threads.messages.list(thread_id=thread.id)
    latest = messages.data[0].content[0].text.value
    return latest
