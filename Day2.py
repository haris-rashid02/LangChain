from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()


llm = ChatOpenAI(model="gpt-3.5-turbo")

template = "Write an introduction about {name} and their hobby is {hobby}"
prompt = PromptTemplate.from_template(template)

chain = prompt | llm

response = chain.invoke({"name": "John", "hobby": "reading"})
print(response.content)