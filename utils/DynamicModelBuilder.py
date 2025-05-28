from pydantic import BaseModel, Field, create_model
from typing import List, Dict, Any, Optional
import json
from enum import Enum

class FieldType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST_STRING = "list_string"
    LIST_INTEGER = "list_integer"
    DICT = "dict"
    OPTIONAL_STRING = "optional_string"
    OPTIONAL_INTEGER = "optional_integer"

class FieldDefinition(BaseModel):
    name: str = Field(description="Field name")
    type: FieldType = Field(description="Field type")
    description: str = Field(description="Field description")
    required: bool = Field(default=True, description="Whether field is required")
    default_value: Optional[Any] = Field(default=None, description="Default value")

class ModelDefinition(BaseModel):
    model_name: str = Field(description="Name of the Pydantic model")
    fields: List[FieldDefinition] = Field(description="List of field definitions")

class DynamicModelBuilder:
    @staticmethod
    def type_mapping(field_def: FieldDefinition):
        """Map FieldType to Python types"""
        type_map = {
            FieldType.STRING: str,
            FieldType.INTEGER: int,
            FieldType.FLOAT: float,
            FieldType.BOOLEAN: bool,
            FieldType.LIST_STRING: List[str],
            FieldType.LIST_INTEGER: List[int],
            FieldType.DICT: Dict[str, Any],
            FieldType.OPTIONAL_STRING: Optional[str],
            FieldType.OPTIONAL_INTEGER: Optional[int],
        }
        return type_map.get(field_def.type, str)
    
    @staticmethod
    def create_pydantic_model(model_def: ModelDefinition) -> BaseModel:
        """Create a Pydantic model from ModelDefinition"""
        fields = {}
        
        for field_def in model_def.fields:
            python_type = DynamicModelBuilder.type_mapping(field_def)
            
            if field_def.required and field_def.default_value is None:
                # Required field without default
                fields[field_def.name] = (
                    python_type, 
                    Field(description=field_def.description)
                )
            elif field_def.default_value is not None:
                # Field with default value
                fields[field_def.name] = (
                    python_type, 
                    Field(default=field_def.default_value, description=field_def.description)
                )
            else:
                # Optional field
                fields[field_def.name] = (
                    Optional[python_type], 
                    Field(default=None, description=field_def.description)
                )
        
        return create_model(model_def.model_name, **fields)
        
    @staticmethod
    def _infer_type(value: Any) -> FieldType:
        """Infer FieldType from value"""
        if isinstance(value, str):
            return FieldType.STRING
        elif isinstance(value, int):
            return FieldType.INTEGER
        elif isinstance(value, float):
            return FieldType.FLOAT
        elif isinstance(value, bool):
            return FieldType.BOOLEAN
        elif isinstance(value, list):
            if value and isinstance(value[0], str):
                return FieldType.LIST_STRING
            elif value and isinstance(value[0], int):
                return FieldType.LIST_INTEGER
            else:
                return FieldType.LIST_STRING
        elif isinstance(value, dict):
            return FieldType.DICT
        else:
            return FieldType.STRING

def main():
    model_definition = '''
    {
        "model_name": "ProductInfo",
        "fields": [
            {
                "name": "product_name",
                "type": "string",
                "description": "Name of the product",
                "required": true
            },
            {
                "name": "price",
                "type": "float",
                "description": "Price of the product",
                "required": true
            },
            {
                "name": "categories",
                "type": "list_string",
                "description": "Product categories",
                "required": false,
                "default_value": []
            }
        ]
    }
    '''
    
    # Parse JSON string and create ModelDefinition object
    model_dict = json.loads(model_definition)
    model_def = ModelDefinition(**model_dict)
    
    # Create Pydantic model
    DynamicModel = DynamicModelBuilder.create_pydantic_model(model_def)
    
    # Test the created model
    test_data = {
        "product_name": "Test Product",
        "price": 29.99,
        "categories": ["electronics", "gadgets"]
    }
    
    instance = DynamicModel(**test_data)
    print("Created model instance:")
    print(instance.model_dump())
    print()
    
if __name__ == "__main__":
    main()