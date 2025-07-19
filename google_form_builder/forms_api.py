"""
Google Forms API integration.
"""

import os
from typing import Dict, Any, Optional, List
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .models import FormData, Question, QuestionType


class GoogleFormsAPI:
    """Google Forms API client."""
    
    # Required scopes for Forms API
    SCOPES = [
        'https://www.googleapis.com/auth/forms.body',
        'https://www.googleapis.com/auth/drive'
    ]
    
    def __init__(self, credentials_path: Optional[str] = None, token_path: Optional[str] = None):
        """
        Initialize the Forms API client.
        
        Args:
            credentials_path: Path to service account JSON or OAuth2 credentials
            token_path: Path to store OAuth2 token (for user authentication)
        """
        self.credentials_path = credentials_path
        self.token_path = token_path or "token.json"
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google APIs."""
        creds = None
        
        # Try service account authentication first
        if self.credentials_path and Path(self.credentials_path).exists():
            try:
                creds = ServiceAccountCredentials.from_service_account_file(
                    self.credentials_path, scopes=self.SCOPES
                )
                print("✅ Authenticated using service account")
            except Exception as e:
                print(f"⚠️ Service account authentication failed: {e}")
        
        # Fall back to OAuth2 flow
        if not creds:
            creds = self._oauth2_flow()
        
        if not creds:
            raise ValueError("Authentication failed. Please provide valid credentials.")
        
        try:
            self.service = build('forms', 'v1', credentials=creds)
            print("✅ Google Forms API client initialized")
        except Exception as e:
            raise ValueError(f"Failed to initialize Forms API: {e}")
    
    def _oauth2_flow(self) -> Optional[Credentials]:
        """Handle OAuth2 authentication flow."""
        creds = None
        
        # Check if we have a saved token
        if os.path.exists(self.token_path):
            try:
                creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
            except Exception:
                pass
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception:
                    creds = None
            
            if not creds:
                if not self.credentials_path:
                    print("❌ No credentials provided. Please provide either:")
                    print("   1. Service account JSON file path")
                    print("   2. OAuth2 client credentials JSON file path")
                    return None
                
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                    print("✅ OAuth2 authentication completed")
                except Exception as e:
                    print(f"❌ OAuth2 flow failed: {e}")
                    return None
            
            # Save the credentials for the next run
            try:
                with open(self.token_path, 'w') as token:
                    token.write(creds.to_json())
                print(f"✅ Token saved to {self.token_path}")
            except Exception as e:
                print(f"⚠️ Failed to save token: {e}")
        
        return creds
    
    def create_form(self, form_data: FormData) -> Dict[str, Any]:
        """
        Create a Google Form from FormData.
        
        Args:
            form_data: The form data to create
            
        Returns:
            Dictionary containing form details including URL and ID
        """
        if not self.service:
            raise ValueError("API client not initialized")
        
        try:
            # Create the form
            form = {
                "info": {
                    "title": form_data.title,
                    "description": form_data.description or ""
                }
            }
            
            print(f"🚀 Creating form: {form_data.title}")
            result = self.service.forms().create(body=form).execute()
            form_id = result['formId']
            
            # Add questions to the form
            self._add_questions(form_id, form_data.questions)
            
            # Get the form URL
            form_url = f"https://docs.google.com/forms/d/{form_id}/edit"
            view_url = f"https://docs.google.com/forms/d/{form_id}/viewform"
            
            print(f"✅ Form created successfully!")
            print(f"📝 Edit URL: {form_url}")
            print(f"👀 View URL: {view_url}")
            
            return {
                "form_id": form_id,
                "edit_url": form_url,
                "view_url": view_url,
                "title": form_data.title,
                "question_count": len(form_data.questions)
            }
            
        except HttpError as e:
            raise ValueError(f"Google Forms API error: {e}")
        except Exception as e:
            raise ValueError(f"Failed to create form: {e}")
    
    def _add_questions(self, form_id: str, questions: List[Question]):
        """Add questions to the form."""
        requests = []
        
        for i, question in enumerate(questions):
            request = self._create_question_request(question, i)
            requests.append(request)
        
        if requests:
            batch_update = {
                "requests": requests
            }
            
            print(f"📋 Adding {len(questions)} questions...")
            self.service.forms().batchUpdate(
                formId=form_id, 
                body=batch_update
            ).execute()
            print(f"✅ All questions added successfully")
    
    def _create_question_request(self, question: Question, index: int) -> Dict[str, Any]:
        """Create a request to add a question to the form."""
        location = {"index": index}
        
        # Base question structure
        question_item = {
            "title": question.question,
            "description": question.description or "",
            "required": False  # You can make this configurable
        }
        
        # Add question type and options
        if question.type == QuestionType.SHORT_ANSWER:
            question_item["textQuestion"] = {
                "paragraph": False
            }
        
        elif question.type == QuestionType.PARAGRAPH:
            question_item["textQuestion"] = {
                "paragraph": True
            }
        
        elif question.type == QuestionType.MULTIPLE_CHOICE:
            options = []
            for option in question.options or []:
                options.append({
                    "value": option
                })
            
            question_item["choiceQuestion"] = {
                "type": "RADIO",
                "options": options
            }
        
        elif question.type == QuestionType.CHECKBOXES:
            options = []
            for option in question.options or []:
                options.append({
                    "value": option
                })
            
            question_item["choiceQuestion"] = {
                "type": "CHECKBOX",
                "options": options
            }
        
        elif question.type == QuestionType.DROPDOWN:
            options = []
            for option in question.options or []:
                options.append({
                    "value": option
                })
            
            question_item["choiceQuestion"] = {
                "type": "DROP_DOWN",
                "options": options
            }
        
        return {
            "createItem": {
                "item": question_item,
                "location": location
            }
        }
    
    def list_forms(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        List recent forms (requires Drive API).
        
        Args:
            max_results: Maximum number of forms to return
            
        Returns:
            List of form metadata
        """
        try:
            # Build Drive API service
            drive_service = build('drive', 'v3', credentials=self.service._http.credentials)
            
            # Search for Google Forms
            results = drive_service.files().list(
                q="mimeType='application/vnd.google-apps.form'",
                pageSize=max_results,
                fields="files(id, name, createdTime, webViewLink)"
            ).execute()
            
            forms = results.get('files', [])
            
            formatted_forms = []
            for form in forms:
                formatted_forms.append({
                    'id': form['id'],
                    'title': form['name'],
                    'created': form.get('createdTime', ''),
                    'url': form.get('webViewLink', '')
                })
            
            return formatted_forms
            
        except Exception as e:
            print(f"⚠️ Failed to list forms: {e}")
            return [] 