from fastapi import FastAPI, UploadFile, File, HTTPException, status
import io
from pypdf import PdfReader
from .llm import LLMService

app = FastAPI()
llm_service = LLMService()

@app.post("/extract")
async def extract_purchase_order(file: UploadFile = File(...)):
    # 1. Validate file type (Optional check for PDFs)
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Please upload a PDF file."
        )

    try:
        # 2. Read file bytes and extract text programmatically
        contents = await file.read()
        pdf_file = io.BytesIO(contents)
        reader = PdfReader(pdf_file)
        
        document_text = ""
        for page in reader.pages:
            document_text += page.extract_text() or ""
            
        if not document_text.strip():
            raise ValueError("The uploaded PDF contains no readable text.")

        # 3. Attempt LLM extraction and Pydantic validation (with math reconciliation)
        structured_order = llm_service.extract_order_from_text(document_text)
        
        return {
            "status": "success",
            "filename": file.filename,
            "data": structured_order
        }
        
    except ValueError as ve:
        # Catches Pydantic validation errors, math reconciliation failures, or empty text
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation failed: {str(ve)}"
        )
    except Exception as e:
        # Catches LLM client errors, network timeouts, or PDF reading crashes
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Extraction error: {str(e)}"
        )