import logging
from Week2_Labs_googlegenai.src.week2_labs_googlegenai.day6.config import settings
from google import genai
from google.genai import types

# Turn on X-ray vision for the network library
logging.basicConfig(
    format="%(levelname)s [%(name)s] %(message)s",
    level=logging.DEBUG
)
logging.getLogger("httpx").setLevel(logging.DEBUG)
logging.getLogger("httpcore").setLevel(logging.DEBUG)

print("Starting SDK Network Trace...")

client = genai.Client(
    api_key=settings.gemini_api_key,
    http_options=types.HttpOptions(timeout=10.0)
)

try:
    client.models.generate_content(
        model='gemini-1.5-flash',
        contents='Hello'
    )
except Exception as e:
    print("\nCRASH:", type(e).__name__)