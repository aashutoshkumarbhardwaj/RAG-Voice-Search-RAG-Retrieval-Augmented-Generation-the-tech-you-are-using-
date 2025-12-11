import requests
import base64

# REPLACE THIS WITH YOUR ACTUAL KEY
API_KEY = "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"

invoke_url = "https://grpc.nvcf.nvidia.com/v2/nvcf/pexec/functions/877104f7-e885-42b9-8de8-f6e4c6303969"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

payload = {
    "text": "Hello, this is a test of the NVIDIA audio system.",
    "language_code": "en-US",
    "voice_name": "English-US.Female-1",
    "sample_rate_hz": "44100"
}

print("Testing NVIDIA TTS...")
response = requests.post(invoke_url, headers=headers, json=payload)

print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    print("SUCCESS! Audio generated.")
    # Try to save it to see if it works
    with open("test_audio.mp3", "wb") as f:
        # Check if it's JSON with base64 or raw bytes
        if "application/json" in response.headers.get("Content-Type", ""):
            data = response.json()
            # Handle different JSON structures
            audio_data = data.get("audioContent") or data.get("audio") or ""
            if audio_data:
                f.write(base64.b64decode(audio_data))
                print("Saved as test_audio.mp3")
            else:
                print("JSON received but no audio key found:", data.keys())
        else:
            f.write(response.content)
            print("Saved as test_audio.mp3 (Raw)")
else:
    print("FAILURE.")
    print(response.text)