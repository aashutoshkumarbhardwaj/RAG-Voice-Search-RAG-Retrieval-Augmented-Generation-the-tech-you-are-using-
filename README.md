graph TD
    user(👤 User Input) -->|Search Topic| brain[🧠 AI Search FAISS];
    brain -->|Top Results| text[📄 Summary Text];
    text -->|Send to NVIDIA| voice{🤖 NVIDIA TTS};
    voice -->|Returns MP3| speaker[🔊 Audio Output];

    style user fill:#fff,stroke:#333,stroke-width:2px
    style brain fill:#fff,stroke:#333,stroke-width:2px
    style voice fill:#e6fffa,stroke:#00b894,stroke-width:4px
    style speaker fill:#fff,stroke:#333,stroke-width:2px,stroke-dasharray: 5 5
