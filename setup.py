"""
Korean Investment & Securities Trading API Client Setup
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="korea-investment-trading",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Python client for Korean Investment & Securities OpenAPI trading",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/korea-investment-trading",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=[
        "requests>=2.31.0",
        "websockets>=12.0",
        "aiohttp>=3.9.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.5.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.23.0",
            "pytest-cov>=4.1.0",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "mypy>=1.7.0",
        ],
        "ml": [
            "scikit-learn>=1.3.0",
            "ta-lib>=0.4.29",
            "pandas-ta>=0.3.14b",
        ],
        "viz": [
            "matplotlib>=3.8.0",
            "plotly>=5.17.0",
            "seaborn>=0.13.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "kis-trading=korea_investment_trading.cli:main",
        ],
    },
)