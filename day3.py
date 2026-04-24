from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough


#Genelde RAG uygulamalrında promptlar uzun ve karmaşık olmalı 
# çünkü LLM'in yapması gereken görev daha karmaşıktır. Bu nedenle, prompt şablonları genellikle daha ayrıntılı ve yapılandırılmış olur. 
# Bu, LLM'in verilen bağlamı daha iyi anlamasına ve doğru bir şekilde yanıt vermesine yardımcı olur.  
load_dotenv()

# 1. Daha önce kaydettiğimiz FAISS index'i yükle (yeniden embedding hesaplamaz)
print("Index yükleniyor...")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.load_local(
    "faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)
print("  → Hazır")

# 2. LLM'i tanımla
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

# 3. Prompt şablonu
prompt = ChatPromptTemplate.from_template("""
Aşağıdaki bağlamı kullanarak soruyu Türkçe olarak yanıtla.
Eğer cevap bağlamda yoksa "Bu bilgi belgede yer almıyor" de, uydurma.

Bağlam:
{context}

Soru: {question}

Cevap:""")

# 4. Retriever ve RAG zinciri (LCEL ile)
#iligili vektör dökümanlarını getir ve bunları bağlam olarak kullanarak LLM'e soruyu sor    
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# Bağlamı formatla
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

#ne sormak istediğimizi al, ilgili dökümanları getir, bunları formatla ve prompta yerleştir, sonra LLM'e sor    
chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
)

# 5. Soru-cevap döngüsü
print("\nPDF botuna hoş geldin! Çıkmak için 'q' yaz.\n")
while True:
    question = input("Soru: ").strip()
    if question.lower() == "q":
        break
    if not question:
        continue

    # Cevap ve kaynak belgeleri al
    result = chain.invoke(question)
    docs = retriever.invoke(question)

    print(f"\nCevap: {result.content}")
    print("\nKaynak parçalar:")
    for i, doc in enumerate(docs):
        print(f"  [{i+1}] Sayfa {doc.metadata.get('page','?')} → {doc.page_content[:100]}...")
    print()