from dotenv import load_dotenv
load_dotenv()

from typing import Annotated, TypedDict

from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from vector import retriever, df

#Tools

@tool
def search_knowledge_base(query: str) -> str:
    """Searches my basketball opinions for information relevant to the query."""
    results = retriever.invoke(query)
    return "\n\n".join(doc.page_content for doc in results)

@tool
def get_player_by_rank(rank: int) -> str:
    """Look up which player David ranked at a specific position, 1 being his favorite."""
    row = df[df["Ranking"] == rank]
    if row.empty:
        return f"No player found at rank {rank}."
    row = row.iloc[0]
    return f"Rank {row['Ranking']}: {row['Player Name']} — {row['Reasoning']}"

web_search = DuckDuckGoSearchRun()

tools = [search_knowledge_base, get_player_by_rank, web_search]


#Model
def get_answer_text(result):
    if isinstance(result.content, list):
        return "".join(part.get("text", "") for part in result.content if isinstance(part, dict))
    return result.content

model = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite").bind_tools(tools)

SYSTEM_PROMPT = SystemMessage(content = ("""
You are an expert in answering questions about David's favorite basketball players.
Use search_knowledge_base for questions about his opinions on a player.
Use get_player_by_rank for any question about the ranking/position of a player.
If a player is not in the knowledge base or the question asks for information outside the csv file, use web_search to find the answer.
Answer in plain text without markdown formatting.
"""
))

#LangGraph

class State(TypedDict):
    messages: Annotated[list, add_messages]

def call_model(state: State):
    response = model.invoke([SYSTEM_PROMPT] + state["messages"])
    return {"messages": [response]}

def should_continue(state: State):
    last_message = state["messages"][-1]
    return "tools" if getattr(last_message, "tool_calls", None) else END

graph = StateGraph(State)
graph.add_node("agent", call_model)
graph.add_node("tools", ToolNode(tools))
graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", should_continue)
graph.add_edge("tools", "agent")

app = graph.compile()

#Chat Loop

if __name__ == "__main__":
    conversation = []
    while True:
        question = input("Ask your question (q to quit): ")
        if question.lower() == "q":
            break

        conversation.append(("user", question))
        result = app.invoke({"messages": conversation})
        conversation = result["messages"]
        print(f"\n{get_answer_text(conversation[-1])}\n")