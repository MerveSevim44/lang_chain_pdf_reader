# 📄 PDF Soru-Cevap Sistemi (LangChain PDF Reader)

Yapay zeka ile PDF belgelerine akıllı sorular sorup yanıtlar alın. Bu proje, LangChain, Groq LLM ve vektör arama teknolojisini kullanarak PDF'ler üzerinde gerçek zamanlı Q&A işlemleri gerçekleştirir.

## 🎯 Proje Özeti

Bu uygulama, kullanıcılara şu işlemleri yapma imkanı tanır:
- 📤 **PDF Yükleme**: Belgeler doğrudan arayüzden yüklenebilir
- 💬 **Akıllı Sorular**: PDF içeriği hakkında doğal dilde sorular sorun
- 🔍 **Bağlama Dayalı Yanıtlar**: Yapay zeka, sadece belgeden ilgili bilgileri kullanarak yanıt verir
- 🚀 **Hızlı İşleme**: FAISS vektör veritabanı sayesinde milisaniyeler içinde arama yapılır

## 🏗️ Mimari

```
┌─────────────────────────────────────────────────────────────┐
│                    WEB ARAYÜZÜ (React + Vite)              │
│              http://localhost:5173                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  PDF Yükleme  │  Soru Giriş  │  Yanıtlar Görüntüle  │  │
│  └──────────────────────────────────────────────────────┘  │
│                         ↕ HTTP/JSON                         │
├─────────────────────────────────────────────────────────────┤
│                   REST API (FastAPI)                        │
│              http://localhost:8000                          │
├─────────────────────────────────────────────────────────────┤
│                     İŞLEME KATMANI                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ PDF Yükleme  │→ │ Chunk Ayırma │→ │ Embedding Oluşt  │  │
│  │ (PyMuPDF)    │  │ (RecCharSplit)  │ (HuggingFace)    │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
│           ↓                                      ↓           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  FAISS Vektör Veritabanı (Hızlı Benzerlik Araması)  │  │
│  └──────────────────────────────────────────────────────┘  │
│           ↓                                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  LLM (Groq - llama-3.3-70b) - Yanıt Üretme          │  │
│  └──────────────────────────────────────────────────────┘  │
```

## 🔄 İş Akışı

### 1. **Eğitim (Vektörleştirme) - day2.py**
```
PDF Belgesi
    ↓
PyMuPDF ile Sayfa Okuma
    ↓
Chunk'lara Bölme (500 karakter + 50 karakter overlap)
    ↓
HuggingFace Embeddings (sentence-transformers/all-MiniLM-L6-v2)
    ↓
FAISS İndeks Oluşturma & Kaydetme
    ↓
faiss_index/ klasörü
```

### 2. **Sorgulanma - main.py & Frontend**
```
Kullanıcı Sorusu
    ↓
FastAPI /ask Endpoint
    ↓
FAISS'den Benzer Chunk'ları Getir (Top-3)
    ↓
Groq LLM'e Gönder (Bağlam + Soru)
    ↓
Türkçe Yanıt Oluştur
    ↓
Kullanıcıya Göster
```

## 📋 Dosya Yapısı

```
lang_chain_pdf_reader/
├── README.md                 # Bu dosya
├── requirements.txt          # Python bağımlılıkları
├── main.py                   # FastAPI sunucusu (✨ ANA DOSYA)
├── day2.py                   # PDF'i işleyip FAISS indeksi oluştur
├── day3.py                   # Groq entegrasyonu örneği
├── test.py                   # Temel testler
├── test_api.py               # API testleri
├── faiss_index/              # Oluşturulan vektör indeksi (otomatik)
│   └── index.faiss
└── pdf-ask-answer/           # React Frontend
    ├── package.json
    └── frontend/
        ├── src/
        │   ├── App.jsx       # Ana React bileşeni
        │   ├── App.css
        │   ├── main.jsx
        │   └── index.css
        ├── vite.config.js
        ├── tailwind.config.js
        └── package.json
```

## 🚀 Kurulum & Çalıştırma

### Gereksinimler
- Python 3.9+
- Node.js 16+
- Groq API Key

### 1. Backend Kurulumu

```bash
# Proje dizinine git
cd lang_chain_pdf_reader

# Virtual environment oluştur
python -m venv venv

# Virtual environment'ı etkinleştir
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# .env dosyası oluştur
echo GROQ_API_KEY=your_key_here > .env
```

### 2. PDF Vektörleştirme (İlk Çalışma)

```bash
# PDF'i yükle ve FAISS indeksi oluştur
python day2.py

# ✨ Çıktı:
# PDF okunuyor...
#   → X sayfa yüklendi
# Parçalara bölünüyor...
#   → Y parça oluşturuldu
# Vektörler hesaplanıyor...
#   → faiss_index/ klasörüne kaydedildi
```

### 3. Backend Sunucusu Başlat

```bash
# FastAPI sunucusunu başlat
python main.py

# Tarayıcıda aç:
# http://127.0.0.1:8000/docs (API dokümantasyonu)
```

### 4. Frontend Kurulumu & Başlatma

```bash
# Frontend dizinine git
cd pdf-ask-answer/frontend

# Bağımlılıkları yükle
npm install

# Development sunucusu başlat
npm run dev

# Tarayıcıda aç:
# http://localhost:5173
```

## 🔌 API Endpoints

### 1. **Upload Endpoint**
```
POST /upload
Content-Type: multipart/form-data

Parametreler:
  file: PDF dosyası

Yanıt:
{
  "message": "PDF başarıyla işlendi",
  "pages": 10,
  "chunks": 45,
  "index_path": "./faiss_index"
}
```

