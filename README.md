%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#ffffff', 'edgeLabelBackground':'#ffffff', 'tertiaryColor': '#f4f4f4'}}}%%
graph TD
    A[🧑‍💻 User Types Topic] -->|Search Query| B(🧠 AI Embeddings Search);
    B -->|Find relevant books| C{📚 Book Results Found};
    C -->|Summarized Text| D[🤖 NVIDIA NIMs TTS];
    D -->|Generates Audio| E[🔊 Speaker Plays Audio & Text Shown];

    style A fill:#fff,stroke:#333,stroke-width:2px,stroke-dasharray: 5 5
    style B fill:#fff,stroke:#333,stroke-width:2px,stroke-dasharray: 5 5
    style D fill:#eefaee,stroke:#333,stroke-width:4px
    style E fill:#fff,stroke:#333,stroke-width:2px,stroke-dasharray: 5 5
