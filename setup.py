"""
ISA SuperApp Setup Script.

This script is used to install the ISA SuperApp package and its dependencies.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = ""
readme_path = this_directory / "README.md"
if readme_path.exists():
    long_description = readme_path.read_text(encoding='utf-8')

# Read requirements
requirements = []
requirements_path = this_directory / "requirements.txt"
if requirements_path.exists():
    with open(requirements_path, 'r', encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="isa-superapp",
    version="0.1.0",
    author="ISA SuperApp Team",
    author_email="team@isa-superapp.com",
    description="Intelligent System Architecture SuperApp - A comprehensive AI-powered research and analysis platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/isa-superapp/isa-superapp",
    packages=find_packages(exclude=["tests*", "experiments*", "docs*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Indexing",
        "Topic :: Database",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.2.0",
            "sphinx-autodoc-typehints>=1.23.0",
            "myst-parser>=1.0.0",
        ],
        "research": [
            "jupyter>=1.0.0",
            "matplotlib>=3.7.0",
            "seaborn>=0.12.0",
            "plotly>=5.15.0",
            "streamlit>=1.25.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "isa-superapp=isa_superapp.cli:main",
            "isa=isa_superapp.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "isa_superapp": [
            "config/*.yaml",
            "config/*.json",
            "templates/*.yaml",
            "templates/*.json",
        ],
    },
    zip_safe=False,
    keywords=[
        "ai",
        "artificial-intelligence",
        "machine-learning",
        "nlp",
        "natural-language-processing",
        "vector-database",
        "semantic-search",
        "research",
        "analysis",
        "automation",
        "workflow",
        "agents",
        "llm",
        "large-language-models",
        "rag",
        "retrieval-augmented-generation",
        "isa",
        "intelligent-system-architecture",
    ],
    project_urls={
        "Bug Reports": "https://github.com/isa-superapp/isa-superapp/issues",
        "Source": "https://github.com/isa-superapp/isa-superapp",
        "Documentation": "https://isa-superapp.readthedocs.io/",
        "Changelog": "https://github.com/isa-superapp/isa-superapp/blob/main/CHANGELOG.md",
    },
)