import os
import time
import warnings
import numpy as np
import faiss
import sounddevice as sd
from scipy.io.wavfile import write

import whisper
import pyttsx3
from sentence_transformers import SentenceTransformer
from huggingface_hub import InferenceClient

warnings.filterwarnings("ignore")
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# ---------- SETTINGS ----------
DATA_FILE = "bank_data_large.txt"   # use big dataset
MODEL_NAME = "meta-llama/Meta-Llama-3-8B-Instruct"
SIMILARITY_THRESHOLD = 0.55         # stricter = safer
TOP_K = 1                           # prevent unrelated context
RECORD_SECONDS = 5                  # adjust based on your speaking speed
SAMPLE_RATE = 16000

# ---------- CHECK TOKEN ----------
hf_token = os.getenv("HF_TOKEN")
if not hf_token:
    raise RuntimeError("HF_TOKEN not found. Set it and restart terminal/VS Code.")

client = InferenceClient(token=hf_token)

# ---------- LOAD DATA ----------
with open(DATA_FILE, "r", encoding="utf-8") as f:
    docs = [line.strip() for line in f if line.strip()]
if not docs:
    raise RuntimeError(f"{DATA_FILE} is empty.")

# ---------- EMBEDDINGS + FAISS (cosine) ----------
embed_model = SentenceTransformer("all-MiniLM-L6-v2")
doc_vecs = embed_model.encode(docs).astype("float32")
faiss.normalize_L2(doc_vecs)
dim = doc_vecs.shape[1]
index = faiss.IndexFlatIP(dim)
index.add(doc_vecs)

# ---------- WHISPER + TTS ----------
stt_model = whisper.load_model("base")  # small + good CPU
tts = pyttsx3.init()
tts.setProperty("rate", 175)

def speak(text: str):
    tts.say(text)
    tts.runAndWait()

def record_audio(filename="query.wav", seconds=RECORD_SECONDS):
    print(f"\n🎙️ Speak now... ({seconds}s)")
    audio = sd.rec(int(seconds * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype=np.int16)
    sd.wait()
    write(filename, SAMPLE_RATE, audio)
    return filename

def transcribe(filename="query.wav") -> str:
    result = stt_model.transcribe(filename)
    return (result.get("text") or "").strip()

def retrieve_context(query: str):
    q_vec = embed_model.encode([query]).astype("float32")
    faiss.normalize_L2(q_vec)
    scores, ids = index.search(q_vec, k=TOP_K)
    best_score = float(scores[0][0])
    best_id = int(ids[0][0])

    if best_id < 0 or best_score < SIMILARITY_THRESHOLD:
        return None, best_score
    return docs[best_id], best_score

def answer_with_llama(query: str, context: str) -> str:
    prompt = f"""You are a banking assistant.
Answer ONLY using the context. If the answer is not in the context, say: "I don't know from the given data."

Context:
{context}

Question: {query}
Answer:
"""
    resp = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "Answer only using the provided context. Do not guess."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=140,
    )
    return resp.choices[0].message["content"].strip()

print("✅ Voice Bank RAG Chatbot Ready")
print("Say 'exit' to stop.\n")

while True:
    wav = record_audio()
    query = transcribe(wav)

    if not query:
        print("❗ I didn't catch that. Try again.")
        speak("I didn't catch that. Please repeat.")
        continue

    print("🗣️ You said:", query)

    if query.lower().strip() == "exit":
        speak("Bye!")
        break

    context, score = retrieve_context(query)
    if context is None:
        print("Answer: I don't know from the given data.")
        speak("I don't know from the given data.")
        continue

    answer = answer_with_llama(query, context)
    print("Answer:", answer)
    speak(answer)
