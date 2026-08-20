from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import  UploadFile
from fastapi import File
from pypdf import PdfReader
from rag import rag_pipeline,process_pdf
from fastapi import HTTPException
import rag
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


@app.post("/upload")  # post/upload endpoint
async def upload_file(file:UploadFile):# func can perform async operations and client is sending us a file
    if file.content_type!= "application/pdf":
        raise HTTPException(
            status_code=400,
            detail= "Only PDF files are allowed."
        )
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="A filename is required."
        )
    contents = await file.read()  # wait for the uploaded file's contents to be read.
    with open("uploads/" + file.filename, "wb") as f: #open the  destination PDF.
        f.write(contents) #put the pdf data into it.

    try:
        chunk_count = process_pdf("uploads/"+ file.filename)

    except Exception as e:
        print("PDF ERROR:", e)
        raise HTTPException(
            status_code=400,
            detail="Could not process the PDF."
        )
    return {
        "filename": file.filename,
        "chunks": chunk_count
    }    #your file was processed and i created X chunks.

