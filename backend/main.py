from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import  UploadFile
from fastapi.middleware.cors import CORSMiddleware
from rag import rag_pipeline,process_pdf,remove_pdf
from fastapi import HTTPException
from database import save_document , get_documents , delete_document, get_document, document_exists
from pathlib import Path


import rag
import os
import uuid
import hashlib        

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class chatRequest(BaseModel):
    question : str


#Login endpoint
@app.get("/")
def home():
    return {"message": "Hello World"}

#chat endpoint
@app.post("/chat")
def chat(request: chatRequest):
    if rag.index is None:
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF before asking a question."
        )
    answer = rag_pipeline(request.question)
    return {
        "your_answer": answer
    }


@app.get("/documents")
def documents():
    rows = get_documents()

    documents = []

    for row in rows:
        documents.append({
            "id": row[0],
            "filename": row[1],
            "source": row[2],
            "uploaded_at":row[3]
        })

    return {
        "documents": documents
    }


@app.delete("/documents/{document_id}")
def delete_document_endpoint(document_id: int):
    document = get_document(document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    file_path = document[2]

    # Resolve the physical file path.
    absolute_path = Path(file_path)

    if not absolute_path.is_absolute():
        absolute_path = Path(__file__).resolve().parent / absolute_path

    # Remove this PDF's chunks from the in-memory FAISS index.
    try:
        remove_pdf(file_path)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Index cleanup failed: {str(e)}"
        )

    # Delete the physical PDF.
    try:
        if absolute_path.exists():
            absolute_path.unlink()
    except OSError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Could not delete physical PDF: {str(e)}"
        )

    # Delete the database record.
    try:
        delete_document(document_id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Could not delete document information: {str(e)}"
        )

    return {
        "message": "Document deleted successfully",
        "document_id": document_id
    }


@app.post("/upload")
async def upload_file(file: UploadFile):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="A filename is required."
        )

    contents = await file.read()

    file_hash = hashlib.sha256(contents).hexdigest()

    if document_exists(file_hash):
        raise HTTPException(
            status_code=409,
            detail="This PDF has already been uploaded."
        )

    upload_dir = Path(__file__).resolve().parent / "uploads"
    upload_dir.mkdir(parents = True, exist_ok=True)

    stored_filename = f"{uuid.uuid4()}.pdf"
    file_path = str(upload_dir/ stored_filename)

    print("SAVING PDF TO:", file_path)


    with open(file_path, "wb") as f:
        f.write(contents)


    print("SAVED FILE:", os.path.abspath(file_path))
    print("FILE EXISTS:", os.path.exists(file_path))



    try:
        chunk_count = process_pdf(file_path)

    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)

        raise HTTPException(
            status_code=400,
            detail="Could not process the PDF."
        )





    try:
        save_document(file.filename, file_path, file_hash)

    except Exception as e:
        print("DATABASE ERROR:", e)

        try:
            remove_pdf(file_path)
        except Exception as cleanup_error:
            print("INDEX CLEANUP ERROR:", cleanup_error)

        finally:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except OSError as file_error:
                print("FILE CLEANUP ERROR:", file_error)

        raise HTTPException(
            status_code=500,
            detail="Could not save document information."
        )

    return {
        "filename": file.filename,
        "chunks": chunk_count
    }