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

#### Option A: Service Account (Recommended for automation)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable **Google Forms API** and **Google Drive API**
4. Create a **Service Account** 
5. Download the JSON credentials file
6. Save it as `credentials.json` in the project root
   
   A template is provided in `credentials_example.json`

#### Option B: OAuth2 Client (For interactive use)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create **OAuth2 credentials** for Desktop application
3. Download the JSON file
4. Use it with the `--credentials` flag

### 3. Create Your First Form

```bash
# Generate an example file
python cli.py example examples/my_questions.json

# Validate the input
python cli.py create examples/my_questions.json --validate-only

# Create the Google Form
python cli.py create examples/my_questions.json --credentials credentials.json
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

**Made with ❤️ by the Google Form Builder team**
