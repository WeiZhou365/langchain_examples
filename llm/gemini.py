import os
import dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

def get_gemini_client():
    dotenv.load_dotenv()
    api_key = os.getenv("API_KEY")
    model = os.getenv("MODEL", "gemini-1.5-flash")  # fallback to gemini-1.5-flash if MODEL not set
    
    # Create Gemini LLM using LangChain
    llm = ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        temperature=0.7,
        max_tokens=1000
    )
    
    return llm



