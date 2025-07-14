from typing import TypedDict, Annotated, Sequence,List,Union
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, ToolMessage
from langgraph.graph import add_messages

class AgentState(TypedDict):
   
    messages: Annotated[Sequence[BaseMessage], add_messages]

    # Intake information
    presenting_problem: str       
    history: str                

    #  Case formulation (abc model)
    activating_event: str        
    beliefs: List[str]           
    consequences: List[str]       

         
    next_node: Union[str,bool]                   
              