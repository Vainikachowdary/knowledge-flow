
import { useState, useEffect } from 'react'
import './App.css'
import ReactMarkdown from "react-markdown";

function App() {
  const [file, setFile] = useState(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");

  // Document management state
  const [documents, setDocuments] = useState([]);
  const [showDocuments, setShowDocuments] = useState(false);

  // Fetch documents from the backend
  const fetchDocuments = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/documents");
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Could not fetch documents.");
      }

      setDocuments(data.documents);

    } catch (error) {
      console.error("Error fetching documents:", error);
    }
  };

  // Fetch documents when the page loads
  useEffect(() => {
    fetchDocuments();
  }, []);

  // Upload PDF to the backend
  const handleUpload = async () => {
    if (!file) {
      alert("Please select a PDF first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://127.0.0.1:8000/upload", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        alert(data.detail || "PDF upload failed.");
        return;
      }

      alert(`Uploaded ${data.filename} successfully. Created ${data.chunks} chunks.`);

      // Refresh document list after successful upload
      await fetchDocuments();

      // Clear selected file
      setFile(null);

    } catch (error) {
      console.error("Upload failed:", error);
      alert("Upload failed: " + error.message);
    }
  };

  const handleDelete = async (documentId) => {
    const confirmDelete = window.confirm(
      "Are you sure you want to delete this document?"
    );

    if (!confirmDelete) return;

    


    try {
      const response = await fetch(
         `http://127.0.0.1:8000/documents/${documentId}`,
         {
          method: "DELETE",

         }         
      );

      const data = await response.json();

      if (!response.ok) {
        alert(data.detail || "Could not delete document.");
        return;
      }

      // Refresh the document list
     await fetchDocuments();
     
     alert("Document deleted successfully.");


  } catch (error) {
    console.error ("Delete failed:", error);
    alert("Delete failed: "+ error.message);

  }
  };

  // Send question to the RAG backend
  const handleChat = async () => {
    if (!question.trim()) {
      alert("Please enter a question.");
      return;
    }

    try {
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: question,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        alert(data.detail || "Something went wrong.");
        return;
      }

      setAnswer(data.your_answer);

    } catch (error) {
      console.error("Chat request failed:", error);
      alert("Chat request failed: " + error.message);
    }
  };

  return (
    <div className="app">

      <header className="header">

        <div>
          <h1>✦ KnowledgeFlow</h1>
          <p>Ask anything from your document</p>
        </div>

        <div className="header-actions">

          <input
            type="file"
            accept=".pdf"
            id="pdf-upload"
            style={{ display: "none" }}
            onChange={(event) => setFile(event.target.files[0])}
          />

          <label htmlFor="pdf-upload" className="upload-btn">
            Upload PDF
          </label>

          <button className="upload-btn" onClick={handleUpload}>
            Send to KnowledgeFlow
          </button>

          <span className="status">● AI Online</span>

          <button
            className="clear-btn"
            onClick={() => {
              setQuestion("");
              setAnswer("");
            }}
          >
            Clear
          </button>

        </div>

      </header>

      <main className="content">

        {/* Document panel */}
        <section className="document-panel">

          <h2>Document</h2>

          <button
            className="document-toggle"
            onClick={() => setShowDocuments(!showDocuments)}
          >
            Your Documents ({documents.length})
            <span>{showDocuments ? "▲" : "▼"}</span>
          </button>

          {showDocuments && (
            <div className="document-list">

              {documents.length > 0 ? (
                documents.map((doc) => (
                  
                  <div key={doc.id} className="document-item">
                   <span>📄 {doc.filename}</span>

                   <button
                     className="delete-btn"
                     onClick={() => handleDelete(doc.id)}
                   >
                     Delete
                   </button>
                 </div>
                ))
              ) : (
                <p>No documents uploaded yet.</p>
              )}

            </div>
          )}

          <div className="document-placeholder">

            <div className="pdf-icon">PDF</div>

            {file ? (
              <>
                <p>{file.name}</p>
                <span>PDF selected</span>
              </>
            ) : (
              <>
                <p>No document selected</p>
                <span>Upload a PDF to get started</span>
              </>
            )}

          </div>

        </section>

        {/* AI Assistant panel */}
        <section className="chat-panel">

          <h2>AI Assistant</h2>

          <div className="chat-placeholder">

            <div className="ai-icon">✦</div>

            {answer ? (
              <ReactMarkdown>{answer}</ReactMarkdown>
            ) : (
              <>
                <p>Ask a question about your document</p>
                <span>Your answer will appear here</span>
              </>
            )}

          </div>

        </section>

      </main>

      <footer className="input-area">

        <input
          type="text"
          placeholder="Ask something about your document..."
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
        />

        <button className="send-btn" onClick={handleChat}>
          →
        </button>

      </footer>

    </div>
  );
}

export default App;
