# Self-Correcting-Agentic-RAG
Intelligent RAG assistant capable of answering complex medical compliance questions 

**Local Environment Setup**
1. Install Ollama -> to run LLMs locally <br>
   https://ollama.com/download/windows

2. Open VSCode only after installing Ollama so VSCode can recognize Ollama

3. Create a new project directory in VS Code and run below commands in Terminal
   1. Create the virtual environment <br>
      python -m venv venv

   2. Activate it (Windows PowerShell) <br> 
	.\venv\Scripts\Activate.ps1

   3. Run below if this error (cannot be loaded because running scripts is disabled on this system) and try again <br>
	Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
	
   4. Install required ollama libraries <br>
	ollama pull llama3.1 (for complex reasoning and answering) <br>
	ollama pull phi3 (for fast rephrasing and safety checks) <br>
	ollama pull nomic-embed-text (embedding model) <br>

   5. Test that Ollama is awake and responsive <br>
	ollama list

   6. Install required python libraries <br> 
	pip install langgraph langchain_ollama langchain_community chromadb

	_langgraph_: Orchestrates the stateful graph, handling loops and conditional routing <br>
	_langchain-ollama_: Connects graph nodes directly to our local Ollama models (Llama 3.1 and Phi-3) for both text generation and vector embeddings <br>
	_langchain-community_: Provides helpful, pre-built utility integrations to load, split, and manage raw text documents before sending them to Chroma <br>
	_chromadb_: Acts as local embedded vector database to store and query document context without cloud dependencies <br>

   7. Install relevant guardrails library <br> 
	pip install guardrails-ai <br>
	guardrails hub install hub://guardrails/toxic_language <br>

   8. requirements.txt <br> 
	pip freeze > requirements.txt <br>
	
	This file lists all the external packages project depends on. If this project moved to another computer or uploaded to GitHub, anyone can recreate the exact environment with a single command instead of guessing what to install.

   9. dotenv file <br>
	New-Item -Path .env -ItemType File <br>
	pip install python-dotenv (to access this .env file inside code) <br>
	
	Since this is a entirely local project running on Ollama, we don't have secret API keys (like OpenAI keys) to hide right now. However, a .env file is still incredibly useful for defining configuration variables like local model names or database paths. If we decide to switch from a local model to an enterprise cloud model later, we only have to change it in this one file instead of hunting through the code.
    
	10. To test using real pdf <br>
		pip install pypdf

**Project Setup** <br>
In workspace, create 3 blank Python files: <br>
- state.py (to define the data structure that moves through nodes)
- nodes.py (to write the logic for guardrails, rephrasing, and ChromaDB retrieval)
- main.py (to orchestrate the LangGraph workflow and run the input() loop)


**Flow of pipeline:**
1. user_query
2. guardrails_toxic_language check <br> 
		approved - move forward <br> 
		not approved - stop the flow <br>
3. vague query -> followup 
4. right query -> fetch the response from vector db <br> 
		if relevant -> reverify using evals -> generate response <br>
		not relevant -> rephrase the query -> right query <br>

<img width="426" height="531" alt="image" src="https://github.com/user-attachments/assets/d2362f6e-74c3-4329-aa38-7de576a623fd" />

 
 _guardrails_ai_: https://guardrailsai.com/hub/validator/guardrails/toxic_language

**Git Setup** <br>
create .gitignore and add all unwanted files and folders <br>
git init <br>
git add . <br>
git commit -m "project structure and RAG architecture setup" <br>
git branch -M main <br>
git remote add origin https://github.com/tkavi/Self-Correcting-Agentic-RAG.git <br>
git pull origin main --allow-unrelated-histories (if repo created already) <br>
git push origin main <br>
