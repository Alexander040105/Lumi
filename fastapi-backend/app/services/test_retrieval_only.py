import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "fastapi-backend"))

from app.services import rag_pipeline

rag_pipeline.ensure_index_built()

queries = [
    "How much would solar installation cost for this municipality?",
    "Which renewable source is cheaper?",
    "How much does a small hydro system usually require?",
    "Compare solar vs wind vs hydro costs.",
    "What equipment is needed for a wind system?",
    "Solar panel price range",
    "Hydro turbine equipment cost",
]

for q in queries:
    print(f"\n=== {q} ===")
    results = rag_pipeline.retrieve_context(q, top_k=3)
    for i, r in enumerate(results, 1):
        score = r["score"]
        rtype = r.get("renewable_type", "?")
        cat = r.get("category", "?")
        text = r["text"][:180].replace("\n", " ")
        print(f"  {i}. [score={score}] [{rtype}/{cat}] {text}...")
