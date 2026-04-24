import { useState, useRef } from "react"
import axios from "axios"

const API = "http://localhost:8000"

export default function App() {
  const [messages, setMessages] = useState([])
  const [question, setQuestion] = useState("")
  const [uploading, setUploading] = useState(false)
  const [asking, setAsking] = useState(false)
  const [pdfName, setPdfName] = useState(null)
  const fileRef = useRef()

  async function handleUpload(e) {
    const file = e.target.files[0]
    if (!file) return
    setUploading(true)
    const form = new FormData()
    form.append("file", file)
    try {
      const res = await axios.post(`${API}/upload`, form)
      setPdfName(file.name)
      setMessages([{
        role: "system",
        text: `"${file.name}" yüklendi — ${res.data.pages} sayfa, ${res.data.chunks} parça.`
      }])
    } catch {
      alert("Yükleme hatası. Backend çalışıyor mu?")
    }
    setUploading(false)
  }

  async function handleAsk() {
    if (!question.trim() || asking) return
    const q = question.trim()
    setQuestion("")
    setMessages(prev => [...prev, { role: "user", text: q }])
    setAsking(true)
    try {
      const res = await axios.post(`${API}/ask`, { text: q })
      setMessages(prev => [...prev, {
        role: "bot",
        text: res.data.answer,
        sources: res.data.sources
      }])
    } catch {
      setMessages(prev => [...prev, {
        role: "bot",
        text: "Bir hata oluştu, tekrar dene."
      }])
    }
    setAsking(false)
  }

  return (
    <div style={{
      maxWidth: 680, margin: "0 auto", padding: "24px 16px",
      fontFamily: "system-ui, sans-serif", minHeight: "100vh",
      display: "flex", flexDirection: "column", gap: 16
    }}>

      {/* Başlık */}
      <div>
        <h1 style={{ fontSize: 20, fontWeight: 600, margin: 0 }}>PDF Soru-Cevap</h1>
        <p style={{ fontSize: 13, color: "#888", margin: "4px 0 0" }}>
          PDF yükle, sorularını sor
        </p>
      </div>

      {/* PDF yükleme */}
      <div style={{
        border: "1.5px dashed #ddd", borderRadius: 12,
        padding: "20px", textAlign: "center", cursor: "pointer",
        background: pdfName ? "#f6fff9" : "#fafafa"
      }} onClick={() => fileRef.current.click()}>
        <input ref={fileRef} type="file" accept=".pdf"
          style={{ display: "none" }} onChange={handleUpload} />
        {uploading
          ? <p style={{ margin: 0, color: "#888" }}>Yükleniyor...</p>
          : pdfName
            ? <p style={{ margin: 0, color: "#1D9E75", fontWeight: 500 }}>✓ {pdfName}</p>
            : <p style={{ margin: 0, color: "#aaa" }}>PDF seçmek için tıkla</p>
        }
      </div>

      {/* Mesajlar */}
      <div style={{
        flex: 1, display: "flex", flexDirection: "column", gap: 10,
        minHeight: 300
      }}>
        {messages.map((m, i) => (
          <div key={i} style={{
            display: "flex",
            justifyContent: m.role === "user" ? "flex-end" : "flex-start"
          }}>
            <div style={{
              maxWidth: "80%", padding: "10px 14px",
              borderRadius: m.role === "user" ? "16px 16px 4px 16px" : "16px 16px 16px 4px",
              background: m.role === "user" ? "#1D9E75" : m.role === "system" ? "#f0f0f0" : "#f5f5f5",
              color: m.role === "user" ? "#fff" : "#222",
              fontSize: 14, lineHeight: 1.6
            }}>
              {m.text}
              {m.sources && m.sources.length > 0 && (
                <div style={{ marginTop: 6, fontSize: 12, opacity: 0.6 }}>
                  Kaynak sayfa: {m.sources.join(", ")}
                </div>
              )}
            </div>
          </div>
        ))}
        {asking && (
          <div style={{ fontSize: 13, color: "#aaa", paddingLeft: 4 }}>
            Yanıt hazırlanıyor...
          </div>
        )}
      </div>

      {/* Soru kutusu */}
      <div style={{ display: "flex", gap: 8 }}>
        <input
          value={question}
          onChange={e => setQuestion(e.target.value)}
          onKeyDown={e => e.key === "Enter" && handleAsk()}
          placeholder={pdfName ? "Sorunuzu yazın..." : "Önce PDF yükleyin"}
          disabled={!pdfName || asking}
          style={{
            flex: 1, padding: "10px 14px", borderRadius: 10,
            border: "1px solid #ddd", fontSize: 14, outline: "none"
          }}
        />
        <button
          onClick={handleAsk}
          disabled={!pdfName || asking || !question.trim()}
          style={{
            padding: "10px 20px", borderRadius: 10, border: "none",
            background: "#1D9E75", color: "#fff", fontSize: 14,
            cursor: "pointer", fontWeight: 500
          }}
        >
          Gönder
        </button>
      </div>
    </div>
  )
}