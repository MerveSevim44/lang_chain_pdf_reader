from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile")

response = llm.invoke([HumanMessage(content="Merhaba! Sen kimsin?")])

print(response.content)

