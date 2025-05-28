import sys
import os
# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.tools import tool
from langchain import hub
from llm.gemini import get_gemini_client
import requests
from datetime import datetime
from langchain_core.prompts import PromptTemplate

# Define custom tools using @tool decorator
@tool
def get_current_time() -> str:
    """Get the current time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@tool
def calculate_math(expression: str) -> str:
    """Calculate a mathematical expression. Use Python syntax."""
    try:
        # For safety, only allow basic math operations
        allowed_chars = set('0123456789+-*/().= ')
        if all(c in allowed_chars for c in expression):
            result = eval(expression)
            return str(result)
        else:
            return "Error: Invalid characters in expression"
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def search_wikipedia(query: str) -> str:
    """Search Wikipedia for information about a topic."""
    try:
        # Simple Wikipedia API call
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return f"Title: {data.get('title', 'N/A')}\nSummary: {data.get('extract', 'No summary available')}"
        else:
            return f"Could not find information about {query}"
    except Exception as e:
        return f"Error searching Wikipedia: {str(e)}"

# Define the React prompt template directly
REACT_PROMPT_TEMPLATE = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""

def main():
    # Get the LLM
    llm = get_gemini_client()
    
    # Tools are now just the decorated functions
    tools = [get_current_time, calculate_math, search_wikipedia]
    
    # Create prompt from template
    prompt = PromptTemplate.from_template(REACT_PROMPT_TEMPLATE)
    
    print("Using local prompt template")
    
    # Create the React agent
    agent = create_react_agent(llm, tools, prompt)
    
    # Create agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5
    )
    
    # Example queries
    queries = [
        "What time is it right now?",
        # "Calculate 15 * 23 + 42",
        # "Tell me about quantum computing from Wikipedia",
        # "What's the current time and calculate 100 divided by 4?"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'='*50}")
        print(f"Query {i}: {query}")
        print('='*50)
        
        try:
            result = agent_executor.invoke({"input": query})
            print(f"\nFinal Answer: {result['output']}")
        except Exception as e:
            print(f"Error: {str(e)}")
        
        print("\n" + "-"*50)

if __name__ == "__main__":
    main()