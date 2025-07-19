"""
Main FormBuilder application.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from urllib.parse import urlparse

from .parsers import JSONParser, CSVParser, SheetsParser
from .forms_api import GoogleFormsAPI
from .models import FormData


class FormBuilder:
    """Main application class for building Google Forms."""
    
    def __init__(self, credentials_path: Optional[str] = None, token_path: Optional[str] = None):
        """
        Initialize FormBuilder.
        
        Args:
            credentials_path: Path to Google API credentials
            token_path: Path to store OAuth2 token
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.forms_api = None
    
    def _get_forms_api(self) -> GoogleFormsAPI:
        """Get or create Forms API instance."""
        if self.forms_api is None:
            self.forms_api = GoogleFormsAPI(
                credentials_path=self.credentials_path,
                token_path=self.token_path
            )
        return self.forms_api
    
    def detect_input_type(self, source: str) -> str:
        """
        Detect the input type based on source.
        
        Args:
            source: Path to file or URL
            
        Returns:
            Input type: 'json', 'csv', or 'sheets'
        """
        # Check if it's a Google Sheets URL
        if ('docs.google.com' in source and 'spreadsheets' in source) or \
           (len(source) > 20 and '/' not in source):  # Likely a sheet ID
            return 'sheets'
        
        # Check file extension
        if os.path.exists(source):
            path = Path(source)
            ext = path.suffix.lower()
            if ext == '.json':
                return 'json'
            elif ext == '.csv':
                return 'csv'
            else:
                # Try to detect based on content
                try:
                    with open(source, 'r') as f:
                        content = f.read().strip()
                        if content.startswith('[') or content.startswith('{'):
                            return 'json'
                        elif ',' in content:
                            return 'csv'
                except:
                    pass
        
        # Default to JSON if unclear
        return 'json'
    
    def parse_input(self, source: str, input_type: Optional[str] = None) -> FormData:
        """
        Parse input from various sources.
        
        Args:
            source: Path to file or Google Sheets URL
            input_type: Force specific input type ('json', 'csv', 'sheets')
            
        Returns:
            Parsed FormData
        """
        if input_type is None:
            input_type = self.detect_input_type(source)
        
        print(f"📖 Parsing {input_type.upper()} input: {source}")
        
        try:
            if input_type == 'json':
                parser = JSONParser()
                return parser.parse(source)
            
            elif input_type == 'csv':
                parser = CSVParser()
                return parser.parse(source)
            
            elif input_type == 'sheets':
                parser = SheetsParser(credentials_path=self.credentials_path)
                return parser.parse(source)
            
            else:
                raise ValueError(f"Unsupported input type: {input_type}")
                
        except Exception as e:
            raise ValueError(f"Failed to parse {input_type} input: {e}")
    
    def create_form(self, source: str, input_type: Optional[str] = None, 
                   title: Optional[str] = None, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a Google Form from input source.
        
        Args:
            source: Path to file or Google Sheets URL
            input_type: Force specific input type
            title: Override form title
            description: Override form description
            
        Returns:
            Dictionary with form details
        """
        # Parse the input
        form_data = self.parse_input(source, input_type)
        
        # Override title and description if provided
        if title:
            form_data.title = title
        if description:
            form_data.description = description
        
        print(f"📋 Parsed {len(form_data.questions)} questions")
        
        # Create the form
        forms_api = self._get_forms_api()
        result = forms_api.create_form(form_data)
        
        return result
    
    def validate_input(self, source: str, input_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate input without creating a form.
        
        Args:
            source: Path to file or Google Sheets URL
            input_type: Force specific input type
            
        Returns:
            Validation results
        """
        try:
            form_data = self.parse_input(source, input_type)
            
            # Collect validation info
            question_types = {}
            for question in form_data.questions:
                qtype = question.type  # Already a string due to use_enum_values = True
                question_types[qtype] = question_types.get(qtype, 0) + 1
            
            # Check for potential issues
            warnings = []
            
            # Check for questions without options where needed
            for question in form_data.questions:
                if question.type in ['multiple choice', 'checkboxes', 'dropdown']:
                    if not question.options or len(question.options) == 0:
                        warnings.append(f"Question '{question.question}' needs options")
            
            return {
                "valid": True,
                "title": form_data.title,
                "description": form_data.description,
                "question_count": len(form_data.questions),
                "question_types": question_types,
                "warnings": warnings,
                "questions": [
                    {
                        "question": q.question,
                        "type": q.type,
                        "description": q.description,
                        "options": q.options
                    }
                    for q in form_data.questions
                ]
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "question_count": 0,
                "question_types": {},
                "warnings": [],
                "questions": []
            }
    
    def list_forms(self, max_results: int = 10):
        """List recent Google Forms."""
        forms_api = self._get_forms_api()
        return forms_api.list_forms(max_results)
    
    def get_supported_formats(self) -> Dict[str, Dict[str, Any]]:
        """Get information about supported input formats."""
        return {
            "json": {
                "description": "JSON array of question objects",
                "extension": ".json",
                "example": {
                    "structure": "Array of objects",
                    "required_fields": ["question", "type"],
                    "optional_fields": ["description", "options"],
                    "sample": [
                        {
                            "question": "What is your favorite color?",
                            "description": "Choose one from the list",
                            "type": "multiple choice",
                            "options": ["Red", "Green", "Blue"]
                        }
                    ]
                }
            },
            "csv": {
                "description": "CSV file with Question, Description, Type columns",
                "extension": ".csv",
                "example": {
                    "structure": "CSV with headers",
                    "required_columns": ["Question", "Type"],
                    "optional_columns": ["Description"],
                    "type_format": "type: option1, option2, option3",
                    "sample_content": "Question,Description,Type\nWhat is your name?,,short answer\nPick a fruit,Choose one,multiple choice: Apple, Banana"
                }
            },
            "sheets": {
                "description": "Google Sheets with Question, Description, Type columns",
                "extension": "Google Sheets URL or ID",
                "example": {
                    "structure": "Same as CSV but in Google Sheets",
                    "required_columns": ["Question", "Type"],
                    "optional_columns": ["Description"],
                    "type_format": "type: option1, option2, option3",
                    "authentication": "Requires Google API credentials"
                }
            }
        }
    
    def get_question_types(self) -> Dict[str, Dict[str, Any]]:
        """Get information about supported question types."""
        return {
            "short answer": {
                "description": "Single-line text input",
                "options_required": False,
                "google_forms_type": "Short answer text"
            },
            "paragraph": {
                "description": "Multi-line text input",
                "options_required": False,
                "google_forms_type": "Paragraph text"
            },
            "multiple choice": {
                "description": "Single selection from options",
                "options_required": True,
                "google_forms_type": "Multiple choice"
            },
            "checkboxes": {
                "description": "Multiple selections from options",
                "options_required": True,
                "google_forms_type": "Checkboxes"
            },
            "dropdown": {
                "description": "Dropdown selection from options",
                "options_required": True,
                "google_forms_type": "Dropdown"
            }
        } 