# 🚀 Google Form Builder

A powerful Python tool that automatically generates Google Forms from structured data sources. Support for JSON files, CSV files, and Google Sheets with intelligent question type detection and validation.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-brightgreen.svg)

## ✨ Features

- 📄 **Multiple Input Formats**: JSON, CSV, and Google Sheets
- 🎯 **Smart Type Detection**: Automatically detects question types and validates options
- 🔧 **Flexible Configuration**: Support for all Google Forms question types
- 🚀 **CLI Interface**: Easy-to-use command-line interface with colored output
- 📊 **Validation**: Comprehensive input validation before form creation
- 🔐 **Secure Authentication**: Support for both service account and OAuth2 authentication
- 📋 **Batch Processing**: Process multiple questions at once with intelligent parsing

## 🏗️ Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/your-username/google-form-builder.git
cd google-form-builder

# Install dependencies
pip install -r requirements.txt
```

### 2. Set Up Google API Credentials

You need Google API credentials to create forms. Choose one of these methods:

#### Option A: OAuth2 Client (Recommended for testing)
⚠️ **Important Note**: This method might not work if:
- Your Google account is managed by an organization
- Your organization restricts access to unverified apps
- Your organization blocks OAuth access to Google Forms
- You're using a Google Workspace account with strict policies

Best when you want to:
- Create forms under your personal Google account (gmail.com)
- Test the tool during development
- Create forms for personal use
- Have forms show up in your Google Drive

Steps:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable **Google Forms API** and **Google Drive API**
4. Configure OAuth Consent Screen:
   - Go to "APIs & Services" > "OAuth consent screen"
   - Choose "External" user type
   - Fill in required fields under "App information":
     - App name (e.g., "Google Form Builder")
     - User support email (your email)
     - Developer contact email (your email)
   - Skip "App domain" section (not needed for local use)
   - Click "Save and Continue"
   - On "Scopes" page:
     - Click "Add or Remove Scopes"
     - Add these scopes:
       - `https://www.googleapis.com/auth/forms.body`
       - `https://www.googleapis.com/auth/drive`
     - Click "Save and Continue"
   - On "Test users" page:
     - Click "Add Users"
     - Add your Google email address
     - Click "Save and Continue"

5. Create OAuth Client ID:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop Application"
   - Give it a name (e.g., "Google Form Builder Desktop")
   - Download the JSON file and save as `credentials.json`

When you first run the tool:
```bash
python cli.py --credentials credentials.json create examples/sample_questions.json
```
It will:
1. Open your browser
2. Show "App is not verified" warning (expected for development)
3. Click "Continue" to proceed
4. Choose your Google account
5. Grant the requested permissions
6. Save the token for future use

#### Common Issues and Solutions

1. **"App is not verified" warning**
   - This is normal for development
   - Click "Continue" (or "Advanced" > "Go to {App Name}")
   - Only you can access the app as a test user

2. **"Error 403: access_denied"**
   - Make sure you completed OAuth consent screen setup
   - Verify you added your email as a test user
   - Check that you added both required scopes
   - If using a managed Google account:
     - Try with a personal Gmail account instead
     - Contact your IT admin for permissions
     - Consider using Service Account method (Option B)

3. **"Invalid client" error**
   - Ensure you chose "Desktop Application" type
   - Download fresh credentials and try again

