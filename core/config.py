# core/config.py
import os
import getpass
import warnings
from serpapi import GoogleSearch


def setup_environment():
    """Sets up API keys for Upstage and SerpAPI."""
    warnings.filterwarnings("ignore")
    print("Setting up environment variables...")

    # Set Upstage API key
    if "UPSTAGE_API_KEY" not in os.environ or not os.environ.get("UPSTAGE_API_KEY"):
        try:
            os.environ["UPSTAGE_API_KEY"] = getpass.getpass(
                "Enter your Upstage API key: "
            )
            print("Upstage API key set.")
        except Exception as e:
            print(f"Error setting Upstage API KEY: {e}")
            return False

    # Set SERPAPI KEY
    # SerpAPI 라이브러리는 환경 변수 또는 GoogleSearch.SERP_API_KEY를 참조합니다.
    if "SERPAPI_API_KEY" not in os.environ or not os.environ.get("SERPAPI_API_KEY"):
        try:
            serpapi_key = getpass.getpass("Enter your SERPAPI API key: ")
            os.environ["SERPAPI_API_KEY"] = serpapi_key
            GoogleSearch.SERP_API_KEY = serpapi_key  # 명시적으로 설정
            print("SerpAPI key set.")
        except Exception as e:
            print(f"Error setting SerpAPI API KEY: {e}")
            return False

    return True
