import pandas as pd
import faiss
import numpy as np
from openai import OpenAI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles  # <--- NEW IMPORT
from pydantic import BaseModel
import requests  # <--- NEW IMPORT (Make sure to run: pip install requests)
import uuid
import os
from fastapi.responses import FileResponse
# ==========================================

# ======================
# LOAD DATA
# ======================
CSV_PATH = "data.csv"
if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(f"ERROR: '{CSV_PATH}' not found.")

df = pd.read_csv(CSV_PATH)
df["text_representation"] = df.apply(
    lambda row: f"{row['Author\'s Name']} - {row['Title']} - {row['Publisher / Place']} - {row['Year']}", 
    axis=1
)

# ======================
# CONFIGURATION
# ======================
# Using the same key for everything
API_KEY = "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" 

client = OpenAI(
    api_key=API_KEY,
    base_url="https://integrate.api.nvidia.com/v1"
)

# ======================
# BUILD INDEX
# ======================
print("Generating embeddings... (This happens only once)")
embeddings = []
for text in df["text_representation"].tolist():
    response = client.embeddings.create(
        model="nvidia/nv-embedqa-e5-v5",
        input=text,
        extra_body={"input_type": "query"}
    )
    embeddings.append(response.data[0].embedding)

embedding_array = np.array(embeddings).astype("float32")
index = faiss.IndexFlatL2(embedding_array.shape[1])
index.add(embedding_array)
metadata = df["text_representation"].tolist()
print("Ready.")

# ======================
# FASTAPI SETUP
# ======================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. CREATE A FOLDER FOR AUDIO
os.makedirs("generated_audio", exist_ok=True)

# 2. MOUNT THE FOLDER SO THE FRONTEND CAN ACCESS IT
# This makes files in 'generated_audio' accessible at 'http://.../audio/filename.wav'
app.mount("/audio", StaticFiles(directory="generated_audio"), name="audio")

class QueryItem(BaseModel):
    query: str

@app.get("/") 
async def read_index():
    return FileResponse("index.html")

@app.post("/process")
def process(query_data: QueryItem):
    query = query_data.query
    print(f"Incoming Query: {query}")
    

    # --- SEARCH ---
    query_response = client.embeddings.create(
        model="nvidia/nv-embedqa-e5-v5",
        input=query,
        extra_body={"input_type": "query"}
    )
    q_emb = np.array([query_response.data[0].embedding]).astype("float32")
    distances, indices = index.search(q_emb, 2)
    results = [metadata[i] for i in indices[0]]

    # --- TEXT GENERATION ---
    summary_text = "Hello VIPS Trainees, I found these books for you: " + ". ".join(results)

    # --- TTS (DIRECT API CALL - NO SUBPROCESS) ---
    function_id = "877104f7-e885-42b9-8de8-f6e4c6303969"
    invoke_url = f"https://grpc.nvcf.nvidia.com/v2/nvcf/pexec/functions/{function_id}"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "function-id": function_id,  # This is required by the pexec endpoint
    }
    
    # Simplified payload. Let the model use its default sample rate.
    payload = {
        "text": summary_text,
        "language_code": "en-US",
        "voice_name": "English-US.Female-1", 
    }

    print("Generating Audio via API...")
    final_audio_url = None
    file_id = str(uuid.uuid4())
    filename = f"{file_id}.mp3" # The model produces MP3 audio
    filepath = f"generated_audio/{filename}"

    try:
        response = requests.post(invoke_url, headers=headers, json=payload, timeout=20)
        response.raise_for_status() # This will raise an exception for HTTP error codes (4xx or 5xx)

        # The API returns a JSON object with the audio data encoded in Base64.
        data = response.json()
        audio_content = data.get("audioContent")

        if audio_content:
            # Decode the Base64 string and save it as a binary file.
            with open(filepath, "wb") as f:
                f.write(base64.b64decode(audio_content))
            print(f"SUCCESS: Audio decoded and saved to {filepath}")
            final_audio_url = f"http://127.0.0.1:8000/audio/{filename}"
        else:
            print("ERROR: JSON response received, but 'audioContent' key was missing or empty.")
            print("Response Data:", data)

    except requests.exceptions.RequestException as e:
        # This provides more detailed error info for 4xx/5xx errors
        print("\n!!! NVIDIA TTS API ERROR !!!")
        if e.response is not None:
            print(f"Status Code: {e.response.status_code}")
            print(f"Details: {e.response.text}")
        else:
            print(f"Request Exception: {e}")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")

    # --- RETURN URL TO FRONTEND ---
    return {
        "results": results, 
        "audio_url": final_audio_url
    }