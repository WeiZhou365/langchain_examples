import sys
import os
# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph.graph import StateGraph, END
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from llm.gemini import get_gemini_client
from typing import TypedDict, List, Literal
import json

# Define the state that will be passed between agents
class HandoffState(TypedDict):
    messages: List[dict]
    current_agent: str
    task_type: str
    handoff_reason: str
    final_result: str

# Define tools for different agents
@tool
def research_tool(query: str) -> str:
    """Research information about a topic."""
    # Simulated research - in real scenario, this could call APIs, databases, etc.
    research_data = {
        "quantum computing": "Quantum computing uses quantum mechanical phenomena like superposition and entanglement to process information.",
        "machine learning": "Machine learning is a subset of AI that enables computers to learn without being explicitly programmed.",
        "blockchain": "Blockchain is a distributed ledger technology that maintains a secure and decentralized record of transactions."
    }
    return research_data.get(query.lower(), f"No specific research data found for {query}")

@tool
def analysis_tool(data: str) -> str:
    """Analyze data and provide insights."""
    # Simulated analysis
    if "quantum" in data.lower():
        return "Analysis: Quantum computing shows promise for cryptography, optimization, and simulation problems."
    elif "machine learning" in data.lower():
        return "Analysis: ML applications span across healthcare, finance, autonomous vehicles, and recommendation systems."
    elif "blockchain" in data.lower():
        return "Analysis: Blockchain technology can improve transparency, security, and decentralization in various industries."
    else:
        return f"Analysis: The provided data requires further investigation to draw meaningful insights."

@tool
def writing_tool(content: str) -> str:
    """Format content into a well-structured report."""
    return f"""
# Research Report

## Executive Summary
{content}

## Key Findings
- Technology shows significant potential
- Multiple industry applications identified
- Further research recommended

## Conclusion
The analysis indicates promising opportunities for implementation and development.
"""

# Agent definitions
class ResearchAgent:
    def __init__(self, llm):
        self.llm = llm
        self.name = "Research Agent"
        self.tools = [research_tool]
    
    def process(self, state: HandoffState) -> HandoffState:
        print(f"\n🔬 {self.name} is working...")
        
        # Get the user query from messages
        user_query = state["messages"][-1]["content"] if state["messages"] else ""
        
        # Use research tool
        research_result = research_tool.invoke({"query": user_query})
        
        # Determine if we need to hand off to analysis
        if len(research_result) > 50:  # If we have substantial research data
            state["messages"].append({
                "role": "assistant", 
                "content": f"Research completed: {research_result}",
                "agent": self.name
            })
            state["current_agent"] = "analysis"
            state["handoff_reason"] = "Research completed, needs analysis"
        else:
            state["messages"].append({
                "role": "assistant", 
                "content": f"Insufficient research data: {research_result}",
                "agent": self.name
            })
            state["current_agent"] = "end"
            state["final_result"] = "Research incomplete"
        
        return state

class AnalysisAgent:
    def __init__(self, llm):
        self.llm = llm
        self.name = "Analysis Agent"
        self.tools = [analysis_tool]
    
    def process(self, state: HandoffState) -> HandoffState:
        print(f"\n📊 {self.name} is working...")
        
        # Get the research data from previous messages
        research_data = ""
        for msg in state["messages"]:
            if msg.get("agent") == "Research Agent":
                research_data = msg["content"]
                break
        
        # Analyze the research data
        analysis_result = analysis_tool.invoke({"data": research_data})
        
        state["messages"].append({
            "role": "assistant",
            "content": analysis_result,
            "agent": self.name
        })
        
        # Hand off to writing agent
        state["current_agent"] = "writing"
        state["handoff_reason"] = "Analysis completed, needs formatting"
        
        return state

class WritingAgent:
    def __init__(self, llm):
        self.llm = llm
        self.name = "Writing Agent"
        self.tools = [writing_tool]
    
    def process(self, state: HandoffState) -> HandoffState:
        print(f"\n✍️ {self.name} is working...")
        
        # Compile all previous work
        all_content = ""
        for msg in state["messages"]:
            if msg.get("agent") in ["Research Agent", "Analysis Agent"]:
                all_content += msg["content"] + "\n"
        
        # Format into final report
        final_report = writing_tool.invoke({"content": all_content})
        
        state["messages"].append({
            "role": "assistant",
            "content": final_report,
            "agent": self.name
        })
        
        state["current_agent"] = "end"
        state["final_result"] = final_report
        
        return state

# Router function to determine next agent
def route_to_agent(state: HandoffState) -> Literal["research", "analysis", "writing", "end"]:
    current = state.get("current_agent", "research")
    print(f"\n🔄 Routing to: {current}")
    return current

# Node functions for the graph
def research_node(state: HandoffState) -> HandoffState:
    llm = get_gemini_client()
    agent = ResearchAgent(llm)
    return agent.process(state)

def analysis_node(state: HandoffState) -> HandoffState:
    llm = get_gemini_client()
    agent = AnalysisAgent(llm)
    return agent.process(state)

def writing_node(state: HandoffState) -> HandoffState:
    llm = get_gemini_client()
    agent = WritingAgent(llm)
    return agent.process(state)

def create_handoff_graph():
    """Create the LangGraph workflow with handoff patterns."""
    
    # Create the graph
    workflow = StateGraph(HandoffState)
    
    # Add nodes
    workflow.add_node("research", research_node)
    workflow.add_node("analysis", analysis_node)
    workflow.add_node("writing", writing_node)
    
    # Set entry point
    workflow.set_entry_point("research")
    
    # Add conditional edges for handoffs
    workflow.add_conditional_edges(
        "research",
        route_to_agent,
        {
            "analysis": "analysis",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "analysis", 
        route_to_agent,
        {
            "writing": "writing",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "writing",
        route_to_agent,
        {
            "end": END
        }
    )
    
    return workflow.compile()

def main():
    print("🚀 Starting LangGraph Handoff Pattern Example")
    
    # Create the workflow
    app = create_handoff_graph()
    
    # Test queries
    queries = [
        "quantum computing",
        "machine learning", 
        "blockchain"
    ]
    
    for query in queries:
        print(f"\n{'='*60}")
        print(f"🎯 Processing Query: {query}")
        print('='*60)
        
        # Initial state
        initial_state = {
            "messages": [{"role": "user", "content": query}],
            "current_agent": "research",
            "task_type": "research_analysis_report",
            "handoff_reason": "Initial request",
            "final_result": ""
        }
        
        try:
            # Run the workflow
            final_state = app.invoke(initial_state)
            
            print(f"\n📋 Final Result:")
            print(final_state["final_result"])
            
            print(f"\n📊 Workflow Summary:")
            print(f"- Total messages: {len(final_state['messages'])}")
            print(f"- Final agent: {final_state['current_agent']}")
            print(f"- Last handoff reason: {final_state['handoff_reason']}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("\n" + "-"*60)

if __name__ == "__main__":
    main()