# Self-Correcting-Agentic-RAG
Intelligent RAG assistant capable of answering complex medical compliance questions 

**Local Environment Setup**
1. Install Ollama -> to run LLMs locally

2. Open VSCode only after installing Ollama so VSCode can recognize Ollama

3. Create a new project directory in VS Code and run below commands in Terminal
   1. Create the virtual environment
	python -m venv venv

   2. Activate it (Windows PowerShell)
	.\venv\Scripts\Activate.ps1

    Run below if this error (cannot be loaded because running scripts is disabled on this system) and try again
	Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
	
   3. Install required ollama libraries
	ollama pull llama3.1 (for complex reasoning and answering)
	ollama pull phi3 (for fast rephrasing and safety checks)
	ollama pull nomic-embed-text (embedding model)

   4. Test that Ollama is awake and responsive
	ollama list

   5. Install required python libraries
	pip install langgraph langchain_ollama langchain_community chromadb

	langgraph: Orchestrates the stateful graph, handling loops and conditional routing.  
	langchain-ollama: Connects graph nodes directly to our local Ollama models (Llama 3.1 and Phi-3) for both text generation and vector embeddings.
	langchain-community: Provides helpful, pre-built utility integrations to load, split, and manage raw text documents before sending them to Chroma.
	chromadb: Acts as local embedded vector database to store and query document context without cloud dependencies.

   6. Install relevant guardrails library
	pip install guardrails-ai
	guardrails hub install hub://guardrails/toxic_language

   7. requirements.txt
	pip freeze > requirements.txt
	
	This file lists all the external packages project depends on. If this project moved to another computer or uploaded to GitHub, anyone can recreate the exact environment with a single command instead of guessing what to install.

   8. dotenv file
	New-Item -Path .env -ItemType File
	pip install python-dotenv (to access this .env file inside code)
	
	Since this is a entirely local project running on Ollama, we don't have secret API keys (like OpenAI keys) to hide right now. However, a .env file is still incredibly useful for defining configuration variables like local model names or database paths. If we decide to switch from a local model to an enterprise cloud model later, we only have to change it in this one file instead of hunting through the code.

**Project Setup**
In workspace, create 3 blank Python files: 
	- state.py (to define the data structure that moves through nodes)
	- nodes.py (to write the logic for guardrails, rephrasing, and ChromaDB retrieval)
	- main.py (to orchestrate the LangGraph workflow and run the input() loop)


**Flow of pipeline:**
1. user_query
2. guardrails_toxic_language check 
		approved - move forward 
		not approved - stop the flow 
3. vague query -> followup 
4. right query -> fetch the response from vector db 
		if relevant -> reverify using evals -> generate response
		not relevant -> rephrase the query -> right query

<img width="1206" height="550" alt="image" src="https://github.com/user-attachments/assets/d5b96ad4-861f-4531-ac06-63188b139e2c" />
 
 guardrails_ai: https://guardrailsai.com/hub/validator/guardrails/toxic_language

To test using real pdf: pip install pypdf

**Git Setup **
create .gitignore and add all unwanted files and folders
git init
git add .
git commit -m "project structure and RAG architecture setup"
git branch -M main
git remote add origin https://github.com/tkavi/Self-Correcting-Agentic-RAG.git
git pull origin main --allow-unrelated-histories (if repo created already)
git push origin main
