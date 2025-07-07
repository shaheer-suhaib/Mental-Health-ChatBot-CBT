from typing import TypedDict, Annotated, Sequence,List,Union
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, ToolMessage
from operator import add as add_messages

class AgentState(TypedDict):
   
    messages: Annotated[Sequence[BaseMessage], add_messages]

    # Current stage
    stage: str 

    # Intake information
    presenting_problem: str       
    history: str                

    #  Case formulation (abc model)
    activating_event: str        
    beliefs: List[str]           
    consequences: List[str]       

  
    # LLM & Routing
    last_user_message: str            
    next_node: Union[str,bool]                   

  
    ready_to_end: bool                