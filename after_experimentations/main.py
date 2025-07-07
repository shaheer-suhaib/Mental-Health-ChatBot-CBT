# from Conversation_Chat import CBTChatbot
from Graph import CBTGraph
from langchain.schema import HumanMessage
import time

if __name__ == "__main__":
    inst = CBTGraph()
    graph_compiled=inst.get_graph()
  
   
    # chatbot = CBTChatbot(graph_compiled)
    # chatbot.run_conversation()
    user_input = "I yelled at my son today. I feel like a horrible parent.  i feel low "


    
    messages = [HumanMessage(content=user_input)]
        
      
    initial_state = {          ##3333333???????
            "messages": messages,
            "stage": "intake_node",
            "presenting_problem": "",
            "history": "",
            "activating_event": "",
            "beliefs": [],
            "consequences": [],
            "last_user_message": "",
            "next_node": "",
            "ready_to_end": False
        }
    st = graph_compiled.stream(initial_state,stream_mode="values")
    print("streaming")
    
    for s in st:
        try:
            # Check if 'messages' key exists and has content
            if "messages" in s and s["messages"]:
                message = s["messages"][-1]
                
                if isinstance(message, tuple):
                    print(message)
                elif hasattr(message, 'pretty_print'):
                    message.pretty_print()
                else:
                    # Fallback for other message types
                    print(f"Message: {message}")
            else:
                # Handle cases where there are no messages
                print(f"State update: {s}")
                
        except Exception as e:
            print(f"Error processing stream item: {e}")
            print(f"Stream item: {s}")
            continue