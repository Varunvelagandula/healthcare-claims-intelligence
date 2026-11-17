import json
import re
import time
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from agent import run_agent

app = FastAPI(title="Healthcare Claims Copilot")


class Question(BaseModel):
    question: str


def mask_pii(text: str) -> str:
    """Light PII masking for logs: emails, SSN-like and phone-like numbers."""
    text = re.sub(r"[\w.+-]+@[\w-]+\.[\w.]+", "[EMAIL]", text)
    text = re.sub(r"\b\d{3}[-.\s]?\d{2}[-.\s]?\d{4}\b", "[SSN]", text)
    text = re.sub(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b", "[PHONE]", text)
    return text


def audit(entry: dict):
    entry["time"] = datetime.now(timezone.utc).isoformat()
    with open("audit_log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask")
def ask(body: Question):
    q = body.question.strip()
    if not q:
        raise HTTPException(status_code=400, detail="Question is empty.")
    if len(q) > 500:
        raise HTTPException(status_code=400, detail="Question is too long (max 500 characters).")
    start = time.time()
    try:
        label, answer = run_agent(q)
    except Exception as e:
        audit({"question": mask_pii(q), "status": "error", "error": str(e)[:200]})
        raise HTTPException(status_code=500, detail="Something went wrong. Please try again.")
    seconds = round(time.time() - start, 1)
    audit({"question": mask_pii(q), "route": label, "status": "ok", "seconds": seconds})
    return {"route": label, "answer": answer, "seconds": seconds}


PAGE = """<!doctype html>
<html><head><meta charset="utf-8"><title>Claims Copilot</title>
<style>
body{font-family:Segoe UI,Arial,sans-serif;max-width:820px;margin:2rem auto;padding:0 1rem;color:#222}
h1{font-size:1.4rem} .note{color:#666;font-size:.85rem}
textarea{width:100%;height:70px;padding:8px;font-size:1rem;box-sizing:border-box}
button{padding:8px 18px;font-size:1rem;margin-top:8px;cursor:pointer}
.card{border:1px solid #ddd;border-radius:8px;padding:12px;margin-top:14px;white-space:pre-wrap}
.q{background:#f3f6ff;font-weight:600}
</style></head><body>
<h1>Healthcare Claims Copilot</h1>
<p class="note">Synthetic data only. Ask about plan policies or aggregate claims numbers.</p>
<textarea id="q" placeholder="e.g. Which diagnosis had the highest total claim cost?"></textarea><br>
<button id="go">Ask</button>
<div id="out"></div>
<script>
const out = document.getElementById("out");
function card(text, cls){
  const d = document.createElement("div");
  d.className = "card " + (cls || "");
  d.textContent = text;
  out.prepend(d);
  return d;
}
document.getElementById("go").onclick = async () => {
  const q = document.getElementById("q").value.trim();
  if(!q) return;
  const waiting = card("Thinking...", "");
  card(q, "q");
  try{
    const r = await fetch("/ask", {method:"POST", headers:{"Content-Type":"application/json"},
                                   body: JSON.stringify({question:q})});
    const j = await r.json();
    waiting.textContent = r.ok ? "[" + j.route + ", " + j.seconds + "s]\\n\\n" + j.answer : "Error: " + j.detail;
  }catch(e){ waiting.textContent = "Could not reach the server."; }
};
</script></body></html>"""


@app.get("/", response_class=HTMLResponse)
def home():
    return PAGE