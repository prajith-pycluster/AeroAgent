import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

print("DATABASE_URL LOADED =", DATABASE_URL)

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
AVIATION_STACK_API_KEY = os.getenv("AVIATION_STACK_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


def get_llm():
    return ChatGroq(
        model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
    )