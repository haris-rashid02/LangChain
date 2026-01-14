from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory

from dotenv import load_dotenv
load_dotenv()

docs = [
    """LangChain is a powerful framework for building applications with language models.
    It provides tools to manage chains, memory, prompts, and vector stores.""",

    """Chroma is a vector database used to store embeddings. 
    It works well with LangChain for semantic search and retrieval-based QA systems.""",

    """Prompt engineering is the process of designing and structuring prompts 
    to get better responses from language models. LangChain simplifies this."""
]

text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
all_chunks = []

for doc in docs:
    all_chunks.extend(text_splitter.split_text(doc))


embeddings = OpenAIEmbeddings()
vectorStore = Chroma.from_texts(all_chunks, embeddings)

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
llm  = ChatOpenAI(model="gpt-3.5-turbo")
qa_chain = RetrievalQA.from_chain_type(llm=llm, memory=memory, retriever = vectorStore.as_retriever())

questions = [
    "What is LangChain?",
    "What is Chroma used for?",
    "How does LangChain help in prompt engineering?",
        "Can you summarize all I asked so far?"

]

for q in questions:
    answer = qa_chain.invoke({"query":q})
    print("Question", q)
    print("Answer:", answer["result"])