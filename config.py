import os
from dotenv import load_dotenv

load_dotenv()


def _get_val(key: str, default: str = "") -> str:
    val = os.getenv(key)
    if val:
        return val
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    return default


DATABASE_URL = _get_val("DATABASE_URL")
print("DATABASE_URL LOADED =", DATABASE_URL)

TAVILY_API_KEY = _get_val("TAVILY_API_KEY", "")
AVIATION_STACK_API_KEY = _get_val("AVIATION_STACK_API_KEY", "")
OPENWEATHER_API_KEY = _get_val("OPENWEATHER_API_KEY", "")
GROQ_API_KEY = _get_val("GROQ_API_KEY", "")
GEMINI_API_KEY = _get_val("GEMINI_API_KEY") or _get_val("GOOGLE_API_KEY", "")


def get_llm(model_override: str = None):
    """
    Returns an instantiated LangChain Chat model.
    Prioritizes Groq if a Groq key is present, with automatic model sanitization.
    """
    # 1. Groq Integration
    if GROQ_API_KEY and GROQ_API_KEY.startswith("gsk_"):
        from langchain_groq import ChatGroq
        model_name = model_override or _get_val("GROQ_MODEL", "openai/gpt-oss-120b")

        # Sanitize any old/deprecated model names
        if "llama" in model_name.lower():
            model_name = "openai/gpt-oss-120b"

        return ChatGroq(
            model=model_name,
            groq_api_key=GROQ_API_KEY,
            temperature=0.3,
        )

    # 2. Google Gemini Integration
    gemini_key = GEMINI_API_KEY or (GROQ_API_KEY if GROQ_API_KEY.startswith(("AQ.", "AIza")) else "")
    if gemini_key:
        from langchain_google_genai import ChatGoogleGenerativeAI
        model_name = model_override or os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
        if "2.5" in model_name:
            model_name = "gemini-3.8-flash"

        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=gemini_key,
            temperature=0.3,
        )

    # 3. Default fallback
    from langchain_groq import ChatGroq
    return ChatGroq(
        model="openai/gpt-oss-120b",
        groq_api_key=GROQ_API_KEY if GROQ_API_KEY else None,
    )
