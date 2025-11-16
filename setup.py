"""Setup script for Multimodal Enterprise RAG System."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="multimodal-rag",
    version="1.0.0",
    description="Multimodal Enterprise RAG System with Knowledge Graphs and Hybrid Search",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/multimodal-rag",
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.10",
    install_requires=[
        "langchain>=0.1.0",
        "langchain-community>=0.0.10",
        "langchain-openai>=0.0.2",
        "llama-index>=0.9.48",
        "openai>=1.10.0",
        "deepeval>=0.20.0",
        "ragas>=0.1.0",
        "pytest>=7.4.0",
        "pytest-asyncio>=0.21.0",
        "qdrant-client>=1.7.0",
        "sentence-transformers>=2.3.0",
        "neo4j>=5.16.0",
        "Pillow>=10.0.0",
        "pytesseract>=0.3.10",
        "transformers>=4.30.0",
        "torch>=2.0.0",
        "torchvision>=0.15.0",
        "openai-whisper>=20231117",
        "pydub>=0.25.1",
        "librosa>=0.10.0",
        "opencv-python>=4.8.0",
        "moviepy>=1.0.3",
        "scenedetect[opencv]>=0.6.0",
        "pypdf>=4.0.0",
        "python-docx>=1.0.0",
        "spacy>=3.7.0",
        "nltk>=3.8.0",
        "rank-bm25>=0.2.2",
        "streamlit>=1.31.0",
        "streamlit-agraph>=0.0.45",
        "plotly>=5.18.0",
        "pandas>=2.0.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.6.0",
        "pydantic-settings>=2.1.0",
        "tenacity>=8.2.0",
        "loguru>=0.7.0",
        "tqdm>=4.66.0",
        "scikit-learn>=1.3.0",
    ],
    extras_require={
        "dev": [
            "black>=24.1.1",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
            "ipython>=8.20.0",
            "jupyter>=1.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "multimodal-rag=src.cli:main",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)

