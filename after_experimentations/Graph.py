from langgraph.graph import StateGraph, END

from typing import TypedDict, Annotated, Sequence, List
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, ToolMessage
from operator import add as add_messages
import json
import re
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import ToolNode

from CBT_State import AgentState


class CBTGraph:
    def __init__(self):
     
       
       
       
        self.llm_json = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=GenerationConfig(
                response_mime_type="application/json",
                temperature=0
            )
        )

        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=self.GEMINI_API_KEY)
        
        #  tools
        self.tools = [self.run_phq9_assessment, self.run_gad7_assessment]
        self.llm = self.llm.bind_tools(self.tools)
        
        #  graph
        self.graph = self._build_graph()

    def _build_graph(self):
    
        graph = StateGraph(AgentState)
        graph.add_node("intake_node", self.intake_node)
        graph.add_node("Case_Formulatin", self.case_formulation_node)
        graph.add_node("router_node", self.router_node)
        graph.add_node("emotional_check_in_node",self.emotional_check_in_node)


        graph.set_entry_point("intake_node")
        graph.add_edge("intake_node","Case_Formulatin")
        graph.add_edge("Case_Formulatin","router_node")



        graph.add_conditional_edges(
            "router_node",
            self.decide_next_node, 

            {
                # Edge: Node
            #  "psychoeducation": "pss",
                "emotional_check_in": "emotional_check_in_node",
            }

        )

        # ToolNode()
        tool_node = ToolNode(tools=self.tools)
        graph.add_node("PHQ9/GAD-7 TOOLS", tool_node)




        graph.add_conditional_edges(
            "emotional_check_in_node",
            self.should_continue,
        {
                "continue": "PHQ9/GAD-7 TOOLS",
                "end": END,

        }
        )

        graph.add_edge("PHQ9/GAD-7 TOOLS", "emotional_check_in_node")






        graph.set_finish_point("emotional_check_in_node")
      
        return graph.compile()

    def intake_node(self, state: AgentState) -> AgentState:
      

       
        human_messages = [msg for msg in state["messages"] if isinstance(msg, HumanMessage)]
        if not human_messages:
            raise ValueError("No user message found for intake.")

        user_input = human_messages[0].content

       
        prompt = (
            "You are a CBT assistant.\n"
            "Extract the user's presenting problem and a brief emotional history from this message:\n\n"
            f"{user_input}\n\n"
            "Respond ONLY with valid JSON in this exact format:\n"
            "{\n"
            "  \"presenting_problem\": \"...\",\n"
            "  \"history\": \"...\"\n"
            "}"
        )

        # messages = [SystemMessage(content=prompt)] + state["messages"]

    
        # response = self.llm.invoke(messages)
        response = self.llm.invoke([SystemMessage(content=prompt), HumanMessage(content=user_input)])

        
        response_content = response.content
        
        
        if isinstance(response_content, str):
            # Remove markdown code blocks if present
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_content, re.DOTALL)
            if json_match:
                response_content = json_match.group(1)
            else:
                # Try to find JSON object in the text
                json_match = re.search(r'\{.*?\}', response_content, re.DOTALL)
                if json_match:
                    response_content = json_match.group(0)
        
        # Parse the JSON
        try:
            if isinstance(response_content, dict):
                result = response_content
            else:
                result = json.loads(response_content)
        except (json.JSONDecodeError, TypeError):
            # Fallback: create a simple result
            result = {
                "presenting_problem": user_input,
                "history": "No specific history provided"
            }

        
        return {
            # "messages": messages + [response],

            "messages": [SystemMessage(content=prompt), response],
            "stage": "case_formulation_node",
            "presenting_problem": result.get("presenting_problem", ""),
            "history": result.get("history", ""),
            "activating_event": "",
            "beliefs": [],
            "consequences": [],
            "last_user_message": user_input,
            "next_node": "",
            "ready_to_end": False
        }

  
  
  
    def case_formulation_node(self, state: AgentState) -> AgentState:
        presenting_problem = state["presenting_problem"]

        prompt = (
            "You are a CBT assistant.\n"
            "Given this user's presenting problem, extract as much of the ABC model as possible:\n"
            "- A (Activating Event): what clearly happened?\n"
            "- B (Beliefs): only include if user directly stated their thoughts or judgments\n"
            "- C (Consequences): only include if emotions or actions are clearly stated\n\n"
            f"Presenting Problem:\n{presenting_problem}\n\n"
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

        return {
            **state,
            # "messages": state["messages"] + [HumanMessage(content=response.text)],
            "messages": [HumanMessage(content=f'{{"activating_event": "{result.get("activating_event", "")}", "beliefs": {result.get("beliefs", [])}, "consequences": {result.get("consequences", [])}}}')],
            "stage": "goal_setting_node",
            "activating_event": result.get("activating_event", ""),
            "beliefs": result.get("beliefs", []),
            "consequences": result.get("consequences", [])
        }



    def router_node(self, state: AgentState) -> AgentState:
      
        
        prompt = (
            "You are a CBT workflow assistant. Choose the next most appropriate therapeutic step.\n\n"
            "Current State:\n"
            f"Presenting Problem: {state['presenting_problem']}\n"
            f"History: {state['history']}\n"
            f"Activating Event: {state['activating_event']}\n"
            f"Beliefs: {state['beliefs']}\n"
            f"Consequences: {state['consequences']}\n"
            f"Last User Message: {state['last_user_message']}\n\n"
            "Available Options:\n"
            "- emotional_check_in: If user shows distress, negative emotions, or needs emotional support\n"
            "- psychoeducation: If user needs to understand CBT concepts or coping strategies\n"
            "- emergency_support: If there are signs of crisis, panic, or suicidal thoughts\n"
            "- problem_solving: If user is stuck or needs practical solutions\n"
            "- goal_setting_node: If ready to set therapeutic goals\n\n"
            "Respond in this EXACT format:\n"
            "{\n"
            "  \"next_node\": \"...\",\n"
            "  \"reasoning\": \"...\"\n"
            "}"
        )
        
        response = self.llm_json.generate_content(prompt)
        
        # Parse JSON response
        try:
            result = json.loads(response.text.strip())
            next_node = result.get("next_node")
            if not next_node:
                raise ValueError("Missing next_node in response")
        except:
            raise ValueError("Router failed to parse LLM response - check model configuration")
        
        # Validate the response
        valid_nodes = ["emotional_check_in", "psychoeducation", "emergency_support", "problem_solving", "goal_setting_node"]
        if next_node not in valid_nodes:
            raise ValueError(f"Invalid next_node '{next_node}' - must be one of {valid_nodes}")
        
        return {
            **state,
            "next_node": next_node,
            "stage": "router"
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





    def emotional_check_in_node(self, state: AgentState) -> AgentState:
          
            
            prompt = (
                "You are a CBT therapist doing an emotional check-in.\n\n"
                "Current State:\n"
                f"Presenting Problem: {state['presenting_problem']}\n"
                f"Consequences: {state['consequences']}\n"
                f"Last User Message: {state['last_user_message']}\n\n"
                "Provide empathetic emotional support and validate their feelings.\n"
                "Based on their emotional state, use the appropriate assessment tool if needed.\n"
                "You have access to depression and anxiety screening tools. [run_phq9_assessment, run_gad7_assessment]"
            )
            
           
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
           
            print(f"\n🎯 EMOTIONAL CHECK-       NODE:")
           
            
            # Check if tools were called
            if hasattr(response, 'tool_calls') and response.tool_calls:
                for tool_call in response.tool_calls:
                    print(f"\n🔍 Running {tool_call['name']}...")
                 
            
            return {
                **state,
                "messages": state["messages"] + [response],
                "stage": "emotional_check_in",
                "next_node": True
            }

    
    
    def decide_next_node(self, state: AgentState) -> AgentState:
        
        return state['next_node']
    
    def should_continue(state: AgentState) -> str:
        last = state["messages"][-1]
        if not getattr(last, "tool_calls", None):
            return "end"
        return "continue"


    def get_graph(self):
        
        return self.graph

    def invoke(self, initial_state: AgentState):
        
        return self.graph.invoke(initial_state)

    def stream(self, initial_state: AgentState):
     
        return self.graph.stream(initial_state)