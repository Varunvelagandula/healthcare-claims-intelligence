import json
import sys

import numpy as np

from common import client, CHAT_MODEL, EMBED_MODEL

with open("index.json", encoding="utf-8") as f:
    records = json.load(f)
matrix = np.array([r["embedding"] for r in records])
matrix = matrix / np.linalg.norm(matrix, axis=1, keepdims=True)


def retrieve(question, k=3):
    q = client.embeddings.create(model=EMBED_MODEL, input=question).data[0].embedding
    q = np.array(q) / np.linalg.norm(q)
    scores = matrix @ q
    top = np.argsort(scores)[::-1][:k]
    return [(records[i], float(scores[i])) for i in top]


def answer(question):
    hits = retrieve(question)
    context = "\n\n".join(f"[{r['source']}]\n{r['text']}" for r, _ in hits)
    prompt = (
        "You answer questions about health plan policies using ONLY the sources below.\n"
        "Cite the source file name in square brackets after each fact, for example [physical_therapy.md].\n"
        "If the sources do not contain the answer, say you do not have that information.\n\n"
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
    print("\nRETRIEVED:")
    for r, score in hits:
        print(f"  {r['source']} (score {score:.2f})")