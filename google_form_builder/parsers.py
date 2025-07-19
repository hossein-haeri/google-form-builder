"""
Parsers for different input formats.
"""

import json
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

import pandas as pd
import gspread
from google.auth.exceptions import RefreshError

from .models import Question, FormData, QuestionType


class BaseParser(ABC):
    """Base class for all parsers."""
    
    @abstractmethod
    def parse(self, source: str) -> FormData:
        """Parse the source and return FormData."""
        pass
    
    def _parse_type_and_options(self, type_str: str) -> tuple[str, List[str]]:
        """
        Parse type string that may contain options.
        
        Examples:
        - "short answer" -> ("short answer", [])
        - "multiple choice: Apple, Banana, Cherry" -> ("multiple choice", ["Apple", "Banana", "Cherry"])
        - "checkboxes: "New York, NY", "Los Angeles, CA"" -> ("checkboxes", ["New York, NY", "Los Angeles, CA"])
        """
        if not type_str:
            return QuestionType.MULTIPLE_CHOICE.value, []
        
        type_str = type_str.strip()
        
        if ':' not in type_str:
            return type_str, []
        
        parts = type_str.split(':', 1)
        question_type = parts[0].strip()
        options_str = parts[1].strip()
        
        # Parse options - handle both quoted and unquoted
        options = []
        if options_str:
            # Try to split by comma, but respect quotes
            current_option = ""
            in_quotes = False
            quote_char = None
            
            i = 0
            while i < len(options_str):
                char = options_str[i]
                
                if not in_quotes and char in ['"', "'"]:
                    in_quotes = True
                    quote_char = char
                elif in_quotes and char == quote_char:
                    in_quotes = False
                    quote_char = None
                elif not in_quotes and char == ',':
                    if current_option.strip():
                        # Remove surrounding quotes if present
                        option = current_option.strip()
                        if option.startswith('"') and option.endswith('"'):
                            option = option[1:-1]
                        elif option.startswith("'") and option.endswith("'"):
                            option = option[1:-1]
                        options.append(option.strip())
                    current_option = ""
                    i += 1
                    continue
                else:
                    current_option += char
                
                i += 1
            
            # Add the last option
            if current_option.strip():
                option = current_option.strip()
                if option.startswith('"') and option.endswith('"'):
                    option = option[1:-1]
                elif option.startswith("'") and option.endswith("'"):
                    option = option[1:-1]
                options.append(option.strip())
        
        return question_type, options


class JSONParser(BaseParser):
    """Parser for JSON input files."""
    
    def parse(self, source: str) -> FormData:
        """
        Parse JSON file and return FormData.
        
        Args:
            source: Path to JSON file
            
        Returns:
            FormData object
        """
        file_path = Path(source)
        if not file_path.exists():
            raise FileNotFoundError(f"JSON file not found: {source}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
        
        if not isinstance(data, list):
            raise ValueError("JSON must contain a list of questions")
        
        questions = []
        for i, item in enumerate(data):
            if not isinstance(item, dict):
                raise ValueError(f"Question {i+1} must be an object")
            
            try:
                question = Question(**item)
                questions.append(question)
            except Exception as e:
                raise ValueError(f"Error parsing question {i+1}: {e}")
        
        return FormData(
            title=f"Form from {file_path.stem}",
            questions=questions
        )


class CSVParser(BaseParser):
    """Parser for CSV input files."""
    
    def parse(self, source: str) -> FormData:
        """
        Parse CSV file and return FormData.
        
        Args:
            source: Path to CSV file
            
        Returns:
            FormData object
        """
        file_path = Path(source)
        if not file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {source}")
        
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {e}")
        
        return self._parse_dataframe(df, f"Form from {file_path.stem}")
    
    def _parse_dataframe(self, df: pd.DataFrame, title: str) -> FormData:
        """Parse a pandas DataFrame into FormData."""
        # Normalize column names (case-insensitive)
        df.columns = df.columns.str.strip().str.lower()
        
        # Check for required columns
        required_cols = {'question', 'type'}
        available_cols = set(df.columns)
        
        if not required_cols.issubset(available_cols):
            missing = required_cols - available_cols
            raise ValueError(f"Missing required columns: {missing}")
        
        questions = []
        for idx, row in df.iterrows():
            try:
                question_text = str(row['question']).strip()
                if not question_text or question_text.lower() == 'nan':
                    continue
                
                description = ""
                if 'description' in df.columns:
                    desc = str(row['description']).strip()
                    if desc.lower() != 'nan':
                        description = desc
                
                type_str = str(row['type']).strip()
                question_type, options = self._parse_type_and_options(type_str)
                
                question = Question(
                    question=question_text,
                    description=description,
                    type=question_type,
                    options=options if options else None
                )
                questions.append(question)
                
            except Exception as e:
                raise ValueError(f"Error parsing row {idx+1}: {e}")
        
        if not questions:
            raise ValueError("No valid questions found in the data")
        
        return FormData(title=title, questions=questions)


class SheetsParser(BaseParser):
    """Parser for Google Sheets."""
    
    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize with optional credentials path.
        
        Args:
            credentials_path: Path to Google service account credentials JSON
        """
        self.credentials_path = credentials_path
        self._gc = None
    
    def _get_client(self):
        """Get authenticated gspread client."""
        if self._gc is None:
            try:
                if self.credentials_path:
                    self._gc = gspread.service_account(filename=self.credentials_path)
                else:
                    # Try to use default credentials
                    self._gc = gspread.service_account()
            except Exception as e:
                raise ValueError(f"Failed to authenticate with Google Sheets: {e}")
        return self._gc
    
    def parse(self, source: str) -> FormData:
        """
        Parse Google Sheets and return FormData.
        
        Args:
            source: Google Sheets URL or ID
            
        Returns:
            FormData object
        """
        # Extract sheet ID from URL if needed
        sheet_id = self._extract_sheet_id(source)
        
        try:
            gc = self._get_client()
            sheet = gc.open_by_key(sheet_id)
            worksheet = sheet.get_worksheet(0)  # Use first worksheet
            
            # Get all values and convert to DataFrame
            values = worksheet.get_all_values()
            if not values:
                raise ValueError("Sheet is empty")
            
            df = pd.DataFrame(values[1:], columns=values[0])  # First row as headers
            
            return self._parse_dataframe(df, sheet.title)
            
        except RefreshError:
            raise ValueError("Authentication failed. Please check your credentials.")
        except Exception as e:
            raise ValueError(f"Error accessing Google Sheet: {e}")
    
    def _extract_sheet_id(self, source: str) -> str:
        """Extract sheet ID from URL or return as-is if already an ID."""
        # If it's already just an ID (no URL parts), return it
        if '/' not in source and len(source) > 20:
            return source
        
        # Extract from URL patterns
        url_patterns = [
            r'/spreadsheets/d/([a-zA-Z0-9-_]+)',
            r'docs\.google\.com.*[/=]([a-zA-Z0-9-_]{30,})',
        ]
        
        for pattern in url_patterns:
            match = re.search(pattern, source)
            if match:
                return match.group(1)
        
        raise ValueError(f"Could not extract sheet ID from: {source}")
    
    def _parse_dataframe(self, df: pd.DataFrame, title: str) -> FormData:
        """Parse a pandas DataFrame into FormData."""
        # Use the same logic as CSVParser
        csv_parser = CSVParser()
        return csv_parser._parse_dataframe(df, title) 