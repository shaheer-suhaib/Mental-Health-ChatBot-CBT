# from Conversation_Chat import CBTChatbot
from Graph import CBTGraph
from langchain.schema import HumanMessage
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, ToolMessage,AIMessage,AIMessageChunk,FunctionMessage
import time

def print_red(text):
    print(f"\033[31m{text}\033[0m")

def take_input():
    user_input = input("Hello how can i help you Today. Are you struggling with Any Mental Distress\n")
    messages = [HumanMessage(content=user_input)]
        
       
    initial_state = {         
            "messages": messages, 
            "next_node" : False
        }
    return initial_state

if __name__ == "__main__":
    inst = CBTGraph()
    graph_compiled=inst.get_graph()

    last_type = None  

    initial_state = take_input()

    print("👱‍♂️  USER:", initial_state["messages"][0].content)

    for message_chunk, metadata in graph_compiled.stream(initial_state, stream_mode="messages"):
        if message_chunk.content:
            msg_type = type(message_chunk).__name__

        
            if msg_type != last_type:

                if  msg_type=="AIMessageChunk":

                    print_red("BOT")
                elif  msg_type== "ToolMessage":

                    print_red(" TOOL Process OUT")
            
                
                last_type = msg_type

            if isinstance(message_chunk, AIMessageChunk):
                print(message_chunk.content, end="", flush=True)
            elif isinstance(message_chunk, ToolMessage):
                print( message_chunk.content, end="|", flush=True)
            elif isinstance(message_chunk, HumanMessage):
                print("👱‍♂️  USER:", message_chunk.content, end="|", flush=True)
            elif isinstance(message_chunk, FunctionMessage):


                if metadata["langgraph_node"] == "intake_node":
                    print(7*"  "+"Process Happend in INTAKE NODE ")
                    print( message_chunk.content)

                elif metadata["langgraph_node"] == "Case_Formulatin":
                    print(7*"  "+"Process Happend in Case Formulatin NODE ")
                    print( message_chunk.content)
        


    