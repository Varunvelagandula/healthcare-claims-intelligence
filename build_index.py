import glob
import json
import os

from common import client, EMBED_MODEL


def chunk_text(text, max_chars=500):
    """Split a document into chunks, keeping the title line at the top of each chunk."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    title = lines[0]
    chunks, current = [], title
    for line in lines[1:]:
        if len(current) + len(line) > max_chars:
            chunks.append(current)
            current = title
        current += "\n" + line
    chunks.append(current)
    return chunks


records = []
for path in sorted(glob.glob("policy_docs/*.md")):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    source = os.path.basename(path)
    for i, chunk in enumerate(chunk_text(text)):
        records.append({"source": source, "chunk_id": i, "text": chunk})

print(f"{len(records)} chunks from policy_docs")

response = client.embeddings.create(model=EMBED_MODEL, input=[r["text"] for r in records])
for r, item in zip(records, response.data):
    r["embedding"] = item.embedding

with open("index.json", "w", encoding="utf-8") as f:
    json.dump(records, f)
print("saved index.json")