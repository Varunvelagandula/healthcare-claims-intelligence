import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url=os.environ["AZURE_OPENAI_ENDPOINT"].rstrip("/") + "/openai/v1/",
    api_key=os.environ["AZURE_OPENAI_KEY"],
)
CHAT_MODEL = os.environ["CHAT_DEPLOYMENT"]
EMBED_MODEL = os.environ["EMBED_DEPLOYMENT"]