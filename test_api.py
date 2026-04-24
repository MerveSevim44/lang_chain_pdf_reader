import requests
import os

print("=" * 50)
print("API TEST")
print("=" * 50)

# .env kontrolü
print(f"\n.env dosyası var mı? {os.path.exists('.env')}")
if os.path.exists('.env'):
    with open('.env') as f:
        env_content = f.read()
        has_groq = 'GROQ_API_KEY' in env_content
        print(f"GROQ_API_KEY tanımlanmış mı? {has_groq}")

# faiss_index kontrolü
print(f"faiss_index klasörü var mı? {os.path.exists('faiss_index')}")

# Önce backend'in çalışıp çalışmadığını test et
try:
    response = requests.get("http://localhost:8000/")
    print("\n✓ Backend çalışıyor:", response.json())
except Exception as e:
    print("\n✗ Backend çalışmıyor:", e)
    exit(1)

# Şimdi /ask endpoint'ini test et
try:
    response = requests.post(
        "http://localhost:8000/ask",
        json={"text": "test"}
    )
    print(f"✓ /ask endpoint'i yanıt verdi (HTTP {response.status_code}):")
    if response.status_code == 200:
        print(response.json())
    else:
        print("Hata yanıtı:")
        print(response.text)
except Exception as e:
    print("✗ /ask hatası:", e)
    print("Yanıt:", response.text if 'response' in locals() else "Yanıt alınamadı")
