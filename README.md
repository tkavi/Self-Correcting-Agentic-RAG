# Self-Correcting-Agentic-RAG

The objective of this project is to build an intelligent Retrieval-Augmented Generation (RAG) assistant capable of answering questions based on the ingested source. <br>

Standard RAG systems fail when users provide vague inputs or when the vector database returns irrelevant text. This system implements an Agentic Loop Framework using LangGraph. It acts as a smart state machine that dynamically intercepts poor user inputs before searching, and automatically critiques and rewrites search queries after searching if the data found is insufficient.

<img width="426" height="531" alt="image" src="https://github.com/user-attachments/assets/d2362f6e-74c3-4329-aa38-7de576a623fd" />

