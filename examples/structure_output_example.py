import sys
import os
# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.gemini import get_gemini_client
from pydantic import BaseModel, Field
from typing import List
import json

# Define Pydantic models for structured output
class CountryInfo(BaseModel):
    country: str = Field(description="The country name")
    capital: str = Field(description="The capital city")
    population: int = Field(description="Population of the country")
    continent: str = Field(description="The continent the country is in")

class QuantumConcept(BaseModel):
    concept: str = Field(description="A quantum computing concept")
    simple_explanation: str = Field(description="Simple explanation of the concept")

class QuantumExplanation(BaseModel):
    main_idea: str = Field(description="The main idea of quantum computing")
    key_concepts: List[QuantumConcept] = Field(description="List of key concepts")
    real_world_applications: List[str] = Field(description="Real world applications")

def main():
    # Example usage
    llm = get_gemini_client()
    
    # Structured output for country information
    structured_llm = llm.with_structured_output(CountryInfo)
    response = structured_llm.invoke("Tell me about France - its capital, population, and continent")
    print(json.dumps(response.model_dump(), indent=2))
    print()    
    # Structured output for quantum computing explanation
    quantum_llm = llm.with_structured_output(QuantumExplanation)
    quantum_response = quantum_llm.invoke("Explain quantum computing in simple terms with key concepts and applications")
    print(json.dumps(quantum_response.model_dump(), indent=2))
if __name__ == "__main__":
    main()