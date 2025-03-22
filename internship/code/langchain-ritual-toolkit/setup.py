from setuptools import setup, find_packages

setup(
    name="langchain_ritual_toolkit",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "langchain>=0.0.300",
    ],
    python_requires=">=3.8",
)
