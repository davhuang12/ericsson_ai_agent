from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from vector import retriever

def get_answer_text(result):
    if isinstance(result.content, list):
        return "".join(part.get("text", "") for part in result.content if isinstance(part, dict))
    return result.content

model = ChatGoogleGenerativeAI(model="gemini-3.6-flash")

template = """
You are an expert in answering questions about David's favorite basketball players.

Here are his favorite rankings and opinions on different basketball players: {opinions}

Here is the question to answer: {question}

If you find no information 
"""

prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

while True:
    question = input("Ask your question: ")

    opinions = retriever.invoke(question)
    result = chain.invoke({"opinions": opinions, "question": question} )
    print(f"\n{get_answer_text(result)}\n")