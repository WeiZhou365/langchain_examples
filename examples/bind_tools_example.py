import sys
import os
# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from llm.gemini import get_gemini_client
import json
from datetime import datetime

# Define tools using @tool decorator
@tool
def get_weather(location: str) -> str:
    """Get the current weather for a location."""
    # Mock weather data - in real app, you'd call a weather API
    weather_data = {
        "new york": "Sunny, 72°F (22°C)",
        "london": "Cloudy, 60°F (15°C)", 
        "tokyo": "Rainy, 68°F (20°C)",
        "paris": "Partly cloudy, 65°F (18°C)",
        "sydney": "Sunny, 78°F (26°C)"
    }
    return weather_data.get(location.lower(), f"Weather data not available for {location}")

@tool
def calculate_tip(bill_amount: float, tip_percentage: float = 18.0) -> str:
    """Calculate tip amount and total bill."""
    tip_amount = bill_amount * (tip_percentage / 100)
    total = bill_amount + tip_amount
    return f"Bill: ${bill_amount:.2f}, Tip ({tip_percentage}%): ${tip_amount:.2f}, Total: ${total:.2f}"

@tool
def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """Convert currency amounts (mock data)."""
    # Mock exchange rates - in real app, you'd use a currency API
    rates = {
        ("USD", "EUR"): 0.85,
        ("USD", "GBP"): 0.73,
        ("USD", "JPY"): 110.0,
        ("EUR", "USD"): 1.18,
        ("GBP", "USD"): 1.37,
        ("JPY", "USD"): 0.009
    }
    
    rate = rates.get((from_currency.upper(), to_currency.upper()))
    if rate:
        converted = amount * rate
        return f"{amount} {from_currency.upper()} = {converted:.2f} {to_currency.upper()}"
    else:
        return f"Exchange rate not available for {from_currency} to {to_currency}"

def demonstrate_bind_tools():
    """Demonstrate three different ways to use bind_tools."""
    
    print("🔧 LangChain bind_tools Example")
    print("="*50)
    
    # Get the LLM
    llm = get_gemini_client()
    
    # Case 1: Basic tool binding and execution
    print("\n📌 Case 1: Basic tool binding with execution")
    tools = [get_weather, calculate_tip]
    llm_with_tools = llm.bind_tools(tools)
    
    query1 = "What's the weather in New York and calculate a 20% tip on a $50 bill?"
    print(f"Query: {query1}")
    
    response1 = llm_with_tools.invoke([HumanMessage(content=query1)])
    print(f"Response: {response1.content}")
    
    if response1.tool_calls:
        print("🛠️ Tool calls made:")
        for tool_call in response1.tool_calls:
            print(f"  - {tool_call['name']}: {tool_call['args']}")
            
            # Execute the tool call
            if tool_call['name'] == 'get_weather':
                result = get_weather.invoke(tool_call['args'])
            elif tool_call['name'] == 'calculate_tip':
                result = calculate_tip.invoke(tool_call['args'])
            
            print(f"    Result: {result}")
    
    print("\n" + "-"*50)
    
    # Case 2: Direct tool return (tool choice forced)
    print("\n📌 Case 2: Direct tool return (forced tool use)")
    llm_forced_tool = llm.bind_tools([convert_currency], tool_choice="convert_currency")
    
    query2 = "I need some help with calculations"
    print(f"Query: {query2}")
    print("(Forcing currency conversion tool)")
    
    response2 = llm_forced_tool.invoke([HumanMessage(content=query2)])
    print(f"Response: {response2.content}")
    
    # This will force the tool to be called even with unrelated query
    if response2.tool_calls:
        print("🛠️ Forced tool call with direct return:")
        tool_call = response2.tool_calls[0]
        print(f"  - {tool_call['name']}: {tool_call['args']}")
        
        # Direct tool execution and return
        result = convert_currency.invoke(tool_call['args'])
        print(f"  Direct result: {result}")
    
    print("\n" + "-"*50)
    
    # Case 3: Multiple tools with conversation flow
    print("\n📌 Case 3: Conversation flow with multiple tools")
    all_tools = [get_weather, calculate_tip, convert_currency]
    llm_with_all_tools = llm.bind_tools(all_tools)
    
    messages = []
    user_query = "What's the weather in London, then convert 100 USD to EUR"
    print(f"Query: {user_query}")
    
    messages.append(HumanMessage(content=user_query))
    response3 = llm_with_all_tools.invoke(messages)
    messages.append(response3)
    
    print(f"Response: {response3.content}")
    
    if response3.tool_calls:
        print("🛠️ Tool calls in conversation:")
        for tool_call in response3.tool_calls:
            print(f"  - {tool_call['name']}: {tool_call['args']}")
            
            # Execute tools and add results to conversation
            tool_result = None
            if tool_call['name'] == 'get_weather':
                tool_result = get_weather.invoke(tool_call['args'])
            elif tool_call['name'] == 'convert_currency':
                tool_result = convert_currency.invoke(tool_call['args'])
            elif tool_call['name'] == 'calculate_tip':
                tool_result = calculate_tip.invoke(tool_call['args'])
            
            print(f"    Result: {tool_result}")
            
            # Add tool result to conversation
            messages.append(ToolMessage(
                content=str(tool_result),
                tool_call_id=tool_call['id']
            ))

def main():
    print("🚀 Starting bind_tools Examples (3 Cases)")
    
    try:
        demonstrate_bind_tools()
        print("\n✅ All three cases completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()