# to load env variables
from dotenv import load_dotenv
import os

from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_community.vectorstores import Chroma
from langchain_core.messages import SystemMessage, HumanMessage

# from guardrails.hub import ToxicLanguage
# from guardrails import Guard

from llm_guard import scan_prompt
from llm_guard.input_scanners import Toxicity, PromptInjection
from llm_guard.input_scanners.toxicity import MatchType

# Internal files
from state import State as state_class

# loading env varibles
load_dotenv()

llm_model = os.getenv("LLM_MODEL")
# to set a default value
if llm_model is None:
    llm_model = "llama3.1"

# default values set in-line
embedding_model = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
vector_db_path = os.getenv("VECTOR_DB_PATH", "./chroma_db")

# Initializing the model and connecting to DB
llm = ChatOllama(model = llm_model, temperature=0)
embedding = OllamaEmbeddings(model = embedding_model)
vector_db = Chroma(persist_directory = vector_db_path, embedding_function = embedding, collection_name = "rag_collection")


# --------------- GUARDRAILS NODE ------------------ #
def guardrails_node(state : state_class) -> dict: 
    
    user_query = state.get("user_query","")

    # Initializing the scanner 
    scanners = [
        Toxicity(threshold=0.5, match_type=MatchType.SENTENCE)
        # PromptInjection(threshold=0.6)
    ]

    # Scanning the text locally
    sanitized_prompt, results_valid, results_score = scan_prompt(scanners, user_query)
    
    try:
        # Flag if any scanner marks it as toxic
        if not all(results_valid.values()):
            print(f"Toxic content detected!")
            return {
                "is_offensive": True,
                "is_vague": False,
                "final_response" : "Request flagged. Try Again!"
            }

        # To check if the query is vague
        system_instruction = (
            "You are a linguistic analyzer auditing inputs for a medical compliance database.\n"
            "Determine if the user query is too vague, short, or casual to yield a successful database search.\n"
            "A query is vague if it lacks specific nouns, acronyms, or regulation names (e.g., 'how fast do they answer back?' is vague because it doesn't specify who 'they' are).\n\n"
            "Reply with exactly 'True' if the query is vague or 'False' if query is not vague.\n"
        )

        user_instruction = f"Analyze this query : '{user_query}'"

        response = llm.invoke(
            [
                SystemMessage(content=system_instruction),
                HumanMessage(content=user_instruction)
            ]
        )

        is_vague = 'true' in response.content.lower()

        print("NODE -> Guardrails")
        print(f"-- Is Offensive : {state.get("is_offensive")}")
        print(f"-- Is Vague : {is_vague}")

        return {
            "is_offensive": False,
            "is_vague": is_vague
        }
    
    except Exception as e:
        return {
            "is_offensive": True,
            "final_response" : f"Error in Guardrails node: {e}"
        }

    # #---------GUARDRAILS_AI (installation errors)----------------------------------------------
    # # Use the Guard with the validator
    # guard = Guard().use(
    #     ToxicLanguage, threshold=0.5, validation_method="sentence", on_fail="exception"
    # )

    # user_query = state_class["user_query"]

    # try:      
    #     # Validating the user query
    #     guard.validate(user_query)
    #     print("query passed for rephrasing")
    #     return {"is_offensive": False}
    
    # except Exception as e:
    #     print(f"Offensive Language detected, Try Again!")
    #     return {"is_offensive": True}
    # #-------------------------------------------------------


# --------------- RETRIEVE NODE ------------------ #
def retrieve_node(state : state_class) -> dict:
    print("NODE -> Retrieve")
    # using rephrased query if exist
    user_query = state.get("user_query")

    # fetching top 3 semantic searches
    chunks = vector_db.similarity_search(user_query,k=3)

    # list of the actual string of texts to be processed
    chunks_content = [chunk.page_content for chunk in chunks]
    print(f"-- Top 3 Chunks retrieved")
    return {"relevant_chunks":chunks_content}


