"""
Setup configuration for the BigQuery Export application.
This allows the package to be installed in development mode.
"""

from setuptools import setup, find_packages

setup(
    name="bq-table-export",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "flask>=2.3.3",
        "flask-cors>=4.0.0",
        "google-cloud-bigquery>=3.11.4",
        "google-cloud-storage>=2.10.0",
        "pydantic>=2.3.0",
        "structlog>=23.1.0",
    ],
    extras_require={
        "test": [
            "pytest",
            "pytest-asyncio",
            "pytest-cov",
        ],
    },
) 