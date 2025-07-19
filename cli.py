#!/usr/bin/env python3
"""
Command-line interface for Google Form Builder.
"""

import json
import sys
from pathlib import Path
from typing import Optional

import click
from colorama import init, Fore, Style
from tabulate import tabulate

from google_form_builder import FormBuilder

# Initialize colorama for cross-platform colored output
init()


def print_success(message: str):
    """Print success message in green."""
    click.echo(f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}")


def print_error(message: str):
    """Print error message in red."""
    click.echo(f"{Fore.RED}❌ {message}{Style.RESET_ALL}")


def print_warning(message: str):
    """Print warning message in yellow."""
    click.echo(f"{Fore.YELLOW}⚠️ {message}{Style.RESET_ALL}")


def print_info(message: str):
    """Print info message in blue."""
    click.echo(f"{Fore.BLUE}ℹ️ {message}{Style.RESET_ALL}")


@click.group()
@click.option('--credentials', '-c', type=click.Path(exists=True), 
              help='Path to Google API credentials JSON file')
@click.option('--token', '-t', type=click.Path(), 
              help='Path to store OAuth2 token (default: token.json)')
@click.pass_context
def cli(ctx, credentials: Optional[str], token: Optional[str]):
    """
    Google Form Builder - Create Google Forms from structured data.
    
    Supports input from JSON files, CSV files, and Google Sheets.
    """
    ctx.ensure_object(dict)
    ctx.obj['credentials'] = credentials
    ctx.obj['token'] = token or 'token.json'


@cli.command()
@click.argument('source', type=str)
@click.option('--type', '-t', 'input_type', 
              type=click.Choice(['json', 'csv', 'sheets']),
              help='Force specific input type (auto-detected if not specified)')
@click.option('--title', help='Override form title')
@click.option('--description', help='Override form description')
@click.option('--validate-only', is_flag=True, 
              help='Only validate input without creating form')
@click.pass_context
def create(ctx, source: str, input_type: Optional[str], title: Optional[str], 
          description: Optional[str], validate_only: bool):
    """
    Create a Google Form from input source.
    
    SOURCE can be:
    - Path to JSON file
    - Path to CSV file  
    - Google Sheets URL or ID
    """
    try:
        builder = FormBuilder(
            credentials_path=ctx.obj['credentials'],
            token_path=ctx.obj['token']
        )
        
        if validate_only:
            print_info(f"Validating input: {source}")
            result = builder.validate_input(source, input_type)
            
            if result['valid']:
                print_success("Input validation passed!")
                print(f"Title: {result['title']}")
                if result['description']:
                    print(f"Description: {result['description']}")
                print(f"Questions: {result['question_count']}")
                
                if result['question_types']:
                    print("\nQuestion types:")
                    for qtype, count in result['question_types'].items():
                        print(f"  - {qtype}: {count}")
                
                if result['warnings']:
                    print_warning("Warnings:")
                    for warning in result['warnings']:
                        print(f"  - {warning}")
                
                # Show questions in table format
                if result['questions']:
                    print("\nQuestions preview:")
                    table_data = []
                    for i, q in enumerate(result['questions'][:5], 1):  # Show first 5
                        options = ', '.join(q['options'][:3]) if q['options'] else 'N/A'
                        if q['options'] and len(q['options']) > 3:
                            options += f" (+{len(q['options'])-3} more)"
                        
                        table_data.append([
                            i,
                            q['question'][:50] + ('...' if len(q['question']) > 50 else ''),
                            q['type'],
                            options[:30] + ('...' if len(options) > 30 else '')
                        ])
                    
                    headers = ['#', 'Question', 'Type', 'Options']
                    print(tabulate(table_data, headers=headers, tablefmt='grid'))
                    
                    if len(result['questions']) > 5:
                        print(f"... and {len(result['questions']) - 5} more questions")
            else:
                print_error(f"Input validation failed: {result['error']}")
                sys.exit(1)
        else:
            print_info(f"Creating Google Form from: {source}")
            result = builder.create_form(source, input_type, title, description)
            
            print_success("Google Form created successfully!")
            print(f"📝 Form Title: {result['title']}")
            print(f"📊 Questions: {result['question_count']}")
            print(f"🔗 Edit URL: {result['edit_url']}")
            print(f"👀 View URL: {result['view_url']}")
            
    except Exception as e:
        print_error(f"Failed to process input: {e}")
        sys.exit(1)


@cli.command()
@click.option('--max-results', '-n', default=10, type=int,
              help='Maximum number of forms to list (default: 10)')
