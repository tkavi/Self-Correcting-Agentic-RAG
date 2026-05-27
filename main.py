import os
from dotenv import load_dotenv
from typing import Literal
from IPython.display import Image, display

from langgraph.graph import StateGraph, START, END

# Internal files
from state import State as state_class
from nodes import (
    guardrails_node,
    retrieve_node,
    evals_node,
    generate_node,
    rephrase_node,
    followup_node
)

# loading env varibles
load_dotenv()

# conditional workflows
def flow_after_guardrails(state : state_class) -> Literal["retrieve", "followup", END]:
    if state.get("is_offensive") == True :
        return END
    if state.get("is_vague") == True :
        return "followup"
    return "retrieve"

def flow_after_evals(state : state_class) -> Literal["generate", "rephrase"]:
    if state.get("is_relevant") == True :
        return "generate"
    if state.get("loop_count",0) >= 3 :
        return "generate"
    return "rephrase"

# Initializing Stategraph
workflow = StateGraph(state_class)

# adding nodes to Stategraph
workflow.add_node("guardrails", guardrails_node)
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("evaluate", evals_node)
workflow.add_node("generate", generate_node)
workflow.add_node("rephrase", rephrase_node)
workflow.add_node("followup", followup_node)

# adding edges to Stategraph
workflow.add_edge(START, "guardrails")

# --Flow 1 (Correct query)
workflow.add_conditional_edges("guardrails",flow_after_guardrails,
                               {
                                   "retrieve":"retrieve",
                                   "followup":"followup",
                                   END:END
                               })

workflow.add_edge("retrieve","evaluate")

workflow.add_conditional_edges("evaluate",flow_after_evals,
                               {
                                   "generate":"generate",
                                   "rephrase":"rephrase"
                               })

workflow.add_edge("generate", END)

# --Flow 2 (Rephrase if not relevant after evaluate)
workflow.add_edge("rephrase","retrieve") # -> evauate -> generate -> END

# --Flow 3 (Vague query)
workflow.add_edge("followup", END) # continues loop until final response generated


# Compiling the graph
graph = workflow.compile()

# to view the graph flow
png = graph.get_graph().draw_mermaid_png()
# display(Image(png)) # works only for Jupyter nb

# to view the graph manually
with open("graph.png","wb") as f:
    f.write(png)

# starting point of the application
if __name__ == "__main__" :
    print("Start of RAG application")

    initial_state = {
        "user_query" : input("Type your query here...\n"),
        "is_vague" : False,  
        "followup_required" : False,            
        "relevant_chunks" : [], 
        "final_response" : "",            
        "is_offensive" : False,      
        "is_relevant" : False,         
        "loop_count" : 0 
    }

    while True:
        final_state = graph.invoke(initial_state)

        if final_state.get("followup_required") == True:
            followup_clarification = input("Input your query again...\n")

            combined_query = f"Original query:'{initial_state['user_query']}' and followp clarifiaction :'{followup_clarification}'"

            # initial_state = {
            #     "user_query": combined_query,
            #     "is_vague": False,  
            #     "followup_required": False,            
            #     "relevant_chunks": [], 
            #     "final_response": "",            
            #     "is_offensive": False,      
            #     "is_relevant": False,         
            #     "loop_count": 0 
            # }

            initial_state["user_query"] = combined_query
            initial_state["is_vague"] = False
            initial_state["followup_required"] = False
            initial_state["final_response"] = ""
            # initial_state["relevant_chunks"] = []

            continue

        else:
            print("Response:", final_state["final_response"])
            break

    