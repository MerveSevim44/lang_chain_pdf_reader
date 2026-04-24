from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# 1. PDF'i oku
print("PDF okunuyor...")
loader = PyMuPDFLoader("pdf-ask-answer/test.pdf")
documents = loader.load()
print(f"  → {len(documents)} sayfa yüklendi")

# 2. Sayfaları küçük parçalara böl (chunk)
# chunk_size: her parça max 500 karakter
# chunk_overlap: parçalar 50 karakter örtüşür (bağlam kaybolmasın)
print("Parçalara bölünüyor...")
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
chunks = splitter.split_documents(documents)
print(f"  → {len(chunks)} parça oluşturuldu")

##### BU BÖLÜMLENMİLŞ PARÇALARI VEKTÖR VERİ TABANINA KAYDEDECEĞİZ ##### 

# 3. Her parçayı vektöre çevir ve FAISS'e kaydet
# İlk çalıştırmada model indirilir (~90MB), sonra önbellekten gelir
print("Vektörler hesaplanıyor... (ilk seferde biraz uzun sürebilir)")
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
#Facebook'un geliştirdiği bu kütüphane vektörleri hızlı aranabilir şekilde bellekte saklar.
#dökümanlardan oluşturulan vektörler burada tutulur ve benzerlik araması yapılır.   

###FAISS bu veriyi bu embedding modeline göre vektörleştirir
vectorstore = FAISS.from_documents(chunks, embeddings)

# 4. Diske kaydet — 3. günde buradan yükleyeceğiz
vectorstore.save_local("faiss_index")
print("  → faiss_index/ klasörüne kaydedildi")

# 5. Test: bir soru sor, en alakalı 2 chunk'ı getir
print("\nTest sorgusu yapılıyor...")
query = "Bu belgede ne anlatılıyor?"
results = vectorstore.similarity_search(query, k=2)

print(f"\nEn alakalı {len(results)} parça:\n")
for i, doc in enumerate(results):
    print(f"--- Parça {i+1} (sayfa {doc.metadata.get('page', '?')}) ---")
    print(doc.page_content[:200])
    print()