### 2. **Ask Endpoint**
```
POST /ask
Content-Type: application/json

Gövde:
{
  "text": "Bu belgede ne anlatılıyor?"
}

Yanıt:
{
  "answer": "Belge şu konuları anlatıyor: ...",
  "sources": [
    {"page": 1, "content": "..."},
    {"page": 3, "content": "..."}
  ]
}
```

### 3. **Root Endpoint**
```
GET /
Yanıt:
{
  "message": "PDF Q&A API çalışıyor! 🚀",
  "endpoints": {...}
}
```

## 🛠️ Kullanılan Teknolojiler

### Backend
| Kütüphane | Amaç |
|-----------|------|
| **FastAPI** | REST API çerçevesi |
| **LangChain** | NLP pipeline düzenlemesi |
| **Groq** | Hızlı LLM çıkarımı (llama-3.3-70b) |
| **FAISS** | Vektör benzerlik araması |
| **sentence-transformers** | Metni vektöre çevirme |
| **PyMuPDF** | PDF okuma |

### Frontend
| Kütüphane | Amaç |
|-----------|------|
| **React 19** | UI çerçevesi |
| **Vite** | Modern bundler |
| **Axios** | HTTP istekleri |
| **Tailwind CSS** | Stil & responsive tasarım |

## 📊 Teknik Detaylar

### Embedding Modeli
- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Boyut**: 384-dimensional vectors
- **Boyut**: ~90MB (ilk indirme sırasında)

### LLM Modeli
- **Sağlayıcı**: Groq
- **Model**: `llama-3.3-70b-versatile`
- **Sıcaklık**: 0 (deterministik yanıtlar)
- **Dil**: Türkçe

### Vektör Veritabanı
- **Sistem**: FAISS (Facebook AI Similarity Search)
- **Depolama**: Yerel (`.faiss` dosyası)
- **Arama**: Top-3 benzer chunk

### Chunk Ayırma
- **Boyut**: 500 karakter
- **Overlap**: 50 karakter (bağlam sürekliliği)
- **Yöntem**: `RecursiveCharacterTextSplitter`

## 💡 Örnek Kullanım

### Python ile Test

```python
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# Embeddings modeli yükle
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# FAISS indeksini yükle
vectorstore = FAISS.load_local(
    "faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)

# Benzer chunk'ları ara
results = vectorstore.similarity_search("Belgede ne var?", k=3)
for doc in results:
    print(f"Sayfa {doc.metadata['page']}: {doc.page_content[:100]}...")
```

### cURL ile API Testi

```bash
# PDF yükle
curl -F "file=@document.pdf" http://localhost:8000/upload

# Soru sor
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"text": "Belge hakkında bilgi ver"}'
```

## ⚙️ Yapılandırma

### .env Dosyası
```bash
# .env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxx
```

### FastAPI CORS Ayarları
Backend, React frontend'in `http://localhost:5173`'den istek atmasına izin verir.

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🐛 Sorun Giderme

| Sorun | Çözüm |
|-------|-------|
| **"GROQ_API_KEY not found"** | `.env` dosyasında API key'i ayarla |
| **"FAISS index not found"** | `day2.py` ile vektör indeksi oluştur |
| **CORS hatası** | Backend'in `Allow-Origin` başlıklarını kontrol et |
| **"Embedding model download failed"** | İnternet bağlantısını ve disk alanını kontrol et |
| **Frontend sunucuya bağlanmıyor** | Backend'in `http://localhost:8000`'de çalışıp çalışmadığını kontrol et |

## 🔐 Güvenlik Notları

- ⚠️ API Key'ini hiçbir zaman kamuya açmayın (`.env` dosyası `.gitignore`'da olmalı)
- 🔒 FAISS indeksi `allow_dangerous_deserialization=True` ile yüklenecekse, kaynağını doğrulayın
- 📝 Üretim ortamında HTTPS kullanın

## 📈 Geliştirme Fırsatları

- [ ] Çoklu PDF desteği (session bazında)
- [ ] Yanıt kaynağını göstermek (kaynak belirtme)
- [ ] Sorgu geçmişi kaydetme
- [ ] Farklı embedding modellerine destek
- [ ] Web arayüzü animasyon & UX iyileştirmeleri
- [ ] Docker containerization
- [ ] Veritabanı entegrasyonu (PostgreSQL + pgvector)
- [ ] Kimlik doğrulama sistemi

## 📄 Dosya Açıklamaları

### **main.py** ⭐
FastAPI sunucusu. PDF yükleme ve Q&A işlemlerini gerçekleştir.
- `/upload`: PDF vektörleştir ve FAISS indeksi oluştur
- `/ask`: Soru sor ve yanıt al

### **day2.py**
İlk çalışmada PDF'i işleyip FAISS indeksi oluştur. 
Türkçe yorumlar içeren eğitim örneği.

### **day3.py**
Groq LLM entegrasyonunun basit örneği.

### **test.py & test_api.py**
API ve sistem bileşenlerinin test edilmesi.

## 👨‍💻 Geliştirici Bilgileri

- **Kurs**: MIUUL Generative AI Program
- **Proje Adı**: LangChain PDF Reader
- **Başlangıç**: Gün 2 - Vektör Veritabanları
- **Ilerleme**: Gün 3 - LLM Entegrasyonu

## 📞 İletişim & Destek

Sorular veya önerileriniz varsa:
1. Issue açın (GitHub)
2. Kodu test edin
3. Pull request gönderin

## 📜 Lisans

Bu proje eğitim amaçlı oluşturulmuştur.

---

**Not**: İlk çalıştırmada embedding model (~90MB) ve LLM yanıtı için biraz zaman alabilir. Bunu görmek normaldir! ⏳

