from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.schema import Document
from dotenv import load_dotenv

load_dotenv()

# Sample documents
docs = [
    {"content": """LangChain is a framework for building applications powered by large language models.
    It helps manage chains, memory, prompts, and vector stores for complex AI workflows.""", "source": "LangChain_Doc"},
    
    {"content": """Chroma is an open-source vector database used to store embeddings efficiently.
    It integrates seamlessly with LangChain for semantic search and retrieval-based QA.""", "source": "Chroma_Doc"},
    
    {"content": """Prompt engineering is the technique of crafting effective prompts
    to guide large language models toward accurate and useful responses.""", "source": "Prompt_Eng_Doc"},
]

# Split and label each chunk
text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
texts, metadatas = [], []
for doc in docs:
    for chunk in text_splitter.split_text(doc["content"]):
        texts.append(chunk)
        metadatas.append({"source": doc["source"]})

# Create embeddings and Chroma store
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_texts(texts, embeddings, metadatas=metadatas)

# Create retriever and model
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 2})
llm = ChatOpenAI(model="gpt-3.5-turbo")

# Create the RetrievalQA chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True
)

# Ask a question
query = "What is Chroma and how it helps LangChain?"
result = qa_chain.invoke({"query": query})

print("🔹 Question:", query)
print("🔹 Answer:", result["result"])
print("\n🔹 Sources Used:")
for doc in result["source_documents"]:
    print(f"📄 From: {doc.metadata['source']}")
    print(f"➡️ Content: {doc.page_content.strip()}\n")
