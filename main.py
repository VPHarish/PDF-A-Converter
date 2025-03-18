import os
import shutil
import uuid
from pathlib import Path

import ocrmypdf
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse

# Create app
app = FastAPI(title="PDF to PDF/A Converter")

# Create upload and output directories
UPLOAD_DIR = Path("./uploads")
OUTPUT_DIR = Path("./outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

@app.post("/convert/", description="Convert PDF to PDF/A with OCR")
async def convert_pdf(file: UploadFile = File(...)):
    # Validate file is a PDF
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    # Generate unique filenames
    file_id = str(uuid.uuid4())
    input_file_path = UPLOAD_DIR / f"{file_id}_input.pdf"
    output_file_path = OUTPUT_DIR / f"{file_id}_output.pdf"
    
    try:
        # Save uploaded file
        with open(input_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process the PDF using OCRmyPDF
        ocrmypdf.ocr(
            input_file=str(input_file_path),
            output_file=str(output_file_path),
            output_type="pdfa",
            force_ocr=True,
            skip_text=False,
            deskew=True,
            clean=True
        )
        
        # Return the converted file
        return FileResponse(
            path=output_file_path,
            filename=f"converted_{file.filename}",
            media_type="application/pdf"
        )
    
    except ocrmypdf.exceptions.PriorOcrFoundError:
        # If OCR already exists, try without force_ocr
        try:
            ocrmypdf.ocr(
                input_file=str(input_file_path),
                output_file=str(output_file_path),
                output_type="pdfa",
                skip_text=True,
                optimize=1,
                force_ocr=False
            )
            return FileResponse(
                path=output_file_path,
                filename=f"converted_{file.filename}",
                media_type="application/pdf"
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"OCR conversion error: {str(e)}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
    
    finally:
        # Clean up the input file
        if input_file_path.exists():
            input_file_path.unlink()

@app.on_event("shutdown")
def clean_up_files():
    """Clean up temporary files on shutdown"""
    for file in UPLOAD_DIR.glob("*"):
        file.unlink()
    for file in OUTPUT_DIR.glob("*"):
        file.unlink()