from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-3.5-turbo")

# Set return_messages=True to keep track properly
memory = ConversationBufferMemory(return_messages=True)

conversation = ConversationChain(llm=llm, memory=memory, verbose=True)

print(conversation.invoke({"input": "My favourite color is orange"}))
print(conversation.invoke({"input":"What is my favourite color"}))
