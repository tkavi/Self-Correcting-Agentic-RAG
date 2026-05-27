from typing import TypedDict, List

class State(TypedDict):
    user_query : str              
    is_vague : bool
    followup_required : bool        
    relevant_chunks : List[str]     
    final_response : str             
    is_offensive : bool      
    is_relevant : bool       
    loop_count : int           # Counter to prevent infinite loops during rephrasing