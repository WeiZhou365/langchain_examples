import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm.gemini import get_gemini_client

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langgraph_swarm import create_handoff_tool, create_swarm
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

model = get_gemini_client()

def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

alice = create_react_agent(
    model,
    [add, multiply, create_handoff_tool(agent_name="Bob")],
    prompt="You are Alice, a math expert who can add and multiply numbers. Be helpful and friendly.",
    name="Alice",
)

bob = create_react_agent(
    model,
    [create_handoff_tool(agent_name="Alice", description="Transfer to Alice, she can help with math")],
    prompt="You are Bob, you speak like a pirate and are great at storytelling. You cannot do math - always transfer math questions to Alice.",
    name="Bob",
)

def print_conversation(result, turn_name):
    """Print a nicely formatted conversation."""
    print(f"\n{'='*60}")
    print(f"📝 {turn_name}")
    print('='*60)
    
    for message in result["messages"]:
        if isinstance(message, HumanMessage):
            print(f"👤 User: {message.content}")
        elif isinstance(message, AIMessage):
            agent_name = getattr(message, 'name', 'Unknown')
            if agent_name == 'Alice':
                print(f"🧮 Alice: {message.content}")
            elif agent_name == 'Bob':
                print(f"🏴‍☠️ Bob: {message.content}")
            else:
                print(f"🤖 {agent_name}: {message.content}")
        elif isinstance(message, ToolMessage):
            # Skip tool messages for cleaner output, or show them conditionally
            if "transferred" in message.content.lower():
                print(f"🔄 System: Agent handoff completed")
    
    print(f"\n📊 Active Agent: {result['active_agent']}")
    print("-" * 60)

def main():
    print("🐝 LangGraph Swarm Conversation Example")
    print("🧮 Alice: Math expert (addition, multiplication)")
    print("🏴‍☠️ Bob: Pirate storyteller (transfers math to Alice)")
    
    checkpointer = InMemorySaver()
    workflow = create_swarm(
        [alice, bob],
        default_active_agent="Alice"
    )
    app = workflow.compile(checkpointer=checkpointer)
    
    config = {"configurable": {"thread_id": "conversation_1"}}
    
    # Conversation turns
    conversations = [
        "Hi! I'd like to speak to Bob",
        "Tell me a pirate story!",
        "What's 5 + 7?",
        "Can you multiply 6 by 9?",
        "Bob, tell me another story about treasure hunting",
        "Alice, what's 15 + 25 + 10?"
    ]
    
    for i, user_input in enumerate(conversations, 1):
        print(f"\n🗣️ Turn {i}: {user_input}")
        
        try:
            result = app.invoke(
                {"messages": [{"role": "user", "content": user_input}]},
                config,
            )
            
            print_conversation(result, f"Turn {i} Result")
            
        except Exception as e:
            print(f"❌ Error in turn {i}: {str(e)}")
    
    print(f"\n🎉 Conversation Complete!")
    print(f"📊 Final Summary:")
    print(f"   - Total turns: {len(conversations)}")
    print(f"   - Active agent: {result.get('active_agent', 'Unknown')}")
    print(f"   - Thread ID: {config['configurable']['thread_id']}")

if __name__ == "__main__":
    main()