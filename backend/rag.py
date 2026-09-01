import os
from dotenv import load_dotenv
from groq import Groq
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv(override=True)
key = os.environ.get("GROQ_API_KEY")

print("Key loaded:", bool(key))
print("Key starts with:", key[:4] if key else "NONE")
print("Key length:", len(key) if key else 0)


from pypdf import PdfReader
import faiss

from sentence_transformers import SentenceTransformer
    
model = SentenceTransformer("all-MiniLM-L6-v2")
text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )


index=None
chunks = []

def process_pdf(pdf_path):
    global index, chunks
    
    reader = PdfReader(pdf_path)



#cleaning

    cleaned_text=""
    
    for page in reader.pages:
        text= page.extract_text()
        text = text.replace("-\n","")
        text= text.replace("\n"," ")
        cleaned_text += text + " "
        

    documents = text_splitter.create_documents([cleaned_text], metadatas=[{"source": pdf_path}])
    chunks = [doc.page_content for doc in documents]


    

  
    
    
#embedding

    embeddings = model.encode(chunks) #take the chunks and turn it into an embedding vector


























    
  


    
#creating FAISS index

    dimension = embeddings.shape[1]
    
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)


    return len(chunks)
    

    


def rag_pipeline(query):

    query_embedding = model.encode([query])
    distances ,indices = index.search(query_embedding,3)


# AUGMENTATION

    context = "\n\n".join(chunks[i] for i in indices[0])

    augmented_prompt = f"""
    Answer the question using the following context.

    If the answer cannot be found in the context,sat:
    "I couldn't find the answer in the uploaded document."

    Do not make up information or use outside knowledge.
    
    Context:
    {context}
    
    Question:
    {query}
    """
    
    

#Groq generation 

    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))   #CREATES CONNECTION TO GROQ
    
    response = client.chat.completions.create(     #Sends our augmented_prompt to the LLM and asks it to generate a response
        model = "openai/gpt-oss-120b",
        messages=[
            {
                "role":"user",
                "content": augmented_prompt
            }
        ]
    )
    
    answer = response.choices[0].message.content #take the actual answer out of Groq's response
    
    return answer
    
