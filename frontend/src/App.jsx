import { useState } from 'react'
import './App.css'

function App() {
  const [file, setFile] = useState(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");


  // Upload PDF to the backend
  const handleUpload = async () => {
    if (!file) {
      alert("Please select a PDF first.")
      return
    }

    alert("Button clicked! Sending PDF...")

    const formData = new FormData()
    formData.append("file", file)

    const response = await fetch("http://127.0.0.1:8000/upload", {
      method: "POST",
      body: formData,
    })

    const data = await response.json()

    alert(JSON.stringify(data))
  }

  // Send question to the RAG backend
  const handleChat = async () => {
    alert("handleChat is running");
    if (!question) {
      alert("Please enter a question.")
      return
    }

    const response = await fetch("http://127.0.0.1:8000/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        question: question,
      }),
    });
    alert("FastAPI responded");

    const data = await response.json()
    setAnswer(data.your_answer);
  }

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

          <button className="clear-btn">
            Clear
          </button>

        </div>

      </header>

      <main className="content">

        <section className="document-panel">

          <h2>Document</h2>

          <div className="document-placeholder">

            <div className="pdf-icon">PDF</div>

            {file ? (
              <>
                <p>{file.name}</p>
                <span>PDF selected</span>
              </>
            ) : (
              <>
                <p>No document uploaded</p>
                <span>Upload a PDF to get started</span>
              </>
            )}

          </div>

        </section>

        <section className="chat-panel">

          <h2>AI Assistant</h2>

          <div className="chat-placeholder">
            <div className="ai-icon">✦</div>

            {answer ? (
              <p>{answer}</p>
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
  )
}

export default App