# pip3 install langchain_openai
# python3 deepseek_langchain.py
import os
import dotenv
from langchain_openai.chat_models.base import BaseChatOpenAI

def get_deepseek_client():
    dotenv.load_dotenv()
    api_key = os.getenv("API_KEY")
    model = os.getenv("MODEL")
    llm = BaseChatOpenAI(
        model=model, 
        openai_api_key=api_key,
        openai_api_base='https://ark.cn-beijing.volces.com/api/v3',
    )
    
    return llm

