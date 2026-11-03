import json
from datetime import datetime, timezone
from pathlib import Path
from google import genai
from google.genai import types
from .config import settings

class LLMService:
    def __init__(self):
        # Pass 30000 milliseconds (30 seconds)
        self.client = genai.Client(
            api_key=settings.gemini_api_key,
            http_options=types.HttpOptions(timeout=30000) 
        )
        self.input_cost_per_m = 0.075 
        self.output_cost_per_m = 0.30
        self.log_file = Path(__file__).resolve().parent / "llm_today_usage.jsonl"

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        input_cost = (prompt_tokens / 1_000_000) * self.input_cost_per_m
        output_cost = (completion_tokens / 1_000_000) * self.output_cost_per_m
        return input_cost + output_cost

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

    def generate_completion(self, prompt: str) -> dict:
        model_name = 'gemini-3.6-flash'
        response = self.client.models.generate_content(
            model=model_name,
            contents=prompt,
        )
        
        # Calculate usage
        usage = response.usage_metadata
        prompt_tokens = usage.prompt_token_count
        completion_tokens = usage.candidates_token_count
        
        # Cost math
        cost = self.calculate_cost(prompt_tokens, completion_tokens)
        
        # Log to llm_usage.jsonl
        self.log_usage(model_name, prompt_tokens, completion_tokens, cost)
        
        return {
            "response": response.text,
            "metrics": {
                "model": model_name,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_cost_usd": cost
            }
        }