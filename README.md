# David's Basketball Assistant

The AI Agent I created answers questions about my favorite basketball players of all time. It uses a CSV file to answer those questions and is also connected to DuckDuckGo to answer additional factual questions about players.

## How to run it

1. Clone or download this repository, then move into the project folder.

2. Create and activate a virtual environment:
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
  

3. Install dependencies:
pip install -r requirements.txt
  

4. **ONLY IF THE AI AGENT RUNS OUT OF TOKENS.**
Get a free key from [Google AI Studio](https://aistudio.google.com) — no credit card required.
Paste it into the .env file, replacing --> GOOGLE_API_KEY=your-key-here
   

5. Start the backend (in one terminal, with the venv active):
uvicorn api:app --reload
  

6. Start the frontend (in a **second** terminal, with the venv active):
streamlit run app_ui.py
  
Step 6 opens a chat UI in your browser locally.



## Technologies used

- LLM: Google Gemini (`gemini-3.5-flash-lite`) 
- Agentic framework: LangGraph 
- RAG: ChromaDB (local, embedded vector store) + Gemini embeddings
- Tools: DuckDuckGo search for the web-lookup tool
- Backend:  FastAPI
- Frontend: Streamlit


## Architecture
1.vector.py: Reads the CSV of David's rankings and opinions, turns each row into a searchable chunk of text, and stores it in a small local database (Chroma) that can be searched by meaning, not just exact words.
2.main.py: This is where the logic of the agent lives: the three tools, the LLM, and the LangGraph logic that decides whether a tool is needed for a given question and loops back on itself until it has a real answer.
3.api.py: A small FastAPI server that takes a question from outside, hands it to the brain in main.py, and sends the answer back. It doesn't do any of the thinking itself — it just relays.
4.app_ui.py: A Streamlit chat window where a person types a question and sees the conversation. It talks to the front door (api.py), never directly to the brain.

## Point 3

The agent can answer questions about my opinions about basketball players by reading the CSV file in the project. It can also search the internet to find specific stats or consensus opinions about a player to compare it to mine.

My agent has 3 tools:
search_knowledge_base - looks through my written opinions to find what he said about a player.
get_player_by_rank - looks up the exact player at a given rank (ex: "who's #3," or "who's his favorite" = rank 1).
web_search: searches the web for players who aren't on my list.

RAG component:
The CSV file (containing rank, player, and his reasoning) gets split into small chunks of text and stored in a local vector database. When a question comes in, it's compared against those chunks to find the closest matches, and those get handed to the model as context for its answer.

Where the agent makes decisions:
The Agent has to decide whether it has to use a tool to answer the question or not, and when a tool is required it has to know which of the 3 it calls.