@click.pass_context  
def list_forms(ctx, max_results: int):
    """List recent Google Forms."""
    try:
        builder = FormBuilder(
            credentials_path=ctx.obj['credentials'],
            token_path=ctx.obj['token']
        )
        
        print_info("Fetching your recent Google Forms...")
        forms = builder.list_forms(max_results)
        
        if not forms:
            print_warning("No forms found or unable to access Google Drive.")
            return
        
        print_success(f"Found {len(forms)} recent forms:")
        
        table_data = []
        for form in forms:
            created = form.get('created', '')[:10] if form.get('created') else 'Unknown'
            table_data.append([
                form['title'][:40] + ('...' if len(form['title']) > 40 else ''),
                created,
                form.get('url', 'N/A')[:50] + ('...' if len(form.get('url', '')) > 50 else '')
            ])
        
        headers = ['Title', 'Created', 'URL']
        print(tabulate(table_data, headers=headers, tablefmt='grid'))
        
    except Exception as e:
        print_error(f"Failed to list forms: {e}")
        sys.exit(1)


@cli.command()
def formats():
    """Show supported input formats and examples."""
    builder = FormBuilder()
    formats_info = builder.get_supported_formats()
    
    print_info("Supported Input Formats")
    print("=" * 50)
    
    for format_name, info in formats_info.items():
        print(f"\n{Fore.CYAN}📄 {format_name.upper()}{Style.RESET_ALL}")
        print(f"Description: {info['description']}")
        print(f"Extension: {info['extension']}")
        
        if 'example' in info:
            example = info['example']
            print(f"Structure: {example['structure']}")
            
            if 'required_columns' in example:
                print(f"Required columns: {', '.join(example['required_columns'])}")
            if 'optional_columns' in example:
                print(f"Optional columns: {', '.join(example['optional_columns'])}")
            if 'type_format' in example:
                print(f"Type format: {example['type_format']}")
            
            if 'sample' in example:
                print("Sample JSON:")
                print(json.dumps(example['sample'], indent=2))
            elif 'sample_content' in example:
                print("Sample content:")
                print(example['sample_content'])


@cli.command()
def types():
    """Show supported question types."""
    builder = FormBuilder()
    types_info = builder.get_question_types()
    
    print_info("Supported Question Types")
    print("=" * 50)
    
    table_data = []
    for qtype, info in types_info.items():
        table_data.append([
            qtype,
            info['description'],
            'Yes' if info['options_required'] else 'No',
            info['google_forms_type']
        ])
    
    headers = ['Type', 'Description', 'Options Required', 'Google Forms Type']
    print(tabulate(table_data, headers=headers, tablefmt='grid'))


@cli.command()
@click.argument('output_path', type=click.Path())
@click.option('--format', 'output_format', type=click.Choice(['json', 'csv']),
              default='json', help='Output format (default: json)')
def example(output_path: str, output_format: str):
    """Generate example input files."""
    
    sample_questions = [
        {
            "question": "What is your full name?",
            "description": "Please enter your first and last name",
            "type": "short answer"
        },
        {
            "question": "Tell us about yourself",
            "description": "Write a brief description",
            "type": "paragraph"
        },
        {
            "question": "What is your favorite programming language?",
            "description": "Choose one from the list",
            "type": "multiple choice",
            "options": ["Python", "JavaScript", "Java", "C++", "Go", "Rust"]
        },
        {
            "question": "Which technologies do you use?",
            "description": "Select all that apply",
            "type": "checkboxes",
            "options": ["React", "Vue", "Angular", "Django", "Flask", "FastAPI", "Docker", "Kubernetes"]
        },
        {
            "question": "What is your experience level?",
            "description": "",
            "type": "dropdown",
            "options": ["Beginner", "Intermediate", "Advanced", "Expert"]
        }
    ]
    
    output_path = Path(output_path)
    
    try:
        if output_format == 'json':
            if not output_path.suffix:
                output_path = output_path.with_suffix('.json')
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(sample_questions, f, indent=2, ensure_ascii=False)
        
        elif output_format == 'csv':
            if not output_path.suffix:
                output_path = output_path.with_suffix('.csv')
            
            import csv
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Question', 'Description', 'Type'])
                
                for q in sample_questions:
                    if q.get('options'):
                        type_str = f"{q['type']}: {', '.join(q['options'])}"
                    else:
                        type_str = q['type']
                    
                    writer.writerow([
                        q['question'],
                        q.get('description', ''),
                        type_str
                    ])
        
        print_success(f"Example {output_format.upper()} file created: {output_path}")
        print_info(f"You can now test with: python cli.py create {output_path}")
        
    except Exception as e:
        print_error(f"Failed to create example file: {e}")
        sys.exit(1)


if __name__ == '__main__':
    cli() 