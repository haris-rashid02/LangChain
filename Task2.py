from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

# Use ChatOpenAI for chat models
llm = ChatOpenAI(model="gpt-3.5-turbo")

# Summary chain
summary_prompt = PromptTemplate.from_template("Summarize this {paragraph}")
summary_chain = summary_prompt | llm

# Hashtag generation chain
title_prompt = PromptTemplate.from_template("Generate 3 hashtags related to {summary}")
title_chain = title_prompt | llm

# Input text
text = "LangChain is a framework for developing applications powered by language models."

# Run chains
summary = summary_chain.invoke({"paragraph": text}).content
title = title_chain.invoke({"summary": summary}).content

print("Summary:", summary)
print("Hashtags:", title)
