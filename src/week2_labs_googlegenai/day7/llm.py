from datetime import datetime, timezone
import json
from google import genai
from google.genai import types
from .config import settings
from .schemas import Order
from pathlib import Path

class LLMService:
    def __init__(self):
        self.client = genai.Client(
            api_key=settings.gemini_api_key,
            http_options=types.HttpOptions(timeout=30000)
        )
        self.log_file = Path(__file__).resolve().parent / "llm_today_usage.jsonl"
        
        # Define your pricing rates per million tokens
        self.input_cost_per_m = 0.075 
        self.output_cost_per_m = 0.30

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculates total cost in USD based on token usage."""
        return ((prompt_tokens / 1_000_000) * self.input_cost_per_m) + \
               ((completion_tokens / 1_000_000) * self.output_cost_per_m)

    def log_usage(self, model_name: str, prompt_tokens: int, completion_tokens: int, cost: float):
        """Appends usage metrics to llm_usage.jsonl"""
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": model_name,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_cost_usd": cost
        }
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    def extract_order_from_text(self, document_text: str) -> Order:
        prompt = f"Extract the order details accurately from this purchase order document:\n\n{document_text}"
        model_name = 'gemini-2.5-flash'
        
        response = self.client.models.generate_content(
            model=model_name,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": Order,
            },
        )
        
        # 1. Grab token counts safely
        usage = response.usage_metadata
        if usage:
            prompt_tokens = usage.prompt_token_count
            completion_tokens = usage.candidates_token_count
            
            # 2. Calculate the cost using your pricing rates
            cost = self.calculate_cost(prompt_tokens, completion_tokens)
            
            # 3. Call your log method with all required arguments
            self.log_usage(model_name, prompt_tokens, completion_tokens, cost)
        
        return response.parsed