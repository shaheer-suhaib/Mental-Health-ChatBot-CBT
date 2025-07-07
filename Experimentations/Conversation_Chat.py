from typing import Dict, List
from langchain.schema import HumanMessage, AIMessage

class CBTChatbot:
    """Simplified CBT Chatbot that works with your existing graph"""
    
    def __init__(self, compiled_GRAPH):
      #  self.graph = graph
        self.app = compiled_GRAPH
        self.current_state = None
        self.conversation_active = True
        
    def run_conversation(self):
        """Main conversation loop"""
        print("🤖 CBT Chatbot Started")
        print("💬 Type 'quit', 'exit', or 'bye' to end the conversation")
        print("=" * 60)
        
        # Get initial user input
        user_input = input("👤 Please tell me what brings you here today: ").strip()
        
        if self._should_exit(user_input):
            return
        
        # Create initial state
        self.current_state = self._create_initial_state(user_input)
        
        # Process through the graph once to get to interactive stage
        print("\n🔄 Processing your information...")
        self.current_state = self.app.invoke(self.current_state)
        
        # Main conversation loop - only for interactive nodes
        while self.conversation_active:
            try:
                current_stage = self.current_state.get('stage', '')
                
                # Show current stage info
                print(f"\n📍 Current Stage: {current_stage}")
                
                # Show AI response if available
                self._show_latest_ai_response()
                
                # Check if we've reached the end
                if self._is_end_stage(current_stage):
                    print("\n🎉 Thank you for the session!")
                    print("💪 Remember the techniques we discussed.")
                    print("👋 Take care!")
                    break
                
                # Get user input for interactive stages
                if self._is_interactive_stage(current_stage):
                    user_input = input("\n👤 You: ").strip()
                    
                    if self._should_exit(user_input):
                        break
                    
                    # Handle special commands
                    if self._handle_special_commands(user_input):
                        continue
                    
                    # Update state with user input
                    self.current_state['messages'].append(HumanMessage(content=user_input))
                    self.current_state['last_user_message'] = user_input
                    
                    # Process through graph again
                    print("\n🔄 Processing...")
                    self.current_state = self.app.invoke(self.current_state)
                else:
                    # For non-interactive stages, just continue
                    print("\n🔄 Continuing...")
                    self.current_state = self.app.invoke(self.current_state)
                    
            except KeyboardInterrupt:
                print("\n👋 Conversation interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n⚠️ Error: {e}")
                print("Let's continue...")
                continue
    
    def _create_initial_state(self, user_input: str) -> Dict:
        """Create initial conversation state"""
        return {
            "messages": [HumanMessage(content=user_input)],
            "stage": "intake_node",
            "presenting_problem": "",
            "history": "",
            "activating_event": "",
            "beliefs": [],
            "consequences": [],
            "last_user_message": user_input,
            "next_node": "",
            "ready_to_end": False
        }
    
    def _show_latest_ai_response(self):
        """Show the latest AI response from messages"""
        messages = self.current_state.get('messages', [])
        for msg in reversed(messages):
            if hasattr(msg, 'content') and 'AIMessage' in str(type(msg)):
                print(f"\n🤖 Therapist: {msg.content}")
                break
    
    def _is_interactive_stage(self, stage: str) -> bool:
        """Check if current stage requires user interaction"""
        interactive_stages = [
            "emotional_check_in",
            "psychoeducation", 
            "problem_solving",
            "goal_setting"
        ]
        return stage in interactive_stages
    
    def _is_end_stage(self, stage: str) -> bool:
        """Check if we've reached an end stage"""
        end_stages = ["end_therapy", "session_complete"]
        return stage in end_stages or self.current_state.get('ready_to_end', False)
    
    def _should_exit(self, user_input: str) -> bool:
        """Check if user wants to exit"""
        return user_input.lower() in ['quit', 'exit', 'bye']
    
    def _handle_special_commands(self, user_input: str) -> bool:
        """Handle special commands"""
        if user_input.lower() == 'status':
            self._show_status()
            return True
        elif user_input.lower() == 'restart':
            print("🔄 Restarting conversation...")
            self.run_conversation()
            return True
        return False
    
    def _show_status(self):
        """Show current conversation status"""
        print(f"\n📊 Current Status:")
        print(f"Stage: {self.current_state.get('stage', 'Unknown')}")
        print(f"Problem: {self.current_state.get('presenting_problem', 'Not identified')}")
        print(f"Messages: {len(self.current_state.get('messages', []))}")
        print(f"Ready to end: {self.current_state.get('ready_to_end', False)}")

