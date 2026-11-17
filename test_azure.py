import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

endpoint = os.environ["AZURE_OPENAI_ENDPOINT"].rstrip("/")
client = OpenAI(
    base_url=f"{endpoint}/openai/v1/",
    api_key=os.environ["AZURE_OPENAI_KEY"],
)

chat = client.chat.completions.create(
    model=os.environ["CHAT_DEPLOYMENT"],
    messages=[{"role": "user", "content": "Reply with exactly: chat works"}],
    max_completion_tokens=200,
)
print("CHAT:", chat.choices[0].message.content)

emb = client.embeddings.create(
    model=os.environ["EMBED_DEPLOYMENT"],
    input="Physical therapy is covered up to 20 visits per year.",
)
print("EMBEDDING length:", len(emb.data[0].embedding))