4. **"Failed to create form" error**
   - Check that both Forms API and Drive API are enabled
   - Verify you granted all permissions in consent screen
   - Try revoking access and authenticating again:
     1. Go to [Google Account Security](https://myaccount.google.com/security)
     2. Find the app under "Third-party apps with account access"
     3. Remove access and try again
   - If error persists:
     - Your account might have restrictions
     - Try with a personal Gmail account
     - Switch to Service Account method if available

5. **Token Issues**
   - If you see authentication errors, delete `token.json`
   - Run the command again to re-authenticate

#### Option B: Service Account (Advanced - requires Google Workspace)
Only available if you have a Google Workspace account with admin access. Service Accounts cannot directly create forms without domain-wide delegation.

If you need to use a Service Account:
1. You must have a Google Workspace account
2. Configure domain-wide delegation for the service account
3. Grant necessary OAuth scopes:
   - https://www.googleapis.com/auth/forms
   - https://www.googleapis.com/auth/drive
4. Set up user impersonation

For most users, we recommend using Option A (OAuth2) instead.

### 3. Create Your First Form

```bash

# Validate one of the examples
python cli.py create examples/sample_questions.json --validate-only

# Create a Google Form from the example
python cli.py --credentials credentials.json create examples/sample_questions.json
```

## 📋 Supported Input Formats

### 1. JSON Format

Create a JSON file with an array of question objects:

```json
[
  {
    "question": "What is your favorite color?",
    "description": "Choose one from the list",
    "type": "multiple choice",
    "options": ["Red", "Green", "Blue", "Yellow"]
  },
  {
    "question": "Enter your full name",
    "description": "First and last name",
    "type": "short answer"
  },
  {
    "question": "Tell us about yourself",
    "description": "Brief description",
    "type": "paragraph"
  }
]
```

**Required fields**: `question`, `type`  
**Optional fields**: `description`, `options`

### 2. CSV Format

Create a CSV file with these columns:

```csv
Question,Description,Type
What is your name?,,short answer
Pick your favorite food,Choose one,multiple choice: Pizza, Sushi, Pasta
Choose hobbies,Select multiple,checkboxes: Reading, Gaming, Cooking
```

**Required columns**: `Question`, `Type` (case-insensitive)  
**Optional columns**: `Description`

For choice-based questions, use the format: `type: option1, option2, option3`

### 3. Google Sheets Format

Create a Google Sheet with the same structure as the CSV format:

| Question | Description | Type |
|----------|-------------|------|
| What is your name? | | short answer |
| Pick a fruit | Choose one | multiple choice: Apple, Banana, Cherry |
| Your hobbies | | checkboxes: Reading, Music, Gaming |

**To use**: Share the sheet and copy the URL or sheet ID.

## 🎯 Supported Question Types

| Type | Description | Options Required | Google Forms Equivalent |
|------|-------------|------------------|------------------------|
| `short answer` | Single-line text input | No | Short answer text |
| `paragraph` | Multi-line text input | No | Paragraph text |
| `multiple choice` | Single selection from options | Yes | Multiple choice |
| `checkboxes` | Multiple selections from options | Yes | Checkboxes |
| `dropdown` | Dropdown selection from options | Yes | Dropdown |

### Type Variations and Aliases

The tool accepts these common variations:
- `text` → `short answer`
- `long_answer`, `textarea` → `paragraph`
- `radio` → `multiple choice`
- `checkbox`, `multi_select` → `checkboxes`
- `select` → `dropdown`

## 🖥️ Command Line Interface

### Basic Commands

```bash
# Create a form from JSON file
python cli.py create questions.json

# Create a form from CSV file  
python cli.py create questions.csv

# Create a form from Google Sheets
python cli.py create "https://docs.google.com/spreadsheets/d/your-sheet-id"

# Specify credentials file
python cli.py create questions.json --credentials /path/to/credentials.json

# Override form title and description
python cli.py create questions.json --title "My Custom Form" --description "Form description"

# Validate input without creating form
python cli.py create questions.json --validate-only
```

### Advanced Commands

```bash
# Force specific input type
python cli.py create data.txt --type csv

# List your recent Google Forms
python cli.py list-forms --max-results 20

# Show supported formats
python cli.py formats

# Show supported question types
python cli.py types

# Generate example files
python cli.py example sample.json
python cli.py example sample.csv --format csv
```

### Global Options

```bash
--credentials, -c    Path to Google API credentials JSON file
--token, -t         Path to store OAuth2 token (default: token.json)
--help              Show help message
```

## 📁 Project Structure

```
google-form-builder/
├── google_form_builder/          # Main package
│   ├── __init__.py              # Package initialization
│   ├── models.py                # Data models and validation
│   ├── parsers.py               # Input format parsers
│   ├── forms_api.py             # Google Forms API integration
│   └── app.py                   # Main application class
├── examples/                     # Example input files
│   ├── sample_questions.json    # JSON example
│   └── sample_questions.csv     # CSV example
├── credentials_example.json     # Credentials template
├── cli.py                       # Command-line interface
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🔧 Configuration Examples

### Environment Variables

```bash
# Set default credentials path
export GOOGLE_CREDENTIALS_PATH="credentials.json"

# Set default token storage path
export GOOGLE_TOKEN_PATH="/path/to/token.json"
```

### Programmatic Usage

```python
from google_form_builder import FormBuilder

# Initialize with credentials
builder = FormBuilder(credentials_path="credentials.json")

# Create form from JSON file
result = builder.create_form("questions.json")
print(f"Form created: {result['edit_url']}")

# Validate input first
validation = builder.validate_input("questions.csv")
if validation['valid']:
    result = builder.create_form("questions.csv")
else:
    print(f"Validation failed: {validation['error']}")
```

## 🚨 Common Issues and Solutions

### Authentication Errors

**Problem**: `Authentication failed` error
**Solution**: 
1. Ensure APIs are enabled in Google Cloud Console
2. Check that credentials file path is correct
3. Verify service account has necessary permissions

### Permission Errors

**Problem**: `Insufficient permissions` error
**Solution**:
1. For service accounts: Enable Google Forms API and Google Drive API
2. For OAuth2: Grant necessary scopes during authorization

### Input Validation Errors

**Problem**: `Question type validation failed`
**Solution**:
1. Use `--validate-only` flag to check input first
2. Ensure choice-based questions have options
3. Check that CSV/Sheets format matches expected structure

### CSV Parsing Issues

**Problem**: Options not parsing correctly
**Solution**:
1. Use quotes for options containing commas: `"New York, NY"`
2. Ensure format: `type: option1, option2, option3`
3. Check column headers are exactly: `Question`, `Description`, `Type`

## 📊 Examples

### Complete JSON Example

```json
[
  {
    "question": "What is your experience level?",
    "description": "Select your overall programming experience",
    "type": "dropdown",
    "options": ["Beginner", "Intermediate", "Advanced", "Expert"]
  },
  {
    "question": "Which technologies do you use?",
    "description": "Select all that apply",
    "type": "checkboxes",
    "options": ["Python", "JavaScript", "React", "Django", "Docker"]
  },
  {
    "question": "Describe your ideal project",
    "description": "Tell us about the type of project you'd love to work on",
    "type": "paragraph"
  }
]
```

### Complete CSV Example

```csv
Question,Description,Type
What is your name?,Enter your full name,short answer
What is your email?,We'll use this for updates,short answer
Tell us about your background,Share your experience and skills,paragraph
What's your favorite language?,Choose your preferred programming language,multiple choice: Python, JavaScript, Java, C++, Go
Which frameworks do you know?,Select all you're familiar with,checkboxes: React, Vue, Angular, Django, Flask
What's your experience level?,Choose the option that best describes you,dropdown: Beginner, Intermediate, Advanced, Expert
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📧 Email: support@example.com
- 💬 Issues: [GitHub Issues](https://github.com/your-username/google-form-builder/issues)
- 📖 Documentation: [Wiki](https://github.com/your-username/google-form-builder/wiki)

## 🙏 Acknowledgments

- Google Forms API team for the excellent API
- Python community for amazing libraries
- Contributors and users for feedback and improvements

---

**by Hossein Haeri**
