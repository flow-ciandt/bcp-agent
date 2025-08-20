"""
Setup script for the bcp-calculator package.
"""

from setuptools import setup, find_packages

setup(
    name="bcp-calculator",
    version="0.1.0",
    description="SDK for calculating Business Complexity Points (BCP) of user stories",
    author="BCP Team",
    packages=find_packages(),
    install_requires=[
        "langchain>=0.1.0",
        "langchain-openai>=0.0.5",
        "openai>=1.3.0",
        "langchain-anthropic>=0.1.1",
        "anthropic>=0.8.0",
        "jinja2>=3.1.2",
        "python-dotenv>=1.0.0",
        "fastapi>=0.103.0",
        "uvicorn>=0.23.0",
        "requests>=2.28.0",
        "pydantic>=2.0.0",
    ],
    python_requires=">=3.10",
)