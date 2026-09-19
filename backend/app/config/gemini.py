import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

api_key = (os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or "").strip()

llm = None
if api_key and api_key != "DUMMY_KEY" and not api_key.startswith("DUMMY"):
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.3
        )
    except Exception as e:
        print("Notice: Failed to initialize Gemini LLM:", e)
        llm = None