"""Debug ChatOpenAI source code."""

import inspect
from langchain_openai import ChatOpenAI

def main():
    """Print ChatOpenAI source code."""
    print("ChatOpenAI init signature:")
    print(inspect.signature(ChatOpenAI.__init__))
    print("\nChatOpenAI fields:")
    print(ChatOpenAI.__fields__.keys())

if __name__ == "__main__":
    main()
