import sys
import os
# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# from llm.gemini import get_gemini_client
from llm.deepseek import get_deepseek_client
from utils.DynamicModelBuilder import DynamicModelBuilder, ModelDefinition
import json

def main():
    # JSON definition for CountryInfo model
    country_model_json = {
        "model_name": "CountryInfo",
        "fields": [
            {
                "name": "country",
                "type": "string",
                "description": "The country name",
                "required": True
            },
            {
                "name": "capital",
                "type": "string",
                "description": "The capital city",
                "required": True
            },
            {
                "name": "population",
                "type": "integer",
                "description": "Population of the country",
                "required": True
            },
            {
                "name": "continent",
                "type": "string",
                "description": "The continent the country is in",
                "required": True
            }
        ]
    }
    
    # JSON definition for QuantumConcept model
    quantum_concept_model_json = {
        "model_name": "QuantumConcept",
        "fields": [
            {
                "name": "concept",
                "type": "string",
                "description": "A quantum computing concept",
                "required": True
            },
            {
                "name": "simple_explanation",
                "type": "string",
                "description": "Simple explanation of the concept",
                "required": True
            }
        ]
    }
    
    # JSON definition for QuantumExplanation model (simplified without nested objects)
    quantum_explanation_model_json = {
        "model_name": "QuantumExplanation",
        "fields": [
            {
                "name": "main_idea",
                "type": "string",
                "description": "The main idea of quantum computing",
                "required": True
            },
            {
                "name": "key_concepts",
                "type": "list_string",
                "description": "List of key quantum computing concepts",
                "required": True
            },
            {
                "name": "real_world_applications",
                "type": "list_string",
                "description": "Real world applications",
                "required": True
            }
        ]
    }
    
    # Create ModelDefinition objects
    country_model_def = ModelDefinition(**country_model_json)
    quantum_explanation_model_def = ModelDefinition(**quantum_explanation_model_json)
    
    # Build Pydantic models dynamically
    CountryInfo = DynamicModelBuilder.create_pydantic_model(country_model_def)
    QuantumExplanation = DynamicModelBuilder.create_pydantic_model(quantum_explanation_model_def)
    
    # Example usage with LLM
    # llm = get_gemini_client()
    llm = get_deepseek_client()
    
    print("=== Dynamic Country Information Model ===")
    print(f"Model name: {country_model_def.model_name}")
    print()
    
    # Structured output for country information
    structured_llm = llm.with_structured_output(CountryInfo)
    response = structured_llm.invoke("Tell me about France - its capital, population, and continent")
    print("LLM Response:")
    print(json.dumps(response.model_dump(), indent=2))
    print()
    
    print("=== Dynamic Quantum Explanation Model ===")
    print(f"Model name: {quantum_explanation_model_def.model_name}")
    print()
    
    # Structured output for quantum computing explanation
    quantum_llm = llm.with_structured_output(QuantumExplanation)
    quantum_response = quantum_llm.invoke("Explain quantum computing in simple terms with key concepts and applications")
    print("LLM Response:")
    print(json.dumps(quantum_response.model_dump(), indent=2))

if __name__ == "__main__":
    main()
