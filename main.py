from fastapi import FastAPI, UploadFile, File, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import io
import csv
import json
from pdf_engine import PDFEngine

app = FastAPI(
    title="Extrator e Sanitizador Automático de PDFs (LGPD)",
    description="API robusta para extração de texto, tabelas estruturadas e sanitização de dados sensíveis sob as diretrizes da LGPD.",
    version="1.0.0"
)

# Enable CORS for local testing/cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate the PDF Engine
pdf_engine = PDFEngine()

# Pydantic models for download payloads
class CSVDownloadRequest(BaseModel):
    table: list[list[str]]
    filename: str

class JSONDownloadRequest(BaseModel):
    data: dict
    filename: str


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "pdf-sanitizer-api"}


@app.post("/api/process")
async def process_pdf(file: UploadFile = File(...)):
    """
    Receives a PDF upload, extracts all structured content (metadata, text, tables)
    and applies regex sanitization with a comprehensive LGPD audit trail.
    """
    # 1. Validation
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400, 
            detail="Arquivo inválido. O sistema suporta apenas documentos no formato PDF."
        )
        
    try:
        # Read the file into memory
        file_bytes = await file.read()
        file_stream = io.BytesIO(file_bytes)
        file_stream.size = len(file_bytes) # Inject size attribute for metadata
        
        # Process PDF
        result = pdf_engine.process_pdf(file_stream)
        result["filename"] = file.filename
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Falha ao processar o arquivo PDF. Detalhes: {str(e)}"
        )


@app.post("/api/download/csv")
async def download_csv(request: CSVDownloadRequest):
    """
    Generates a structured CSV in-memory from a 2D table array.
    Appends a UTF-8 BOM prefix (\\xef\\xbb\\xbf) to ensure seamless rendering
    of Brazilian characters (ç, ã, é) inside Microsoft Excel.
    """
    try:
        output = io.StringIO()
        writer = csv.writer(output, delimiter=";", quoting=csv.QUOTE_MINIMAL)
        writer.writerows(request.table)
        
        csv_content = output.getvalue()
        
        # UTF-8 BOM bytes
        bom = b'\xef\xbb\xbf'
        encoded_content = bom + csv_content.encode("utf-8")
        
        headers = {
            "Content-Disposition": f"attachment; filename={request.filename}"
        }
        
        return Response(
            content=encoded_content,
            media_type="text/csv",
            headers=headers
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar o arquivo CSV. Detalhes: {str(e)}"
        )


@app.post("/api/download/json")
async def download_json(request: JSONDownloadRequest):
    """
    Returns a beautifully structured JSON download of the sanitized data.
    """
    try:
        json_str = json.dumps(request.data, indent=4, ensure_ascii=False)
        encoded_content = json_str.encode("utf-8")
        
        headers = {
            "Content-Disposition": f"attachment; filename={request.filename}"
        }
        
        return Response(
            content=encoded_content,
            media_type="application/json",
            headers=headers
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar o arquivo JSON. Detalhes: {str(e)}"
        )


# Serve Static files. Must be registered AFTER the API routes to avoid route overlaps!
# Serves `./static` at `/`. html=True enables serving `index.html` at `/` automatically.
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
