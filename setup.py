#!/usr/bin/env python3
"""
Setup script for Google Form Builder.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read requirements
requirements = []
with open('requirements.txt', 'r') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="google-form-builder",
    version="1.0.0",
    description="Generate Google Forms from structured data (JSON, CSV, Google Sheets)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Google Form Builder Team",
    author_email="support@example.com",
    url="https://github.com/your-username/google-form-builder",
    project_urls={
        "Bug Tracker": "https://github.com/your-username/google-form-builder/issues",
        "Documentation": "https://github.com/your-username/google-form-builder/wiki",
        "Source Code": "https://github.com/your-username/google-form-builder",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Office/Business",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    keywords="google forms api automation csv json sheets survey questionnaire",
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.10",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.900",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "google-form-builder=cli:cli",
            "gfb=cli:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "google_form_builder": ["py.typed"],
        "": ["*.md", "*.txt", "*.json"],
    },
    zip_safe=False,
) 