"""
Setup configuration for the BigQuery Table Export CLI.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bq-table-export",
    version="0.1.0",
    description="A CLI tool for exporting BigQuery tables to CSV files in Google Cloud Storage",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/EddieAtGoogle/bq-table-export",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "rich>=10.0.0",
        "requests>=2.25.0",
        "google-auth>=2.0.0",
        "google-auth-oauthlib>=0.4.0",
        "structlog>=23.1.0",
    ],
    entry_points={
        "console_scripts": [
            "bq-export=bq_export.cli:cli",
        ],
    },
) 