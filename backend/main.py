from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import  UploadFile
from rag import rag_pipeline,process_pdf
from fastapi import HTTPException
from database import save_document , get_documents , delete_document, get_document
import rag
import os
app = FastAPI()

class chatRequest(BaseModel):
    question : str


#Login endpoint
@app.get("/")
def home():
    return {"message": "Hello World"}

#chat endpoint
@app.post("/chat")
def chat(request: chatRequest):  #This function expects one chatRequest

    if rag.index is None:
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF before asking a question."
        )

    answer=rag_pipeline(request.question)
    return{
        "your_answer": answer
    }




@app.get("/pdfs/{pdf-id}")
def get_pdf(pdf_id: int):
    return{
        "pdf_id": pdf_id
    }


@app.get("/search")
def search(query:str):
    return {
        "search": query
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
        "documents": rows
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

    if os.path.exists(file_path):
        os.remove(file_path)

    delete_document(document_id)

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

    with open("uploads/" + file.filename, "wb") as f:
        f.write(contents)

    # Process the PDF
    try:
        chunk_count = process_pdf("uploads/" + file.filename)

    except Exception as e:
        print("PDF ERROR:", e)
        raise HTTPException(
            status_code=400,
            detail="Could not process the PDF."
        )

    # Save document information to PostgreSQL
    try:
        save_document(
            file.filename,
            "uploads/" + file.filename
        )

    except Exception as e:
        print("DATABASE ERROR:", e)
        raise HTTPException(
            status_code=500,
            detail="Could not save document information."
        )

    return {
        "filename": file.filename,
        "chunks": chunk_count
    }