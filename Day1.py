from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
load_dotenv()

llm = ChatOpenAI(model="gpt-3.5-turbo")
response = llm.invoke("How many planets are there in the solar system?")


print(response.content)