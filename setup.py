from setuptools import setup, find_packages

setup(
    name="sovereignty-score",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "streamlit",
        "pandas",
        "duckdb",
        "flask",
        "flask-cors",
        "bcrypt"
    ],
) 