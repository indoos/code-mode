"""Setup script for code-mode Python package."""

from setuptools import setup, find_packages

setup(
    name="code-mode",
    version="1.0.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
)
