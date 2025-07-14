from langgraph.graph import StateGraph, END

from typing import TypedDict, Annotated, Sequence, List
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, ToolMessage,FunctionMessage,AIMessage
import json
import re
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import ToolNode

from CBT_State import AgentState


from dotenv import load_dotenv
import os


load_dotenv()

class CBTGraph:
    def __init__(self):
        GEMINI_API_KEY_JSON_LLM = os.getenv("GEMINI_API_KEYJ")

        genai.configure(api_key=GEMINI_API_KEY_JSON_LLM)
            
       
       
       
        self.llm_json = genai.GenerativeModel(
            model_name="gemini-2.0-flash-lite",
            generation_config=GenerationConfig(
                response_mime_type="application/json",
                temperature=0
            )
            
        )

        Talk_llm = os.getenv("GEMINI_API_KEYY")

        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite", google_api_key=Talk_llm)
        
        #  tools
        self.tools = [self.run_phq9_assessment, self.run_gad7_assessment]
        self.llm = self.llm.bind_tools(self.tools)
        
        #  graph
        self.graph = self._build_graph()

    def print_red(self,text):
        print(f"\033[31m{text}\033[0m") 
    def _build_graph(self):
        graph = StateGraph(AgentState)
        graph.add_node("intake_node", self.intake_node)
        graph.add_node("Case_Formulatin", self.case_formulation_node)
        graph.add_node("Screening_Node",self.Screening_Node)


        graph.set_entry_point("intake_node")
        graph.add_edge("intake_node","Case_Formulatin")
        graph.add_edge("Case_Formulatin","Screening_Node")



        # ToolNode()
        tool_node = ToolNode(tools=self.tools)
        graph.add_node("PHQ9/GAD-7 TOOLS", tool_node)



        graph.add_conditional_edges(
            "Screening_Node",
            self.should_continue,
        {
                "continue": "PHQ9/GAD-7 TOOLS",
                "end": END,

        }
        )

        graph.add_edge("PHQ9/GAD-7 TOOLS", "Screening_Node")


        graph.set_finish_point("Screening_Node")
            

      
        return graph.compile()

    def intake_node(self, state: AgentState) -> AgentState:
        user_input = state["messages"][-1].content
    
        prompt = (
            "You are a CBT assistant.\n"
            "Extract the user's presenting problem and a brief emotional history from this message:\n\n"
            "Respond ONLY with valid JSON in this exact format:\n"
            f"User message: {user_input}\n\n"
            "{\n"
            "  \"presenting_problem\": \"...\",\n"
            "  \"history\": \"...\"\n"
            "}"
        )

        response = self.llm_json.generate_content(prompt)


        response_content = response.text
    
        if isinstance(response_content, str):
        
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_content, re.DOTALL)
            if json_match:
                response_content = json_match.group(1)
            else:
                
                json_match = re.search(r'\{.*?\}', response_content, re.DOTALL)
                if json_match:
                    response_content = json_match.group(0)
        
    
        try:
            if isinstance(response_content, dict):
                result = response_content
            else:
                result = json.loads(response_content)
        except (json.JSONDecodeError, TypeError):
        
            result = {
                "presenting_problem": user_input,
                "history": "No specific history provided"
            }


        presenting_problem = result.get("presenting_problem", "")
        history = result.get("history", "")  
        
        
        state['presenting_problem'] = presenting_problem
        state['history'] = history
        
        t = FunctionMessage(
            name="t",
            content=f'{{"presenting_problem": "{presenting_problem}", "history": "{history}"}}'
        ) 

        prompt = ( f"You are a CBT assistant. Acknowledge that you understand the user's situation from their problem: {presenting_problem} and history: {history}. Respond in just 3 lines." )

        msg=self.llm.invoke(prompt)
        state["messages"].append( AIMessage(content=msg.content) )

        self.print_red("                  --------------INTAKE NODE   OUT---------------------")

    
        return {
            "presenting_problem": presenting_problem,
            "history": history,  
            'messages' :  [ t ]
        }
  
  
  
    def case_formulation_node(self, state: AgentState) -> AgentState:
     

        prompt = (
            "You are a CBT assistant.\n"
            "Given this user's presenting problem, extract as much of the ABC model as possible:\n"
            "- A (Activating Event): what clearly happened?\n"
            "- B (Beliefs): only include if user directly stated their thoughts or judgments\n"
            "- C (Consequences): only include if emotions or actions are clearly stated\n\n"
            f"Presenting Problem:\n{  state["presenting_problem"]}\n\n"
            f"histroy:\n {state["history"]}\n\n"
            "Respond in this EXACT format:\n"
            "{\n"
            "  \"activating_event\": \"...\",\n"
            "  \"beliefs\": [\"...\", \"...\"],\n"
            "  \"consequences\": [\"...\", \"...\"]\n"
            "}"
        )

        
        response = self.llm_json.generate_content(prompt)
        
       
        content = response.text.strip()
        
        try:
            result = json.loads(content)
        except:
            result = {}

        self.print_red("                  --------------case_formulation_node   OUT---------------------")

        return {
            **state,
         
            "messages": [FunctionMessage(name ="t",content=f'{{"activating_event": "{result.get("activating_event", "")}", "beliefs": {result.get("beliefs", [])}, "consequences": {result.get("consequences", [])}}}')],
             
            "activating_event": result.get("activating_event", ""),
            "beliefs": result.get("beliefs", []),
            "consequences": result.get("consequences", [])
        }




    
    def Screening_Node(self, state: AgentState) -> AgentState:
                self.print_red("\n                  --------------Screening_Tool---------------------")

                if state['next_node']:
                    return
        
            
                
                prompt = (
                    "You are a CBT therapist doing an Screening Tool test You are provided with user current information Based on The informatin you can run depression and anxiety screening tools. [run_phq9_assessment, run_gad7_assessment].You can run just one tool only.  User information is Shown\n\n"
                
                    f"Presenting Problem: {state['presenting_problem']}\n"
                    f"history: {state['history']}\n"
                    f"Belief: {state['beliefs']}\n"
                    f"Consequences: {state['consequences']}\n"
                
            
                )
                
            
                response = self.llm.invoke([HumanMessage(content=prompt)])
            
            
                if hasattr(response, 'tool_calls') and response.tool_calls:
                    for tool_call in response.tool_calls:
                        self.print_red(f"\n Running {tool_call['name']}...")
                    
                    

                state["next_node"] = True

                self.print_red("\n                  --------------Screening_Tool  OUT---------------------")

                
                return {
                    **state,
                    "messages": [response],
                    
                }

        
    @tool
    def run_phq9_assessment() -> dict:
        """Run PHQ-9 depression screening assessment FOR user if it is needed"""

        print(" Running PHQ-9 Assessment")
        questions = [
            "Over the last 2 weeks, how often have you felt little interest or pleasure in doing things?",
            "How often have you felt down, depressed, or hopeless?",
            "How often have you had trouble falling or staying asleep?"
        ]
        answers = []
        for q in questions:
            print("🤖:", q)
            a = input("You: ")
            answers.append(a)
        score = sum(3 for a in answers if "yes" in a.lower() or "often" in a.lower())
        return {"tool_name": "PHQ9", "score": score}


    @tool
    def run_gad7_assessment() -> dict:
        """Run GAD-7 anxiety screening assessment FOR user if it is needed"""

    

        print(" Running GAD-7 Assessment")
        questions = [
            "Have you been feeling nervous or on edge?",
            "Do you find it difficult to stop worrying?",
            "Do you feel easily irritated?"
        ]
        answers = []
        for q in questions:
            print("🤖:", q)
            a = input("You: ")
            answers.append(a)
        score = sum(3 for a in answers if "yes" in a.lower() or "often" in a.lower())
        return {"tool_name": "GAD7", "score": score}




    
    def decide_next_node(self, state: AgentState) -> AgentState:
        
        return state['next_node']
    
    def should_continue(self,state: AgentState) -> str:
        
        messages = state["messages"]
        if not messages:
            return "end"
        
        last_message = messages[-1]
        
    
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "continue"
        else:

            print("Ending tool execution")
            return "end"


    def get_graph(self):
        
        return self.graph

    def invoke(self, initial_state: AgentState):
        
        return self.graph.invoke(initial_state)

    def stream(self, initial_state: AgentState):
     
        return self.graph.stream(initial_state)