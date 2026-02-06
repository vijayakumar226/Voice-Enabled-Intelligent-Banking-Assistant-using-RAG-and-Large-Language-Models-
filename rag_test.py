import os
import sys
import warnings
import contextlib

# ---------- SILENCE EVERYTHING BEFORE IMPORTING MODELS ----------
warnings.filterwarnings("ignore")

# Disable HF/Transformers noise
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# A helper to silence prints from libraries (stdout + stderr)
@contextlib.contextmanager
def silence_output():
    with open(os.devnull, "w") as devnull:
        with contextlib.redirect_stdout(devnull), contextlib.redirect_stderr(devnull):
            yield

# Import heavy libs inside silence to avoid their startup logs
with silence_output():
    import faiss
    from sentence_transformers import SentenceTransformer
    from huggingface_hub import InferenceClient

# ---------- LOAD DATA ----------
with open("bank_data.txt", "r", encoding="utf-8") as f:
    docs = [line.strip() for line in f if line.strip()]

if not docs:
    print("bank_data.txt is empty.")
    sys.exit(1)

# ---------- BUILD EMBEDDINGS + FAISS (silenced) ----------
with silence_output():
    embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    doc_vecs = embed_model.encode(docs).astype("float32")

    faiss.normalize_L2(doc_vecs)
    dim = doc_vecs.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(doc_vecs)

# ---------- HF CLIENT ----------
hf_token = os.getenv("HF_TOKEN")
if not hf_token:
    print("HF_TOKEN not found. Set it with: setx HF_TOKEN \"your_token\" then restart VS Code/terminal.")
    sys.exit(1)

client = InferenceClient(token=hf_token)
model_name = "meta-llama/Meta-Llama-3-8B-Instruct"

# Tune for strictness
SIMILARITY_THRESHOLD = 0.55

# ---------- CHAT LOOP ----------
while True:
    query = input("Ask a question (type 'exit' to stop): ").strip()
    if query.lower() == "exit":
        break
    if not query:
        continue

    # Retrieve (silenced)
    with silence_output():
        q_vec = embed_model.encode([query]).astype("float32")
        faiss.normalize_L2(q_vec)
        scores, ids = index.search(q_vec, k=1)

    best_score = float(scores[0][0])
    best_id = int(ids[0][0])

    if best_id < 0 or best_score < SIMILARITY_THRESHOLD:
        print("Answer: I don't know from the given data.\n")
        continue

    context = docs[best_id]

    prompt = f"""Answer ONLY using the context. If not in context, say: "I don't know from the given data."

Context:
{context}

Question: {query}
Answer:
"""

    # LLaMA call (silenced)
    with silence_output():
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "Answer only using the provided context. Do not guess."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=120,
        )

    answer = response.choices[0].message["content"].strip()
    print(f"Answer: {answer}\n")
