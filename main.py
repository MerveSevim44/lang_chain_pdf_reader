# Standard library
import os
import shutil

# Third-party libraries
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# LangChain libraries
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


load_dotenv()

app = FastAPI()

# React'in farklı port'tan istek atmasına izin ver
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite'nin portu
    allow_methods=["*"],
    allow_headers=["*"],
)

# Embedding modelini bir kez yükle — her istekte yeniden yükleme
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Global chain — upload sonrası burada tutulur
qa_chain = None

@app.get("/")
def root():
    """API'nin mevcut olduğunu doğrula."""
    return {
        "message": "PDF Q&A API çalışıyor! 🚀",
        "endpoints": {
            "docs": "http://127.0.0.1:8000/docs",
            "upload": "POST /upload - PDF yükle",
            "ask": "POST /ask - Soru sor"
        }
    }

def build_chain(index_path: str):
    """FAISS index'ten QA chain oluştur."""
    vectorstore = FAISS.load_local(
        index_path,
        embeddings,
        allow_dangerous_deserialization=True
    )
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
    prompt = PromptTemplate(
        template="""Aşağıdaki bağlamı kullanarak soruyu Türkçe yanıtla.
Cevap bağlamda yoksa "Bu bilgi belgede yer almıyor" de.

Bağlam:
{context}

Soru: {question}

Cevap:""",
        input_variables=["context", "question"]
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    
    # Chain'i basitleştir: sadece prompt + llm
    chain = prompt | llm
    
    # Wrapper to maintain compatibility with old API
    class ChainWrapper:
        def __init__(self, chain, retriever):
            self.chain = chain
            self.retriever = retriever
        
        def invoke(self, input_dict):
            query = input_dict.get("query", "")
            
            # Retriever'ı manual çağır (string geçir)
            source_docs = self.retriever.invoke(query)
            
            # Context'i format et (list of docs → string)
            context_str = "\n\n".join([doc.page_content for doc in source_docs])
            
            # Chain'i çalıştır
            result_text = self.chain.invoke({
                "context": context_str,
                "question": query
            })
            
            # Result'ı string'e çevir
            if hasattr(result_text, 'content'):
                result_str = result_text.content
            elif isinstance(result_text, dict):
                result_str = result_text.get('result', str(result_text))
            else:
                result_str = str(result_text)
            
            return {
                "result": result_str,
                "source_documents": source_docs
            }
    
    return ChainWrapper(chain, retriever)

# Uygulama başlarken önceki index varsa yükle
if os.path.exists("faiss_index"):
    qa_chain = build_chain("faiss_index")
    print("Mevcut index yüklendi.")


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """PDF al → indexle → kaydet → chain'i güncelle."""
    global qa_chain

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Sadece PDF yükleyebilirsin.")

    # PDF'i diske kaydet
    pdf_path = f"uploaded_{file.filename}"
    with open(pdf_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Indexle
    loader = PyMuPDFLoader(pdf_path)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local("faiss_index")

    # Chain'i yenile
    qa_chain = build_chain("faiss_index")

    # Geçici PDF dosyasını sil
    os.remove(pdf_path)

    return {
        "message": "PDF başarıyla yüklendi.",
        "pages": len(docs),
        "chunks": len(chunks)
    }


class Question(BaseModel):
    text: str

@app.post("/ask")
async def ask(question: Question):
    """Soru al → chain'den cevap al → döndür."""
    try:
        if qa_chain is None:
            raise HTTPException(status_code=400, detail="Önce bir PDF yükle.")

        result = qa_chain.invoke({"query": question.text})

        # Kaynak sayfaları topla
        sources = list(set([
            str(doc.metadata.get("page", "?"))
            for doc in result["source_documents"]
        ]))

        return {
            "answer": result["result"],
            "sources": sources
        }
    except Exception as e:
        print(f"[ERROR] /ask endpoint'inde hata: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Hata: {str(e)}")