import os
import sys

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

from common import client, CHAT_MODEL, EMBED_MODEL

search = SearchClient(
    os.environ["AZURE_SEARCH_ENDPOINT"],
    os.environ["AZURE_SEARCH_INDEX"],
    AzureKeyCredential(os.environ["AZURE_SEARCH_KEY"]),
)


def retrieve(question, k=3):
    vec = client.embeddings.create(model=EMBED_MODEL, input=question).data[0].embedding
    results = search.search(
        search_text=question,
        vector_queries=[VectorizedQuery(vector=vec, k_nearest_neighbors=k, fields="embedding")],
        top=k,
    )
    return [({"source": r["source"], "text": r["text"]}, r["@search.score"]) for r in results]


def answer(question):
    hits = retrieve(question)
    context = "\n\n".join(f"[{r['source']}]\n{r['text']}" for r, _ in hits)
    prompt = (
        "You answer questions about health plan policies using ONLY the sources below.\n"
        "Cite the source file name in square brackets after each fact, for example [physical_therapy.md].\n"
        "If the sources do not contain the answer, say you do not have that information. "
        "Answer only what was asked; do not list topics the sources do not cover.\n\n"
        f"SOURCES:\n{context}\n\nQUESTION: {question}"
    )
    resp = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_completion_tokens=4000,
    )
    return resp.choices[0].message.content, hits


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "Is physical therapy covered and what is the limit?"
    text, hits = answer(question)
    print("\nANSWER:\n" + text)
    print("\nRETRIEVED (Azure AI Search):")
    for r, score in hits:
        print(f"  {r['source']} (score {score:.3f})")