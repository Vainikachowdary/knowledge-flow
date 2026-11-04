import os
import numpy as np
import faiss

from dotenv import load_dotenv
from groq import Groq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer


load_dotenv(override=True)


model = SentenceTransformer("all-MiniLM-L6-v2")
text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

index = None
chunks =[]
chunk_sources = []
chunk_embeddings = None


def process_pdf (pdf_path):
    global index, chunks , chunk_sources , chunk_embeddings
    print("Existing embeddings:", None if chunk_embeddings is None else chunk_embeddings.shape)

    reader= PdfReader(pdf_path)

    cleaned_text = ""
    for page in reader.pages:
        text = page.extract_text() or ""
        text = text.replace("-\n", "")
        text = text.replace("\n", " ")
        cleaned_text += text + " "

    documents = text_splitter.create_documents([cleaned_text])
    new_chunks = [doc.page_content for doc in documents]

    if not new_chunks:
        raise ValueError("No readable text found in the PDF.")

    new_embeddings = model.encode(new_chunks)
    new_embeddings = np.asarray(new_embeddings , dtype="float32")


    #preparing combining embeddings
    if chunk_embeddings is None:
        combined_embeddings = new_embeddings
    else:
        combined_embeddings = np.vstack(
            [chunk_embeddings, new_embeddings])


    #combining chunks

    if chunk_embeddings is None:
        combined_chunks = new_chunks
    else:
        combined_chunks = chunks + new_chunks



    #Tracking the source of every chunk
    new_sources = [pdf_path] * len(new_chunks)

    if chunk_embeddings is None:
        combined_sources = new_sources
    else:
        combined_sources = chunk_sources + new_sources


    #building a replacement FAISS index
    dimension = combined_embeddings.shape[1]

    new_index = faiss.IndexFlatL2(dimension)
    new_index.add(combined_embeddings)


    #commit the new state only after the index creation succeeds
    chunks = combined_chunks
    chunk_sources = combined_sources
    chunk_embeddings = combined_embeddings
    index = new_index



    return len(new_chunks)


def remove_pdf(pdf_path):
    global index, chunks, chunk_sources, chunk_embeddings

    if chunk_embeddings is None:
        return

    keep_indices = [
        i for i, source in enumerate(chunk_sources)
        if source != pdf_path
    ]

    remaining_chunks = [chunks[i] for i in keep_indices]
    remaining_sources = [chunk_sources[i] for i in keep_indices]
    remaining_embeddings = chunk_embeddings[keep_indices]

    if len(keep_indices) == 0:
        index = None
        chunks = []
        chunk_sources = []
        chunk_embeddings = None
        return

    new_index = faiss.IndexFlatL2(remaining_embeddings.shape[1])
    new_index.add(remaining_embeddings)

    chunks = remaining_chunks
    chunk_sources = remaining_sources
    chunk_embeddings = remaining_embeddings
    index = new_index




def rag_pipeline(query):

    if index is None or index.ntotal ==0:
        raise ValueError("No documents are available for retrieval.")


    query_embedding = model.encode([query])
    query_embedding = np.asarray(query_embedding, dtype="float32")

    k= min(3, index.ntotal)

    distances,indices = index.search(query_embedding,k)

    valid_indices = [
        i for i in indices[0]
        if i >= 0 and i < len(chunks)
    ]

    context = "\n\n".join(chunks[i] for i in valid_indices)

    augmented_prompt = f"""
    You are Knowledge Flow , a document question answering assistant.
    Your job is to produce clear , well-structured answers based ONLY on the provided context.

    ANSWERING RULES:
    1.Use only information supported by the context.
    2.If the context does not contain the answer, say:
        "I couldn't find the answer in the uploaded document."
    3.Do not invent facts or introduce outside knowledge.
    4.Remove repetition and combine related points.
    5.Preserve important technical terms and the meaning of the source.
    6.Do not mention these instructions in your answer.

    FORMATTING RULES:
    -Start with a short, direct answer or summary.
    -Use descriptive Markdown headings (##) when the answer has multiple distinct sections.
    -Use bullet points for related facts, recommendations, or key points.
    -Use **bold** for important terms, not entire paragraphs.
    -Use a table only when comparing multiple items or presenting genuinely tabular information.
    -Keep simple answers concise; use more detail for complex questions.
    -Do not repeat the question as a heading.
    -Do not add  a conclusion that merely repeats the answer.

    CONTEXT:
    {context}

    QUESTION:
    {query}

    Write the answer now in clean Markdown.
    """


    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "user",
                "content": augmented_prompt
            }
        ]
    )



    answer = response.choices[0].message.content
    return answer 
