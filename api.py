from fastapi import FastAPI
from pydantic import BaseModel

from main import app as agent, get_answer_text

app = FastAPI(title="Basketball Assistant API")


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


class ChatResponse(BaseModel):
    response: str


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    conversation = [(m.role, m.content) for m in request.messages]
    result = agent.invoke({"messages": conversation})
    answer_text = get_answer_text(result["messages"][-1])
    return ChatResponse(response=answer_text)


@app.get("/")
def root():
    return {"status": "ok", "message": "Basketball Assistant API is running. POST to /chat."}