"""
     Setup script for the bcp-calculator package.
"""

from setuptools import setup, find_packages

# Read the contents of README.md for the long description
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="bcp-calculator",
    version="0.1.0",
    description="SDK for calculating Business Complexity Points (BCP) of user stories",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="BCP Team",
    url="https://github.com/flow-ciandt/bcp-agent",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
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
    entry_points={
        "console_scripts": [
            "bcp-calc=src.main:main",
            "bcp-api=src.api.server:run_api",
            "bcp-compare=tests.compare_providers:main"
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
)