# --------------- EVALS NODE ------------------ #
def evals_node(state : state_class) -> dict:
    print("NODE -> Evaluate")

    user_query = state.get("user_query")
    chunks = state.get("relevant_chunks",[])

    if not chunks:
        print("No chunks found in db")
        return {"is_relevant":False}
    
    # flatten list to single text block
    text_block = "\n\n".join(chunks)

    system_instruction = (
        "You are an expert compliance auditor grading a RAG data pipeline.\n"
        "Your sole task is to determine if the retrieved document context contains "
        "the specific facts, rules, or data needed to fully answer the user's query.\n"
        "Analyze the connection deeply. Reply with exactly 'True' or 'False'."
    )
    
    user_instruction = f"Context:\n{text_block}\n\nQuery:{user_query}"

    response = llm.invoke(
        [
        SystemMessage(content=system_instruction),
        HumanMessage(content=user_instruction)
    ]
    )

    is_relevant = 'true' in response.content.lower()

    print(f"-- Is Relevant : {is_relevant}")

    return {"is_relevant":is_relevant}


# --------------- GENERATE NODE ------------------ #
def generate_node(state : state_class) -> dict:
    print("NODE -> Generate")

    user_query = state.get("user_query")
    chunks = state.get("relevant_chunks")

    text_block = "\n\n".join(chunks)

    system_instruction = ("You are a helpful assistant.\n"
        "Answer the user query using ONLY the provided context.\n"
        "If the context doesn't help, say you don't know."
    )

    user_instruction = f"Context:\n{text_block}\n\nQuery:{user_query}"

    response = llm.invoke(
        [
            SystemMessage(content=system_instruction),
            HumanMessage(content=user_instruction)
        ]
    )

    print(f"-- Final response is below ")

    return {"final_response":response.content}


# --------------- REPHRASE NODE ------------------ #
def rephrase_node(state : state_class) -> dict:

    print("NODE -> Rephrase")

    # current state var
    current_loop = state.get("loop_count",0)
    user_query = state["user_query"]

    system_instruction = (
        "You are an expert query optimization engine for a medical compliance RAG system.\n"
        "Your job is to take a vague, conversational user query and rewrite it into a "
        "highly specific, formal search phrase containing precise keywords found in the "
        "CMS Interoperability and Prior Authorization Final Rule (CMS-0057-F).\n"
        "Rules:\n"
        "- Do not answer the question.\n"
        "- Do not include greetings, introductions, or conversational filler.\n"
        "- Output ONLY the optimized search phrase."
    )

    user_instruction = f"Optimize the query for vector database retrieval: '{user_query}'"

    response = llm.invoke(
        [
        SystemMessage(content=system_instruction),
        HumanMessage(content=user_instruction)
    ]
    )

    rephrased_query = response.content.strip()
    # rephrased_query = rephrased_query.replace('"', '').replace("'", "")
    print("-- Rephrased query :", rephrased_query)
    print(f"-- Loop Count : {state.get("loop_count")}")

    return {
        "user_query": rephrased_query,
        "loop_count": current_loop + 1
    }

def followup_node(state : state_class) -> dict:

    print("NODE -> Follow-up")

    vague_query = state.get("user_query")

    system_instruction = (
        "You are a medical compliance assistant. The user asked a question that is too vague "
        "for our database search engine. Ask a concise, professional follow-up question "
        "requesting clarification on the missing details they are asking about. "
        "You may give suggestions based on their question. \n"
        "Keep your response under two sentences."
    )

    user_instruction = f"The vague query is: '{vague_query}'"

    response = llm.invoke(
        [
            SystemMessage(content=system_instruction),
            HumanMessage(content=user_instruction)
        ]
    )

    print("-- Followup query :", response.content.strip())
    return {
        "final_response": response.content.strip(),
        "followup_required" : True
    }