from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from dotenv import load_dotenv

load_dotenv()

# Sample text
text = """LangChain is a powerful framework designed for developers to build applications 
that are powered by large language models. It provides tools to manage various components 
such as chains, memory, prompts, and vector stores, making it easier to create complex 
AI workflows. With LangChain, developers can seamlessly integrate natural language 
processing capabilities into their applications, enabling functionalities like question 
answering, summarization, and conversational agents. 

The framework supports multiple types of memory, allowing applications to maintain 
context across interactions. It also provides built-in support for vector databases 
like FAISS and Chroma, which makes semantic search and retrieval-based QA systems 
highly efficient. LangChain encourages modularity, meaning developers can mix and 
match different components such as LLMs, embeddings, and prompts to design custom 
solutions for their specific use cases. 

Furthermore, LangChain simplifies the process of prompt engineering by providing 
templating tools and utilities for chaining multiple prompts together. It is widely 
used in applications ranging from chatbots, document analysis, personal assistants, 
to automated content generation. The framework also emphasizes scalability, ensuring 
that applications built with it can handle large datasets and high volumes of queries 
effectively. By leveraging LangChain, developers can accelerate the development of 
AI-powered applications while maintaining flexibility, robustness, and maintainability."""


# Split text into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
chunks = text_splitter.split_text(text)

# Initialize embeddings
embeddings = OpenAIEmbeddings()

# Create Chroma vectorstore
vectorstore = Chroma.from_texts(chunks, embeddings)

# Create a RetrievalQA chain
llm = ChatOpenAI(model="gpt-3.5-turbo")
qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=vectorstore.as_retriever())

# Ask a question
query = "What is LangChain?"
answer = qa_chain.invoke({"query": query})

print("Question:", query)
print("Answer:", answer["result"])

query2 = "How LangChain simplifies the process of prompt engineering"
answer2 = qa_chain.invoke({"query": query2})

print("Question:", query2)
print("Answer:", answer2["result"])

query3 = "Which built-in support for vector databases it provided?"
answer3 = qa_chain.invoke({"query": query3})

print("Question:", query3)
print("Answer:", answer3["result"])
