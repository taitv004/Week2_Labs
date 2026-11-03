from fastapi import FastAPI
from pydantic import BaseModel
from .llm import LLMService

app = FastAPI(title="Capstone LLM Backend - Day 6")
llm = LLMService()

class CompletionRequest(BaseModel):
    prompt: str

@app.get("/health")
def health_check():
    """Pulse check for container and local monitoring."""
    return {"status": "healthy", "service": "LLM API"}

@app.post("/complete")
def complete(request: CompletionRequest):
    """Takes a prompt, calls the LLM, logs metrics, and returns the response."""
    result = llm.generate_completion(request.prompt)
    return {"response": result}