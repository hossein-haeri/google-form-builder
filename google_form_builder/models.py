"""
Data models for Google Form Builder.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, validator


class QuestionType(str, Enum):
    """Supported question types for Google Forms."""
    SHORT_ANSWER = "short answer"
    PARAGRAPH = "paragraph"
    MULTIPLE_CHOICE = "multiple choice"
    CHECKBOXES = "checkboxes"
    DROPDOWN = "dropdown"


class Question(BaseModel):
    """A question model with validation."""
    
    question: str = Field(..., min_length=1, description="The question text")
    description: Optional[str] = Field("", description="Optional description for the question")
    type: QuestionType = Field(QuestionType.MULTIPLE_CHOICE, description="The question type")
    options: Optional[List[str]] = Field(None, description="Options for choice-based questions")
    
    @validator('question')
    def question_must_not_be_empty(cls, v):
        """Validate that question is not empty after stripping whitespace."""
        if not v.strip():
            raise ValueError('Question cannot be empty')
        return v.strip()
    
    @validator('description')
    def clean_description(cls, v):
        """Clean and validate description."""
        if v is None:
            return ""
        return v.strip()
    
    @validator('type', pre=True)
    def normalize_type(cls, v):
        """Normalize and validate question type."""
        if isinstance(v, str):
            v = v.strip().lower()
            # Map common variations
            type_mapping = {
                'text': QuestionType.SHORT_ANSWER,
                'short_answer': QuestionType.SHORT_ANSWER,
                'long_answer': QuestionType.PARAGRAPH,
                'textarea': QuestionType.PARAGRAPH,
                'radio': QuestionType.MULTIPLE_CHOICE,
                'select': QuestionType.DROPDOWN,
                'checkbox': QuestionType.CHECKBOXES,
                'multi_select': QuestionType.CHECKBOXES,
            }
            
            if v in type_mapping:
                return type_mapping[v]
            
            # Try to find exact match
            for question_type in QuestionType:
                if v == question_type.value:
                    return question_type
            
            # Default to multiple choice if invalid
            return QuestionType.MULTIPLE_CHOICE
        
        return v
    
    @validator('options')
    def validate_options(cls, v, values):
        """Validate options based on question type."""
        question_type = values.get('type')
        
        if question_type in [QuestionType.MULTIPLE_CHOICE, QuestionType.CHECKBOXES, QuestionType.DROPDOWN]:
            if not v or len(v) == 0:
                raise ValueError(f'{question_type.value} questions must have at least one option')
            
            # Clean and validate options
            cleaned_options = []
            for option in v:
                if isinstance(option, str) and option.strip():
                    cleaned_options.append(option.strip())
            
            if not cleaned_options:
                raise ValueError(f'{question_type.value} questions must have at least one valid option')
            
            return cleaned_options
        
        # For short answer and paragraph, options should be None or empty
        return None
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True


class FormData(BaseModel):
    """Container for form data with validation."""
    
    title: str = Field("Untitled Form", description="The form title")
    description: Optional[str] = Field("", description="Form description")
    questions: List[Question] = Field(..., min_items=1, description="List of questions")
    
    @validator('title')
    def clean_title(cls, v):
        """Clean form title."""
        return v.strip() if v else "Untitled Form"
    
    @validator('description')
    def clean_description(cls, v):
        """Clean form description."""
        return v.strip() if v else ""
    
    @validator('questions')
    def validate_questions(cls, v):
        """Validate that we have at least one question."""
        if not v:
            raise ValueError('Form must have at least one question')
        return v 